# Saetron's Unraid Templates

Docker container templates for Unraid's **Community Applications** (CA) app store.

## Available Templates

| Template | Category | Description |
| :--- | :--- | :--- |
| **[Codex](templates/codex/codex.xml)** | `MediaApp:Books` | Web server comic book browser and reader. |
| **[Drop-OSS](templates/drop-oss/drop-oss.xml)** | `MediaApp:Other` | Open-source DRM-free game distribution platform. |
| **[Shimmie2](templates/shimmie2/shimmie2.xml)** | `MediaApp:Photos` | Lightweight, tag-based "Booru" style image gallery engine. |

## Installation

1. Open your Unraid WebGUI.
2. Ensure you have the **Community Applications** plugin installed.
3. Search for the application name (e.g., "Shimmie2") in the **Apps** tab.
4. Click **Install**.

## Template Validation

All XML templates are automatically validated on push and pull requests via GitHub Actions (`.github/workflows/validate-xml.yml`) against Unraid's `version="2"` schema and Community Applications rules.

To validate templates locally:

```bash
# Validate against the XSD schema
xmllint --noout --schema .github/unraid-template-v2.xsd templates/*/*.xml

# Run the Community Applications semantic validator
python3 .github/scripts/validate_templates.py
```

## Support

If you encounter issues with these templates or have suggestions for new ones, please visit my [Official Support Thread](https://forums.unraid.net/topic/197096-support-saetron-docker-templates/) on the Unraid Forums.

Please do not open GitHub Issues for template configuration questions; the forum is the best place for community troubleshooting.
