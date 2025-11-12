# Contributing to Canonizer Registry

Thank you for contributing to the Canonizer Registry! This guide will help you submit high-quality transforms and schemas.

## Table of Contents

- [Before You Start](#before-you-start)
- [Contribution Workflow](#contribution-workflow)
- [Transform Structure](#transform-structure)
- [Schema Structure](#schema-structure)
- [Metadata Requirements](#metadata-requirements)
- [Testing Requirements](#testing-requirements)
- [PR Guidelines](#pr-guidelines)
- [Review Process](#review-process)

## Before You Start

1. **Check existing transforms** - Search the registry to avoid duplicates
2. **Install Canonizer CLI** - Required for local validation
   ```bash
   pip install canonizer
   ```
3. **Review versioning policy** - See [README.md](README.md#versioning)
4. **Understand security requirements** - No code execution, JSONata only

## Contribution Workflow

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/canonizer-registry
cd canonizer-registry
```

### 2. Create Your Transform

```bash
# Create directory structure
mkdir -p transforms/email/my_transform/1.0.0/tests

# Create transform files
touch transforms/email/my_transform/1.0.0/spec.jsonata
touch transforms/email/my_transform/1.0.0/spec.meta.yaml
touch transforms/email/my_transform/1.0.0/tests/input.json
touch transforms/email/my_transform/1.0.0/tests/expected.json
```

### 3. Implement Your Transform

**spec.jsonata:**
```jsonata
{
  "field1": source.field1,
  "field2": $uppercase(source.field2)
}
```

**spec.meta.yaml:**
```yaml
id: email/my_transform
version: 1.0.0
engine: jsonata
from_schema: iglu:vendor/source_schema/jsonschema/1-0-0
to_schema: iglu:org.canonical/target_schema/jsonschema/1-0-0

tests:
  - input: tests/input.json
    expect: tests/expected.json

checksum:
  jsonata_sha256: "abc123..."  # Run: sha256sum spec.jsonata

provenance:
  author: "Your Name <you@example.com>"
  created_utc: "2025-11-12T12:34:56Z"

status: stable
```

### 4. Add Golden Tests

**tests/input.json:**
```json
{
  "source": {
    "field1": "value1",
    "field2": "value2"
  }
}
```

**tests/expected.json:**
```json
{
  "field1": "value1",
  "field2": "VALUE2"
}
```

### 5. Validate Locally

```bash
# Validate your transform
can registry validate transforms/email/my_transform/1.0.0/

# Expected output:
# ✓ Directory structure valid
# ✓ Metadata valid
# ✓ Checksum matches
# ✓ Golden tests pass (1/1)
```

### 6. Open Pull Request

```bash
# Commit your changes
git add transforms/email/my_transform/
git commit -m "Add email/my_transform 1.0.0"

# Push to your fork
git push origin main

# Open PR on GitHub
```

## Transform Structure

### Required Files

```
transforms/<category>/<transform_name>/<version>/
├── spec.jsonata          # Transform logic (REQUIRED)
├── spec.meta.yaml        # Metadata (REQUIRED)
└── tests/                # Test fixtures (REQUIRED)
    ├── input.json        # Test input (at least 1)
    └── expected.json     # Expected output
```

### Category Guidelines

- **email/** - Email transforms (Gmail, Outlook, Exchange, etc.)
- **crm/** - CRM system transforms (Salesforce, HubSpot, etc.)
- **analytics/** - Analytics platform transforms (GA, Mixpanel, etc.)
- **ecommerce/** - E-commerce platform transforms (Shopify, WooCommerce, etc.)
- **social/** - Social media platform transforms (Twitter, LinkedIn, etc.)

## Schema Structure

### Adding New Schemas

```
schemas/<vendor>/<schema_name>/jsonschema/<version>.json
```

**Example:**
```
schemas/com.google/gmail_email/jsonschema/1-0-0.json
```

**Schema file (JSON Schema Draft 7):**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "field1": {"type": "string"},
    "field2": {"type": "string"}
  },
  "required": ["field1"],
  "additionalProperties": false
}
```

## Metadata Requirements

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Transform identifier (e.g., `email/gmail_to_canonical`) |
| `version` | string | SemVer version (e.g., `1.0.0`) |
| `engine` | string | Transform engine (must be `jsonata`) |
| `from_schema` | string | Input schema URI (Iglu format) |
| `to_schema` | string | Output schema URI (Iglu format) |
| `tests` | array | List of golden test fixtures (at least 1) |
| `checksum.jsonata_sha256` | string | SHA256 hex digest of `spec.jsonata` |
| `provenance.author` | string | Author name and email |
| `provenance.created_utc` | string | ISO 8601 timestamp (UTC) |
| `status` | enum | `draft`, `stable`, or `deprecated` |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `compat.from_schema_range` | string | Compatible input schema range (Iglu range) |

### Generating Checksum

```bash
sha256sum transforms/<category>/<transform_name>/<version>/spec.jsonata
```

Copy the hex digest to `spec.meta.yaml` under `checksum.jsonata_sha256`.

## Testing Requirements

### Golden Tests

Every transform must include at least one golden test:

1. **input.json** - Real-world example input (anonymized/sanitized)
2. **expected.json** - Expected output after transformation

### Test Quality

- Use realistic data (anonymize PII)
- Cover edge cases (empty values, null, arrays, nested objects)
- Test error handling (invalid input should produce predictable output)

### Multiple Tests

Add multiple test cases if needed:

```yaml
tests:
  - input: tests/input1.json
    expect: tests/expected1.json
  - input: tests/input2.json
    expect: tests/expected2.json
```

## PR Guidelines

### PR Title

Use the format: `Add <transform_id> <version>` or `Update <transform_id> <version>`

**Examples:**
- `Add email/gmail_to_canonical 1.0.0`
- `Update email/gmail_to_canonical 1.1.0`

### PR Description

Fill out the pull request template completely:

1. **Transform ID** and **Version**
2. **Schemas** (from/to)
3. **Rationale** - Why is this transform needed?
4. **Sample Input/Output** - Real-world example
5. **Source Schema Link** - Link to vendor API docs
6. **Checklist** - Complete all items

### PR Checklist

- [ ] Golden tests pass locally (`can registry validate`)
- [ ] No PII in test fixtures
- [ ] Checksum verified
- [ ] Metadata complete and accurate
- [ ] Transform uses JSONata only (no code execution)
- [ ] Documentation updated (if needed)

## Review Process

### CI Validation

Your PR will be automatically validated:

1. **Structure** - Directory layout matches spec
2. **Metadata** - YAML parses and validates
3. **Checksum** - SHA256 matches file content
4. **Golden Tests** - All tests pass
5. **Index** - REGISTRY_INDEX.json regenerates successfully

### Human Review

Maintainers will review:

1. **Code Quality** - JSONata is clean and efficient
2. **Test Coverage** - Tests are comprehensive
3. **Documentation** - Metadata is accurate
4. **Security** - No malicious code or data exfiltration

### Approval Timeline

- **Simple transforms**: 1-3 days
- **Complex transforms**: 3-7 days
- **Schema additions**: 1-2 weeks (requires more review)

## Versioning Your Transform

### When to Bump Version

| Change | Version Bump |
|--------|--------------|
| Fix bug in transform logic | PATCH (`1.0.0` → `1.0.1`) |
| Add support for new input schema | MINOR (`1.0.0` → `1.1.0`) |
| Change output schema (breaking) | MAJOR (`1.0.0` → `2.0.0`) |

### Creating New Version

```bash
# Copy existing version
cp -r transforms/email/my_transform/1.0.0 transforms/email/my_transform/1.1.0

# Edit files in 1.1.0/
# Update version in spec.meta.yaml
# Update checksum
# Update tests if needed

# Validate
can registry validate transforms/email/my_transform/1.1.0/
```

## Common Issues

### Checksum Mismatch

```
Error: Checksum mismatch
  Expected: abc123...
  Actual:   def456...
```

**Solution:** Regenerate checksum
```bash
sha256sum spec.jsonata
# Copy output to spec.meta.yaml
```

### Golden Test Failure

```
Error: Golden test failed
  Expected: {...}
  Actual:   {...}
```

**Solution:** Run transform manually to debug
```bash
can transform run \
  --jsonata spec.jsonata \
  --input tests/input.json \
  --output /tmp/debug.json

diff tests/expected.json /tmp/debug.json
```

### Invalid Metadata

```
Error: Metadata validation failed
  - Missing required field: provenance.author
```

**Solution:** Check spec.meta.yaml against requirements

## Questions?

- Open an issue: [GitHub Issues](https://github.com/benthepsychologist/canonizer-registry/issues)
- Check docs: [Canonizer CLI](https://github.com/benthepsychologist/canonizer)

Thank you for contributing!
