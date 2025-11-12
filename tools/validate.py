#!/usr/bin/env python3
"""
Canonizer Registry Validation Script

Validates transforms and schemas in the registry:
- Directory structure
- Metadata format and integrity
- Checksum verification
- Golden test execution
- Schema validation
- Uniqueness constraints
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

import yaml

try:
    from jsonschema import Draft7Validator, ValidationError as JSONSchemaValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    print("Warning: jsonschema not available, schema validation will be skipped")

try:
    import jsonata
    JSONATA_AVAILABLE = True
except ImportError:
    JSONATA_AVAILABLE = False
    print("Warning: jsonata-python not available, golden tests will be skipped")


class ValidationError(Exception):
    """Validation error exception"""
    pass


class RegistryValidator:
    """Validates the canonizer registry structure and content"""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.transforms_dir = repo_root / "transforms"
        self.schemas_dir = repo_root / "schemas"
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_all(self) -> bool:
        """Run all validation checks"""
        print("=" * 80)
        print("CANONIZER REGISTRY VALIDATION")
        print("=" * 80)
        print()

        success = True
        success &= self.check_structure()
        success &= self.check_transforms()
        success &= self.check_schemas()

        print()
        print("=" * 80)
        if success:
            print("✅ ALL VALIDATIONS PASSED")
        else:
            print("❌ VALIDATION FAILED")
            print()
            print(f"Errors: {len(self.errors)}")
            for error in self.errors:
                print(f"  - {error}")
        print("=" * 80)

        return success

    def check_structure(self) -> bool:
        """Validate directory structure"""
        print("Checking directory structure...")

        required_dirs = [
            self.transforms_dir,
            self.schemas_dir,
            self.repo_root / "tools",
            self.repo_root / ".github" / "workflows",
        ]

        for dir_path in required_dirs:
            if not dir_path.exists():
                self.errors.append(f"Missing required directory: {dir_path}")
                return False

        print("  ✓ Directory structure valid")
        return True

    def check_transforms(self) -> bool:
        """Validate all transforms"""
        print("Checking transforms...")

        if not self.transforms_dir.exists():
            self.errors.append(f"Transforms directory not found: {self.transforms_dir}")
            return False

        transform_ids: Set[Tuple[str, str]] = set()
        transform_count = 0
        success = True

        for category_dir in self.transforms_dir.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith("."):
                continue

            for transform_dir in category_dir.iterdir():
                if not transform_dir.is_dir() or transform_dir.name.startswith("."):
                    continue

                for version_dir in transform_dir.iterdir():
                    if not version_dir.is_dir() or version_dir.name.startswith("."):
                        continue

                    transform_id = f"{category_dir.name}/{transform_dir.name}"
                    version = version_dir.name

                    # Check for duplicate (id, version)
                    if (transform_id, version) in transform_ids:
                        self.errors.append(f"Duplicate transform: {transform_id}@{version}")
                        success = False
                        continue

                    transform_ids.add((transform_id, version))

                    # Validate transform
                    if not self._validate_transform(version_dir, transform_id, version):
                        success = False
                    else:
                        transform_count += 1

        print(f"  ✓ Validated {transform_count} transforms")
        return success

    def _validate_transform(self, transform_dir: Path, expected_id: str, expected_version: str) -> bool:
        """Validate a single transform"""
        success = True

        # Check required files
        jsonata_file = transform_dir / "spec.jsonata"
        meta_file = transform_dir / "spec.meta.yaml"
        tests_dir = transform_dir / "tests"

        if not jsonata_file.exists():
            self.errors.append(f"{expected_id}@{expected_version}: Missing spec.jsonata")
            return False

        if not meta_file.exists():
            self.errors.append(f"{expected_id}@{expected_version}: Missing spec.meta.yaml")
            return False

        if not tests_dir.exists() or not tests_dir.is_dir():
            self.errors.append(f"{expected_id}@{expected_version}: Missing tests/ directory")
            return False

        # Validate metadata
        try:
            with open(meta_file, "r") as f:
                meta = yaml.safe_load(f)
        except Exception as e:
            self.errors.append(f"{expected_id}@{expected_version}: Invalid YAML: {e}")
            return False

        # Check required fields
        required_fields = ["id", "version", "engine", "from_schema", "to_schema", "tests", "checksum", "provenance", "status"]
        for field in required_fields:
            if field not in meta:
                self.errors.append(f"{expected_id}@{expected_version}: Missing required field: {field}")
                success = False

        # Validate ID matches directory
        if meta.get("id") != expected_id:
            self.errors.append(f"{expected_id}@{expected_version}: ID mismatch (expected {expected_id}, got {meta.get('id')})")
            success = False

        # Validate version matches directory
        if meta.get("version") != expected_version:
            self.errors.append(f"{expected_id}@{expected_version}: Version mismatch (expected {expected_version}, got {meta.get('version')})")
            success = False

        # Validate engine
        if meta.get("engine") != "jsonata":
            self.errors.append(f"{expected_id}@{expected_version}: Invalid engine (must be 'jsonata')")
            success = False

        # Validate checksum
        if "checksum" in meta and "jsonata_sha256" in meta["checksum"]:
            expected_checksum = meta["checksum"]["jsonata_sha256"]
            actual_checksum = self._compute_sha256(jsonata_file)

            if expected_checksum != actual_checksum:
                self.errors.append(f"{expected_id}@{expected_version}: Checksum mismatch (expected {expected_checksum}, got {actual_checksum})")
                success = False

        # Validate golden tests
        if JSONATA_AVAILABLE and "tests" in meta:
            for test_spec in meta["tests"]:
                input_file = transform_dir / test_spec["input"]
                expected_file = transform_dir / test_spec["expect"]

                if not input_file.exists():
                    self.errors.append(f"{expected_id}@{expected_version}: Test input not found: {test_spec['input']}")
                    success = False
                    continue

                if not expected_file.exists():
                    self.errors.append(f"{expected_id}@{expected_version}: Test expected output not found: {test_spec['expect']}")
                    success = False
                    continue

                if not self._run_golden_test(jsonata_file, input_file, expected_file, expected_id, expected_version):
                    success = False

        return success

    def _compute_sha256(self, file_path: Path) -> str:
        """Compute SHA256 hash of a file"""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            sha256.update(f.read())
        return sha256.hexdigest()

    def _run_golden_test(self, jsonata_file: Path, input_file: Path, expected_file: Path, transform_id: str, version: str) -> bool:
        """Run a golden test"""
        try:
            # Load JSONata expression
            with open(jsonata_file, "r") as f:
                expression_str = f.read()

            # Load input
            with open(input_file, "r") as f:
                input_data = json.load(f)

            # Load expected output
            with open(expected_file, "r") as f:
                expected_output = json.load(f)

            # Execute transform
            expr = jsonata.Jsonata(expression_str)
            actual_output = expr.evaluate(input_data)

            # Compare outputs
            if actual_output != expected_output:
                self.errors.append(f"{transform_id}@{version}: Golden test failed")
                self.errors.append(f"  Input: {input_file}")
                self.errors.append(f"  Expected: {json.dumps(expected_output, indent=2)[:200]}...")
                self.errors.append(f"  Actual: {json.dumps(actual_output, indent=2)[:200]}...")
                return False

            return True

        except Exception as e:
            self.errors.append(f"{transform_id}@{version}: Golden test error: {e}")
            return False

    def check_schemas(self) -> bool:
        """Validate all schemas"""
        print("Checking schemas...")

        if not self.schemas_dir.exists():
            self.warnings.append(f"Schemas directory not found: {self.schemas_dir}")
            print("  ⚠ No schemas to validate")
            return True

        schema_count = 0
        success = True

        for vendor_dir in self.schemas_dir.iterdir():
            if not vendor_dir.is_dir() or vendor_dir.name.startswith("."):
                continue

            for schema_dir in vendor_dir.iterdir():
                if not schema_dir.is_dir() or schema_dir.name.startswith("."):
                    continue

                jsonschema_dir = schema_dir / "jsonschema"
                if not jsonschema_dir.exists():
                    continue

                for schema_file in jsonschema_dir.glob("*.json"):
                    if not self._validate_schema(schema_file):
                        success = False
                    else:
                        schema_count += 1

        print(f"  ✓ Validated {schema_count} schemas")
        return success

    def _validate_schema(self, schema_file: Path) -> bool:
        """Validate a JSON Schema file"""
        try:
            with open(schema_file, "r") as f:
                schema = json.load(f)

            # Basic check: must be an object with $schema field
            if not isinstance(schema, dict):
                self.errors.append(f"{schema_file}: Schema must be a JSON object")
                return False

            if "$schema" not in schema:
                self.warnings.append(f"{schema_file}: Missing $schema field (recommended)")

            # Validate with jsonschema if available
            if JSONSCHEMA_AVAILABLE:
                Draft7Validator.check_schema(schema)

            return True

        except JSONSchemaValidationError as e:
            self.errors.append(f"{schema_file}: Invalid JSON Schema: {e}")
            return False
        except Exception as e:
            self.errors.append(f"{schema_file}: Error validating schema: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Validate Canonizer Registry")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root directory")
    parser.add_argument("--check-structure", action="store_true", help="Only check directory structure")
    parser.add_argument("--check-transforms", action="store_true", help="Only check transforms")
    parser.add_argument("--check-schemas", action="store_true", help="Only check schemas")

    args = parser.parse_args()

    validator = RegistryValidator(args.repo_root)

    if args.check_structure:
        success = validator.check_structure()
    elif args.check_transforms:
        success = validator.check_transforms()
    elif args.check_schemas:
        success = validator.check_schemas()
    else:
        success = validator.validate_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
