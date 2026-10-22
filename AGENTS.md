# AGENTS.md

Instructions and guidelines for AI coding agents working in this repository.

## Mandatory Rule: Always Update `CHANGELOG.md`

- **Every change to this repository MUST include an update to `CHANGELOG.md`.**
- Group entries under a date heading in `### YYYY.MM.DD` format (newest date at the top).
- If an entry for the current date already exists, append bullet points to that date section rather than creating a duplicate heading.

## Repository Structure

```text
├── .github/
│   ├── scripts/
│   │   └── validate_templates.py   # Unraid CA semantic & structural validator
│   ├── workflows/
│   │   └── validate-xml.yml        # GitHub Actions workflow for XML validation
│   └── unraid-template-v2.xsd      # XSD schema for Unraid Container v2 XML
├── templates/
│   └── <app-name>/
│       ├── <app-name>.xml          # Unraid Docker v2 template
│       └── <icon>.png              # Optional local application icon
├── AGENTS.md
├── CHANGELOG.md
├── LICENSE
└── README.md
```

## Unraid Community Applications XML Template Rules

1. **Root Element**: Must be `<Container version="2">`.
2. **Required Child Tags**: Every template must contain non-empty `<Name>`, `<Repository>`, `<Registry>`, `<Network>`, `<Privileged>`, `<Support>`, `<Project>`, `<Overview>`, `<Category>`, `<TemplateURL>`, and `<Icon>` elements.
3. **Support Thread**: `<Support>` should point to `https://forums.unraid.net/topic/197096-support-saetron-docker-templates/`.
4. **TemplateURL**: Must point to the raw GitHub URL of the XML file on `main` (e.g., `https://raw.githubusercontent.com/Saetron/unRAID-CA-templates/refs/heads/main/templates/<app>/<app>.xml`).
5. **`<Config>` Formatting**:
   - **Single-line opening tags**: Never wrap `<Config ...>` attributes across multiple lines; Unraid's Community Applications parser requires `<Config>` elements on a single line.
   - **Required attributes**: Every `<Config>` tag must include `Name`, `Target`, `Default`, `Mode`, `Description`, `Type`, `Display`, `Required`, and `Mask`.
   - **Valid `Type` values**: `Port`, `Path`, `Variable`, `Device`, `Label`.
   - **Valid `Display` values**: `always`, `advanced`, `always-hide`, `advanced-hide`, `hidden`.
6. **Do NOT use Prettier or auto-formatters on XML files** that split `<Config>` attributes onto multiple lines.

## Validation Before Committing

Before committing any template or validator change, always run both checks:

```bash
xmllint --noout --schema .github/unraid-template-v2.xsd templates/*/*.xml
python3 .github/scripts/validate_templates.py
```

Also verify that `README.md` (if a new template was added or removed) and `CHANGELOG.md` (always) have been updated.
