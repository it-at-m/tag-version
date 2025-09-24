"""
Command Line Interface for the tag_version package.
"""

import sys
from pathlib import Path
from typing import Optional

import click
import colorama
import tomli
from colorama import Back, Fore, Style

from tag_version.constants import (
    CLI_ANNOTATED_TAG_INFO,
    CLI_ANNOTATED_TAG_PROMPT,
    CLI_AVAILABLE_SERVICES,
    CLI_CHECK_PERMISSIONS,
    CLI_CURRENT_VERSION,
    CLI_ERROR_CREATING_TAG,
    CLI_ERROR_SERVICE_OR_PREFIX,
    CLI_FAILED_TO_CREATE_TAG,
    CLI_FINDING_LATEST_VERSION,
    CLI_FOUND_TAGS,
    CLI_HIGHEST_VERSION_FOUND,
    CLI_HIGHEST_VERSION_TAG,
    CLI_INVALID_SELECTION_NUMBER,
    CLI_INVALID_SERVICE_NAME,
    CLI_INVALID_VERSION_TYPE,
    CLI_LIGHTWEIGHT_TAG_INFO,
    CLI_LOOKING_FOR_PREFIX,
    CLI_NEW_TAG,
    CLI_NEW_VERSION,
    CLI_NO_VALID_VERSION_TAGS,
    CLI_OPERATION_CANCELLED,
    CLI_PUSH_ERROR,
    CLI_PUSH_ERROR_SEPARATOR,
    CLI_PUSH_LATER,
    CLI_PUSH_SUCCESS,
    CLI_PUSHING_TAG,
    CLI_SELECTED_SERVICE,
    CLI_SELECTED_VERSION_TYPE,
    CLI_SERVICE_LINE,
    CLI_SERVICE_LINK,
    CLI_SUMMARY_SEPARATOR,
    CLI_TAG_CREATED_LOCALLY,
    CLI_TAG_LOCALLY_NOT_PUSHED,
    CLI_TAG_MESSAGE_LINE,
    CLI_TAG_MESSAGE_PROMPT,
    CLI_TAG_NOT_PUSHED,
    CLI_USING_PREFIX,
    CLI_VALID_VERSIONS_FOUND,
    CLI_VERSION_INCREMENT_TYPE,
    CLI_VERSION_TAG_ENTRY,
    CLI_VERSION_TYPE_MAJOR,
    CLI_VERSION_TYPE_MINOR,
    CLI_VERSION_TYPE_PATCH,
    CLI_VERSION_UPDATE_SUMMARY,
    CLI_WORKFLOW_TRIGGERED,
)
from tag_version.core import (
    VersionInfo,
    create_git_tag,
    filter_tags_by_prefix,
    get_git_tags,
    get_latest_version,
    increment_version,
    parse_version_tags,
    push_git_tag,
)

# Initialize colorama for cross-platform colored terminal output
colorama.init(autoreset=True)


def load_config() -> dict:
    """
    Load configuration from pyproject.toml file.
    Looks for the file in the current directory and parent directories.
    """
    # Start with current directory and go up to find pyproject.toml
    current_dir = Path.cwd()
    config_path = None

    # Search up to 5 levels up for the pyproject.toml file
    for _ in range(5):
        test_path = current_dir / "pyproject.toml"
        if test_path.exists():
            config_path = test_path
            break
        parent = current_dir.parent
        if parent == current_dir:  # Reached root directory
            break
        current_dir = parent

    if not config_path:
        return {}

    try:
        with open(config_path, "rb") as f:
            config = tomli.load(f)
            return config.get("tool", {}).get("tag_version", {})
    except Exception:
        return {}


# Load configuration
tagger_config = load_config()

# Define default services - use config if available, otherwise use empty list
DEFAULT_SERVICES = tagger_config.get("services", [])
DEFAULT_VERSION_TYPES = ["major", "minor", "patch"]


def print_color(message: str, color: str = Fore.WHITE, end="\n"):
    """Print colored text to the console"""
    click.echo(f"{color}{message}{Style.RESET_ALL}", nl=False)
    if end:
        click.echo(end)


@click.command()
@click.option(
    "--service",
    "-s",
    type=click.STRING,
    help=f"Service to tag (available: {', '.join(DEFAULT_SERVICES) if DEFAULT_SERVICES else 'None configured'})",
)
@click.option(
    "--version-type",
    "-t",
    type=click.Choice(DEFAULT_VERSION_TYPES, case_sensitive=False),
    help="Version increment type (major, minor, patch)",
)
@click.option(
    "--prefix",
    "-p",
    type=click.STRING,
    help="Custom prefix for the tag (overrides the configured format)",
)
@click.option(
    "--message",
    "-m",
    type=click.STRING,
    help="Message for annotated tag (creates lightweight tag if not provided)",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Skip confirmation prompts and automatically proceed",
)
@click.option(
    "--services-list",
    type=click.STRING,
    help="Comma-separated list of available services (overrides defaults)",
)
@click.option("--no-push", is_flag=True, help="Don't push the tag to remote repository")
def main(
    service: Optional[str],
    version_type: Optional[str],
    prefix: Optional[str],
    message: Optional[str],
    yes: bool,
    services_list: Optional[str],
    no_push: bool,
):
    """
    Create and push Git tags for semantic versioning.

    This tool helps manage version tags for different services in a repository.
    It follows the semantic versioning specification (major.minor.patch).
    """
    # Setup available services
    available_services = DEFAULT_SERVICES
    if services_list:
        available_services = [s.strip() for s in services_list.split(",")]

    # Interactive service selection if not provided
    if not service and not prefix:
        print_color(CLI_AVAILABLE_SERVICES, color=Fore.CYAN)
        for idx, svc in enumerate(available_services, 1):
            print_color(f"{idx}. {svc}", color=Fore.GREEN)

        # Simple selection without autocomplete
        service_input = click.prompt("Enter service number or name", type=str)

        # Check if input is a number
        if service_input.isdigit():
            idx = int(service_input)
            if 1 <= idx <= len(available_services):
                service = available_services[idx - 1]
                print_color(CLI_SELECTED_SERVICE.format(service), color=Fore.GREEN)
            else:
                print_color(
                    CLI_INVALID_SELECTION_NUMBER.format(len(available_services)),
                    color=Fore.RED,
                )
                sys.exit(1)
        else:
            # Input is a service name - check if it's valid
            if service_input in available_services:
                service = service_input
                print_color(CLI_SELECTED_SERVICE.format(service), color=Fore.GREEN)
            else:
                print_color(
                    CLI_INVALID_SERVICE_NAME.format(service_input), color=Fore.RED
                )
                sys.exit(1)

    # Define tag prefix
    if not prefix and service:
        # Get the prefix format from config or use default
        prefix_format = tagger_config.get("prefix_format", "{service}-")
        prefix = prefix_format.format(service=service)
        print_color(CLI_USING_PREFIX.format(prefix), color=Fore.CYAN)
    elif not prefix:
        print_color(CLI_ERROR_SERVICE_OR_PREFIX, color=Fore.RED)
        sys.exit(1)

    # Interactive version type selection if not provided
    if not version_type:
        print_color(CLI_VERSION_INCREMENT_TYPE, color=Fore.CYAN)
        print_color(CLI_VERSION_TYPE_MAJOR, color=Fore.GREEN)
        print_color(CLI_VERSION_TYPE_MINOR, color=Fore.GREEN)
        print_color(CLI_VERSION_TYPE_PATCH, color=Fore.GREEN)

        version_input = click.prompt("Enter version type number or name", type=str)

        # Check if input is a number
        if version_input.isdigit():
            idx = int(version_input)
            if 1 <= idx <= len(DEFAULT_VERSION_TYPES):
                version_type = DEFAULT_VERSION_TYPES[idx - 1]
            else:
                print_color(
                    CLI_INVALID_SELECTION_NUMBER.format(len(DEFAULT_VERSION_TYPES)),
                    color=Fore.RED,
                )
                sys.exit(1)
        else:
            # Input is a version type name - check if it's valid
            if version_input.lower() in [v.lower() for v in DEFAULT_VERSION_TYPES]:
                # Find the matching version type with correct casing
                version_type = next(
                    v
                    for v in DEFAULT_VERSION_TYPES
                    if v.lower() == version_input.lower()
                )
            else:
                print_color(
                    CLI_INVALID_VERSION_TYPE.format(version_input), color=Fore.RED
                )
                sys.exit(1)

    print_color(CLI_SELECTED_VERSION_TYPE.format(version_type), color=Fore.GREEN)

    # Get all tags from Git
    print_color(
        CLI_FINDING_LATEST_VERSION.format(
            "service " + service if service else "custom prefix " + prefix
        )
    )
    print_color(CLI_LOOKING_FOR_PREFIX.format(prefix), color=Fore.CYAN)

    all_tags = get_git_tags()
    matching_tags = filter_tags_by_prefix(all_tags, prefix)

    tag_count = len(matching_tags)
    color = Fore.YELLOW if tag_count == 0 else Fore.GREEN
    print_color(
        CLI_FOUND_TAGS.format("no" if tag_count == 0 else tag_count), color=color
    )

    # Process matching tags
    version_objects = parse_version_tags(matching_tags, prefix)
    latest_version_obj = get_latest_version(version_objects)

    if latest_version_obj:
        # Display all found versions for verification
        print_color(CLI_VALID_VERSIONS_FOUND, color=Fore.CYAN)
        sorted_versions = sorted(
            version_objects, key=lambda v: (v.major, v.minor, v.patch), reverse=True
        )

        for v in sorted_versions:
            print_color(
                CLI_VERSION_TAG_ENTRY.format(v.version_string, v.tag), color=Fore.GREEN
            )

        print_color(CLI_HIGHEST_VERSION_FOUND, color=Fore.GREEN, end="")
        print_color(
            f"{latest_version_obj.version_string}",
            color=Fore.WHITE + Back.GREEN,
            end="",
        )
        print_color(
            CLI_HIGHEST_VERSION_TAG.format(latest_version_obj.tag), color=Fore.GREEN
        )

    else:
        print_color(CLI_NO_VALID_VERSION_TAGS, color=Fore.YELLOW + Back.RED)

        latest_version_obj = VersionInfo(
            tag=f"{prefix}0.0.0", version_string="0.0.0", major=0, minor=0, patch=0
        )

    # Increment version according to the selected version type
    new_version, new_tag = increment_version(latest_version_obj, version_type)

    # Handle tag message for annotated tags
    if not message and not yes:
        # Ask if user wants to create an annotated tag with a message
        if click.confirm(CLI_ANNOTATED_TAG_PROMPT, default=False):
            message = click.prompt(
                CLI_TAG_MESSAGE_PROMPT, default="", show_default=False
            )
            if not message.strip():
                message = None

    # Show summary and confirm
    print_color(CLI_VERSION_UPDATE_SUMMARY, color=Fore.CYAN)
    if service:
        print_color(CLI_SERVICE_LINE.format(service), color=Fore.GREEN)
    print_color(
        CLI_CURRENT_VERSION.format(latest_version_obj.version_string), color=Fore.YELLOW
    )
    print_color(CLI_NEW_VERSION.format(new_version), color=Fore.GREEN)
    print_color(CLI_NEW_TAG.format(new_tag), color=Fore.GREEN)
    if message:
        print_color(CLI_TAG_MESSAGE_LINE.format(message), color=Fore.CYAN)
        print_color(CLI_ANNOTATED_TAG_INFO, color=Fore.CYAN)
    else:
        print_color(CLI_LIGHTWEIGHT_TAG_INFO, color=Fore.YELLOW)
    print_color(CLI_SUMMARY_SEPARATOR, color=Fore.CYAN)

    # Confirm action
    if not yes and not click.confirm("Do you want to create this tag?", default=True):
        print_color(CLI_OPERATION_CANCELLED, color=Fore.YELLOW)
        sys.exit(0)

    # Create the tag
    try:
        create_git_tag(new_tag, message)
        print_color(CLI_TAG_CREATED_LOCALLY.format(new_tag), color=Fore.GREEN)
    except RuntimeError as e:
        print_color(CLI_ERROR_CREATING_TAG.format(str(e)), color=Fore.RED)
        print_color(CLI_FAILED_TO_CREATE_TAG, color=Fore.RED)
        sys.exit(1)

    # Ask to push the tag
    push_confirmed = yes or (
        not no_push
        and click.confirm("Do you want to push this tag to origin?", default=True)
    )

    if push_confirmed:
        print_color(CLI_PUSHING_TAG, color=Fore.CYAN)
        success, output = push_git_tag(new_tag)

        if success:
            print_color(CLI_PUSH_SUCCESS.format(new_tag), color=Fore.GREEN)
            print_color(CLI_WORKFLOW_TRIGGERED, color=Fore.CYAN)

            # Show relevant link based on service if available
            service_links = tagger_config.get("service_links", {})
            if service and service in service_links:
                print_color(
                    CLI_SERVICE_LINK.format(service, service_links[service]),
                    color=Fore.CYAN,
                )
        else:
            print_color(CLI_PUSH_ERROR, color=Fore.WHITE + Back.RED)
            print_color(CLI_PUSH_ERROR_SEPARATOR, color=Fore.RED)
            print_color(output, color=Fore.RED)
            print_color(CLI_PUSH_ERROR_SEPARATOR, color=Fore.RED)
            print_color(CLI_TAG_LOCALLY_NOT_PUSHED, color=Fore.YELLOW)
            print_color(CLI_CHECK_PERMISSIONS, color=Fore.YELLOW)
            print_color(CLI_PUSH_LATER.format(new_tag), color=Fore.CYAN)
    else:
        print_color(CLI_TAG_NOT_PUSHED, color=Fore.YELLOW)
        print_color(CLI_PUSH_LATER.format(new_tag), color=Fore.CYAN)


if __name__ == "__main__":
    main()
