"""
MO Plugin Template Generator

- Generates a capture plugin template for Multimodal Observer.
- Reads all template files from the installed package directory (templates/<type>/).
- Copies and renders files to the target structure, replacing {plugin_id}, {publisher_id}, and ClassName.
"""

import sys
import re
import argparse
import logging
import os
import shutil
from pathlib import Path
import importlib.resources as resources
from mop.utils.logger import setup_logger, Colors
from mop.utils.path import pretty_path
import questionary

logger = setup_logger()

# Template folder names (add new plugin types here)
PLUGIN_TYPES = {
    "capture": "capture",
}
DEFAULT_PLUGIN_TYPE = "capture"

# Files in the template that require variable replacement
VARIABLE_FILES = {
    "metadata.json",
    "README.md",
    "src/main.py",
    "src/properties.py",
    "locales/en/namespace.json"
}


def safe_ask(question):
    answer = question.ask()
    if answer is None:
        print(f"{Colors.RED.value}Aborted by user (Ctrl+C){Colors.RESET.value}")
        sys.exit(130)
    return answer


def prompt_choice(prompt_text, options, default=None):
    return safe_ask(questionary.select(
        prompt_text,
        choices=options,
        default=options[default] if default is not None else default
    ))


def validate_id(identifier: str) -> bool | str:
    """
    Validates a MO ID for plugin/publisher.
    """
    pattern = re.compile(r"^[a-z0-9][a-z0-9_-]*[a-z0-9]$")
    if len(identifier) < 2:
        return "ID must be at least 2 characters."
    if not pattern.match(identifier):
        return (
            "ID must be lowercase, can contain letters, numbers, hyphens, and underscores, "
            "must not contain spaces or special characters, "
            "must start and end with a letter or number."
        )
    return True


def prompt_input(prompt_text, placeholder=""):
    return safe_ask(questionary.text(
        prompt_text,
        default=placeholder,
        validate=validate_id
    ))


def copy_and_render(
    src: Path,
    dst: Path,
    replacements: dict,
    replace_vars: bool = False
):
    # Always skip .pyc files
    if dst.suffix == ".pyc":
        logger.debug(f"Skipping bytecode file: {dst}")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    if replace_vars:
        content = src.read_text(encoding="utf-8")
        if dst.name == "main.py":
            content = content.replace(
                "class ClassName(", f"class {replacements['ClassName']}(")
        for key, val in replacements.items():
            content = content.replace("{" + key + "}", val)
        dst.write_text(content, encoding="utf-8")
        logger.debug(f"Rendered file with replacements: {dst}")
    else:
        shutil.copyfile(src, dst)
        logger.debug(f"Copied file: {dst}")


def to_camel_case(s):
    return ''.join(word.capitalize() for word in s.replace('-', '_').split('_'))


def render_template(
    plugin_type: str,
    plugin_id: str,
    publisher_id: str,
    create_venv: bool,
    create_locales: bool,
    debug: bool = False,
    package: str = "mop.templates"
):
    if debug:
        logger.setLevel(logging.DEBUG)
    logger.info(
        f"Generating template for type: {plugin_type} | id: {plugin_id} | publisher: {publisher_id}")
    base_template = f"{package}"

    class_name = to_camel_case(plugin_id)
    replacements = {
        "plugin_id": plugin_id,
        "publisher_id": publisher_id,
        "ClassName": class_name
    }
    dest_root = Path(os.getcwd()) / plugin_id

    def list_files(subpackage) -> list[Path]:
        base = resources.files(subpackage)

        def walk(trav):
            files = []
            for entry in trav.iterdir():
                if entry.is_dir():
                    files.extend(walk(entry))
                else:
                    files.append(entry)
            return files
        return walk(base)

    files_to_copy = list_files(base_template)
    template_base = resources.files(
        base_template).joinpath(PLUGIN_TYPES[plugin_type])
    template_base_str = str(template_base)
    logger.debug(f"Template base: {template_base_str}")
    for src_file in files_to_copy:
        if src_file.is_dir():
            continue
        # Skip .pyc files in template
        if src_file.name.endswith(".pyc"):
            logger.debug(f"Skipping .pyc file in template: {src_file}")
            continue

        rel_path = src_file.relative_to(template_base_str)
        parts = rel_path.parts

        if parts and parts[0] == "src":
            dst = dest_root / "src" / plugin_id / rel_path.name
        elif parts and parts[0] == "icons":
            dst = dest_root / "icons" / rel_path.name
        elif parts and parts[0] == "locales" and create_locales:
            if len(parts) == 3 and parts[1] == "en" and rel_path.name == "namespace.json":
                dst = dest_root / "locales" / "en" / f"{plugin_id}.json"
            else:
                logger.debug(
                    f"Skipping locale not matching en/namespace.json: {src_file}")
                continue
        elif parts and parts[0] == "locales" and not create_locales:
            logger.debug(
                f"Skipping locales because create_locales is False: {src_file}")
            continue
        elif rel_path.name in {"metadata.json", "README.md", ".gitignore", "requirements.txt"}:
            dst = dest_root / rel_path.name
        else:
            dst = dest_root / rel_path

        rel_path_str_norm = str(rel_path).replace("\\", "/")
        replace_vars = rel_path_str_norm in VARIABLE_FILES or rel_path.name in VARIABLE_FILES
        copy_and_render(src_file, dst, replacements, replace_vars=replace_vars)
        logger.debug(f"Created {dst}")

    if create_venv:
        import venv
        venv_path = dest_root / "venv"
        logger.info("Creating virtual environment...")
        venv.EnvBuilder(with_pip=True).create(venv_path)
        logger.info(f"Virtual environment created at: {venv_path}")
    logger.info(
        f"Plugin template {Colors.GREEN.value}created successfully{Colors.RESET.value} at {pretty_path(dest_root)}")
    logger.info(
        f"See {pretty_path(dest_root / 'README.md')} for {Colors.CYAN.value}usage and next steps.{Colors.RESET.value}")


def main():
    parser = argparse.ArgumentParser(
        description="MO Plugin Template Generator"
    )
    parser.add_argument(
        "-t", "--type", type=str, help="Plugin type (capture, ...)")
    parser.add_argument("--publisher-id", type=str,
                        help="Publisher ID (e.g., mylab)")
    parser.add_argument("--plugin-id", type=str,
                        help="Plugin ID (e.g., myplugin)")
    parser.add_argument("--venv", action="store_true",
                        help="Create a virtual environment in the plugin folder")
    parser.add_argument("--locales", action="store_true",
                        help="Add English locale files")
    parser.add_argument("--no-locales", action="store_true",
                        help="Do not add English locale files")
    parser.add_argument("--debug", "-d", action="store_true",
                        help="Enable debug logging")
    args = parser.parse_args()

    # 1. Ask for plugin type
    available_types = list(PLUGIN_TYPES.keys())
    plugin_type = args.type or prompt_choice(
        "Select plugin type:", available_types)

    # 2. Ask for required fields
    publisher_id = args.publisher_id or prompt_input(
        "Publisher ID", "your-publisher-id")
    plugin_id = args.plugin_id or prompt_input("Plugin ID", "your-plugin-id")
    create_venv = args.venv or safe_ask(
        questionary.confirm("Create virtual environment?", default=False)
    )

    # 3. Locales: explicit flags win, else prompt (default yes)
    if args.locales:
        create_locales = True
    elif args.no_locales:
        create_locales = False
    else:
        create_locales = safe_ask(questionary.confirm(
            "Add English locale files?", default=True))

    render_template(
        plugin_type=plugin_type,
        plugin_id=plugin_id,
        publisher_id=publisher_id,
        create_venv=create_venv,
        create_locales=create_locales,
        debug=args.debug
    )


if __name__ == "__main__":
    main()
