# Canonizer Registry

**Git-based transform and schema registry for Canonizer**

This repository contains versioned transforms (JSONata) and schemas (JSON Schema) for the Canonizer data transformation tool. All contributions go through CI validation and pull request review.

## Quick Start

### Using the Registry

```bash
# List available transforms
can registry list

# Search for transforms by schema
can registry search --from iglu:com.google/gmail_email/jsonschema/1-0-0

# Download a transform
can registry pull email/gmail_to_canonical@1.0.0

# Use the transform
can transform run \
  --meta ~/.canonizer/registry/transforms/email/gmail_to_canonical/1.0.0/spec.meta.yaml \
  --input gmail_message.json \
  --output canonical_email.json
```

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

**Quick contribution workflow:**

1. Fork this repository
2. Create your transform in the proper structure:
   ```
   transforms/<category>/<transform_name>/<version>/
   ├── spec.jsonata          # Transform logic
   ├── spec.meta.yaml        # Metadata
   └── tests/
       ├── input.json        # Test input
       └── expected.json     # Expected output
   ```
3. Validate locally: `can registry validate transforms/<category>/<transform_name>/<version>/`
4. Open a pull request
5. CI will validate your contribution
6. Maintainers will review and merge

## Repository Structure

```
canonizer-registry/
├── LICENSE                       # Apache-2.0
├── README.md                     # This file
├── CONTRIBUTING.md               # Contribution guidelines
├── REGISTRY_INDEX.json           # Machine-readable index (CI-generated)
│
├── transforms/                   # Transform registry
│   └── <category>/              # e.g., email, crm, analytics
│       └── <transform_name>/    # e.g., gmail_to_canonical
│           └── <version>/       # e.g., 1.0.0 (SemVer)
│               ├── spec.jsonata
│               ├── spec.meta.yaml
│               └── tests/
│                   ├── input.json
│                   └── expected.json
│
├── schemas/                      # Schema registry
│   └── <vendor>/                # e.g., org.canonical, com.google
│       └── <schema_name>/       # e.g., email, gmail_email
│           └── jsonschema/
│               └── <version>.json  # e.g., 1-0-0.json (Iglu SchemaVer)
│
├── .github/
│   ├── workflows/
│   │   └── validate.yml         # CI validation
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── CODEOWNERS
│
└── tools/
    ├── validate.py              # Validation script
    └── generate_index.py        # Index generation
```

## Transform Metadata

Each transform requires a `spec.meta.yaml` file:

```yaml
# Transform identity
id: email/gmail_to_canonical
version: 1.0.0
engine: jsonata

# Schema contracts
from_schema: iglu:com.google/gmail_email/jsonschema/1-0-0
to_schema: iglu:org.canonical/email/jsonschema/1-0-0

# Golden tests (required)
tests:
  - input: tests/input.json
    expect: tests/expected.json

# Integrity
checksum:
  jsonata_sha256: "<hex>"

# Provenance
provenance:
  author: "Your Name <you@example.com>"
  created_utc: "2025-11-12T12:34:56Z"

# Lifecycle
status: stable   # draft | stable | deprecated
```

## CI Validation

All pull requests are automatically validated by GitHub Actions:

1. **Structure validation** - Directory layout, required files
2. **Metadata validation** - YAML parsing, checksum verification
3. **Transform validation** - Golden tests must pass
4. **Schema validation** - JSON Schema syntax
5. **Index generation** - `REGISTRY_INDEX.json` is rebuilt

## Versioning

### Transforms (SemVer)

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| Breaking change (different output schema) | MAJOR | `1.0.0` → `2.0.0` |
| New feature (support new input schema) | MINOR | `1.0.0` → `1.1.0` |
| Bug fix (same I/O, better logic) | PATCH | `1.0.0` → `1.0.1` |

### Schemas (Iglu SchemaVer: MODEL-REVISION-ADDITION)

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| Breaking change (remove field, change type) | MODEL | `1-0-0` → `2-0-0` |
| Non-breaking change (modify description) | REVISION | `1-0-0` → `1-1-0` |
| Additive change (new optional field) | ADDITION | `1-0-0` → `1-0-1` |

## Security

- No code execution in transforms (JSONata only)
- All contributions reviewed by maintainers
- Checksum verification prevents tampering
- Sandboxed CI execution

## License

Apache-2.0 - See [LICENSE](LICENSE)

Contributors retain copyright but license contributions under Apache-2.0.

## Support

- Issues: [GitHub Issues](https://github.com/benthepsychologist/canonizer-registry/issues)
- Canonizer CLI: [Canonizer Repository](https://github.com/benthepsychologist/canonizer)
- Documentation: [Canonizer Docs](https://github.com/benthepsychologist/canonizer/blob/main/README.md)
