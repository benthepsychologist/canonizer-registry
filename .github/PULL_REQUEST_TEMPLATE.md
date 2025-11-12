## Transform Contribution

**Transform ID:** <!-- e.g., email/gmail_to_canonical -->

**Version:** <!-- e.g., 1.0.0 -->

**From Schema:** <!-- e.g., iglu:com.google/gmail_email/jsonschema/1-0-0 -->

**To Schema:** <!-- e.g., iglu:org.canonical/email/jsonschema/1-0-0 -->

### Rationale

<!-- Why is this transform needed? What use case does it solve? -->

### Sample Input/Output

<details>
<summary>Example transformation (click to expand)</summary>

**Input:**
```json
{
  "example": "input data here"
}
```

**Output:**
```json
{
  "example": "transformed data here"
}
```

</details>

### Source Schema Documentation

<!-- Link to official vendor API docs or schema definition -->
- Vendor docs:
- Schema source:

### Testing

<!-- Describe how you tested this transform -->

- [ ] Tested with real-world data
- [ ] Validated edge cases
- [ ] All golden tests pass locally

### Checklist

Before submitting, ensure:

- [ ] Golden tests pass locally (`can registry validate transforms/<path>`)
- [ ] No PII (Personally Identifiable Information) in test fixtures
- [ ] Checksum verified (matches `spec.meta.yaml`)
- [ ] Metadata complete and accurate
- [ ] Transform uses JSONata only (no code execution)
- [ ] `spec.meta.yaml` includes provenance (author, created_utc)
- [ ] Status field set appropriately (`draft`, `stable`, or `deprecated`)
- [ ] README or CONTRIBUTING updated (if introducing new patterns)
- [ ] Follows versioning policy (SemVer for transforms, Iglu for schemas)

### Additional Context

<!-- Any other information that would help reviewers -->
