#!/usr/bin/env python3
"""
Generate REGISTRY_INDEX.json

Builds a machine-readable index of all transforms and schemas in the registry.
This file is used by the Canonizer CLI for discovery and searching.
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import yaml


class IndexGenerator:
    """Generates REGISTRY_INDEX.json from registry contents"""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.transforms_dir = repo_root / "transforms"
        self.schemas_dir = repo_root / "schemas"

    def generate(self) -> Dict:
        """Generate the complete registry index"""
        print("Generating REGISTRY_INDEX.json...")

        transforms = self._collect_transforms()
        schemas = self._collect_schemas()

        index = {
            "version": "1.0.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "transforms": transforms,
            "schemas": schemas,
        }

        print(f"  Collected {len(transforms)} transform(s)")
        print(f"  Collected {len(schemas)} schema(s)")

        return index

    def _collect_transforms(self) -> List[Dict]:
        """Collect all transforms and group by ID"""
        if not self.transforms_dir.exists():
            return []

        # Collect all transforms
        all_transforms: Dict[str, List[Dict]] = {}

        for category_dir in self.transforms_dir.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith("."):
                continue

            for transform_dir in category_dir.iterdir():
                if not transform_dir.is_dir() or transform_dir.name.startswith("."):
                    continue

                transform_id = f"{category_dir.name}/{transform_dir.name}"

                if transform_id not in all_transforms:
                    all_transforms[transform_id] = []

                for version_dir in transform_dir.iterdir():
                    if not version_dir.is_dir() or version_dir.name.startswith("."):
                        continue

                    version_meta = self._read_transform_meta(version_dir)
                    if version_meta:
                        all_transforms[transform_id].append(version_meta)

        # Convert to list format
        result = []
        for transform_id, versions in sorted(all_transforms.items()):
            # Sort versions (newest first)
            versions.sort(key=lambda v: v["version"], reverse=True)

            result.append({
                "id": transform_id,
                "versions": versions,
            })

        return result

    def _read_transform_meta(self, version_dir: Path) -> Dict | None:
        """Read transform metadata and build version entry"""
        meta_file = version_dir / "spec.meta.yaml"

        if not meta_file.exists():
            return None

        try:
            with open(meta_file, "r") as f:
                meta = yaml.safe_load(f)

            # Extract relative path
            rel_path = version_dir.relative_to(self.repo_root)

            version_entry = {
                "version": meta.get("version"),
                "from_schema": meta.get("from_schema"),
                "to_schema": meta.get("to_schema"),
                "status": meta.get("status", "draft"),
                "path": str(rel_path) + "/",
            }

            # Add optional fields
            if "checksum" in meta:
                version_entry["checksum"] = meta["checksum"]

            if "provenance" in meta:
                version_entry["author"] = meta["provenance"].get("author", "Unknown")
                version_entry["created_utc"] = meta["provenance"].get("created_utc")

            if "compat" in meta and "from_schema_range" in meta["compat"]:
                version_entry["compat"] = {
                    "from_schema_range": meta["compat"]["from_schema_range"]
                }

            return version_entry

        except Exception as e:
            print(f"  Warning: Could not read {meta_file}: {e}")
            return None

    def _collect_schemas(self) -> List[Dict]:
        """Collect all schemas"""
        if not self.schemas_dir.exists():
            return []

        schemas = []

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
                    # Parse Iglu-style version from filename
                    version_str = schema_file.stem  # e.g., "1-0-0"

                    # Build Iglu URI
                    uri = f"iglu:{vendor_dir.name}/{schema_dir.name}/jsonschema/{version_str}"

                    # Get relative path
                    rel_path = schema_file.relative_to(self.repo_root)

                    schemas.append({
                        "uri": uri,
                        "path": str(rel_path),
                    })

        return sorted(schemas, key=lambda s: s["uri"])

    def write_index(self, index: Dict, output_path: Path):
        """Write index to file"""
        with open(output_path, "w") as f:
            json.dump(index, f, indent=2, sort_keys=False)
            f.write("\n")  # Add trailing newline

        print(f"  ✓ Wrote {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate REGISTRY_INDEX.json")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root directory")
    parser.add_argument("--output", type=Path, default=None, help="Output file path (default: REGISTRY_INDEX.json)")

    args = parser.parse_args()

    output_path = args.output or (args.repo_root / "REGISTRY_INDEX.json")

    generator = IndexGenerator(args.repo_root)
    index = generator.generate()
    generator.write_index(index, output_path)

    print("✅ Index generation complete")


if __name__ == "__main__":
    main()
