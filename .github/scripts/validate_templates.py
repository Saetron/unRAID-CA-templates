#!/usr/bin/env python3
"""Validate Unraid Community Applications Docker XML templates (version 2)."""

from pathlib import Path
import re
import sys
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

REQUIRED_TAGS = [
    "Name",
    "Repository",
    "Registry",
    "Network",
    "Privileged",
    "Support",
    "Project",
    "Overview",
    "Category",
    "TemplateURL",
    "Icon",
]

URL_TAGS = ["Registry", "Support", "Project", "Icon"]

VALID_MAIN_CATEGORIES = {
    "Backup",
    "Cloud",
    "Downloaders",
    "Drivers",
    "GameServers",
    "HomeAutomation",
    "MediaApp",
    "MediaServer",
    "Network",
    "Other",
    "Plugins",
    "Productivity",
    "Security",
    "Spotlight",
    "Status",
    "Tools",
}

REQUIRED_CONFIG_ATTRS = [
    "Name",
    "Target",
    "Default",
    "Mode",
    "Description",
    "Type",
    "Display",
    "Required",
    "Mask",
]

VALID_CONFIG_TYPES = {"Port", "Path", "Variable", "Device", "Label"}
VALID_DISPLAY_VALUES = {"always", "advanced", "always-hide", "advanced-hide", "hidden"}
VALID_BOOL_VALUES = {"true", "false"}
VALID_PORT_MODES = {"tcp", "udp", "http", "https", ""}
VALID_PATH_MODES = {"rw", "ro", "rw,slave", "rw,shared", "ro,slave", "ro,shared", ""}


def is_valid_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_file(filepath: Path) -> list[str]:
    errors: list[str] = []
    raw_text = filepath.read_text(encoding="utf-8")

    # Ensure <Config ...> tags are not split across multiple lines, which can break CA parsing
    for match in re.finditer(r"<Config\b[^>]*>", raw_text):
        if "\n" in match.group(0):
            line_num = raw_text[: match.start()].count("\n") + 1
            errors.append(
                f"Line {line_num}: <Config> opening tag must be on a single line for Unraid CA compatibility."
            )

    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except ET.ParseError as exc:
        errors.append(f"Invalid XML syntax: {exc}")
        return errors

    if root.tag != "Container":
        errors.append(f"Root element must be <Container>, found <{root.tag}>.")
        return errors

    if root.attrib.get("version") != "2":
        errors.append(
            f'<Container> must have attribute version="2", found version="{root.attrib.get("version")}".'
        )

    for tag in REQUIRED_TAGS:
        elem = root.find(tag)
        if elem is None or elem.text is None or not elem.text.strip():
            errors.append(f"Missing or empty required tag: <{tag}>.")

    # Validate boolean Privileged
    priv_elem = root.find("Privileged")
    if priv_elem is not None and priv_elem.text:
        if priv_elem.text.strip().lower() not in VALID_BOOL_VALUES:
            errors.append(
                f"<Privileged> must be 'true' or 'false', found '{priv_elem.text.strip()}'."
            )

    # Validate URL tags
    for tag in URL_TAGS:
        elem = root.find(tag)
        if elem is not None and elem.text and elem.text.strip():
            url = elem.text.strip()
            if not is_valid_http_url(url):
                errors.append(f"<{tag}> must be a valid HTTP/HTTPS URL, found '{url}'.")

    # Validate TemplateURL (either valid URL or 'false')
    template_url_elem = root.find("TemplateURL")
    if template_url_elem is not None and template_url_elem.text and template_url_elem.text.strip():
        t_url = template_url_elem.text.strip()
        if t_url.lower() != "false" and not is_valid_http_url(t_url):
            errors.append(
                f"<TemplateURL> must be a valid HTTP/HTTPS URL or 'false', found '{t_url}'."
            )

    # Validate Category format
    cat_elem = root.find("Category")
    if cat_elem is not None and cat_elem.text and cat_elem.text.strip():
        categories = cat_elem.text.strip().rstrip(":").split()
        if not categories:
            errors.append("<Category> must contain at least one valid Unraid CA category.")
        for cat in categories:
            main_cat = cat.split(":")[0]
            if main_cat not in VALID_MAIN_CATEGORIES:
                errors.append(
                    f"Invalid category '{cat}' in <Category>. Main category '{main_cat}' is not a standard Unraid CA category."
                )

    # Validate <Config> elements
    for idx, config in enumerate(root.findall("Config"), start=1):
        cfg_name = config.attrib.get("Name", f"#{idx}")
        missing_attrs = [attr for attr in REQUIRED_CONFIG_ATTRS if attr not in config.attrib]
        if missing_attrs:
            errors.append(
                f"<Config Name=\"{cfg_name}\"> missing required attribute(s): {', '.join(missing_attrs)}."
            )
            continue

        cfg_type = config.attrib["Type"]
        cfg_display = config.attrib["Display"]
        cfg_required = config.attrib["Required"].lower()
        cfg_mask = config.attrib["Mask"].lower()
        cfg_mode = config.attrib["Mode"]
        cfg_target = config.attrib["Target"].strip()

        if cfg_type not in VALID_CONFIG_TYPES:
            errors.append(
                f"<Config Name=\"{cfg_name}\"> has invalid Type='{cfg_type}'. Expected one of {sorted(VALID_CONFIG_TYPES)}."
            )

        if cfg_display not in VALID_DISPLAY_VALUES:
            errors.append(
                f"<Config Name=\"{cfg_name}\"> has invalid Display='{cfg_display}'. Expected one of {sorted(VALID_DISPLAY_VALUES)}."
            )

        if cfg_required not in VALID_BOOL_VALUES:
            errors.append(
                f"<Config Name=\"{cfg_name}\"> has invalid Required='{config.attrib['Required']}'. Expected 'true' or 'false'."
            )

        if cfg_mask not in VALID_BOOL_VALUES:
            errors.append(
                f"<Config Name=\"{cfg_name}\"> has invalid Mask='{config.attrib['Mask']}'. Expected 'true' or 'false'."
            )

        if not cfg_target:
            errors.append(f"<Config Name=\"{cfg_name}\"> must have a non-empty Target attribute.")

        if cfg_type == "Port":
            if cfg_mode not in VALID_PORT_MODES:
                errors.append(
                    f"<Config Name=\"{cfg_name}\"> (Type='Port') has invalid Mode='{cfg_mode}'. Expected one of {sorted(VALID_PORT_MODES)}."
                )
            if cfg_target and not re.match(r"^\d+(-\d+)?$", cfg_target):
                errors.append(
                    f"<Config Name=\"{cfg_name}\"> (Type='Port') Target must be a port number or range, found '{cfg_target}'."
                )
        elif cfg_type == "Path":
            if cfg_mode not in VALID_PATH_MODES:
                errors.append(
                    f"<Config Name=\"{cfg_name}\"> (Type='Path') has invalid Mode='{cfg_mode}'. Expected one of {sorted(VALID_PATH_MODES)}."
                )
            if cfg_target and not cfg_target.startswith("/"):
                errors.append(
                    f"<Config Name=\"{cfg_name}\"> (Type='Path') Target must be an absolute container path starting with '/', found '{cfg_target}'."
                )

    return errors


def main() -> int:
    args = sys.argv[1:]
    if args:
        xml_files = [Path(arg) for arg in args if Path(arg).exists()]
    else:
        templates_dir = Path("templates")
        xml_files = sorted(templates_dir.rglob("*.xml")) if templates_dir.exists() else []

    if not xml_files:
        print("No XML files found to validate.")
        return 0

    has_errors = False
    for xml_file in xml_files:
        errors = validate_file(xml_file)
        if errors:
            has_errors = True
            print(f"❌ {xml_file}:")
            for err in errors:
                print(f"   - {err}")
        else:
            print(f"✅ {xml_file} is valid.")

    return 1 if has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
