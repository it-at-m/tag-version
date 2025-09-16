"""
Constants for the tag_version package.
"""

# CLI Messages
CLI_AVAILABLE_SERVICES = "Available services:"
CLI_SELECTED_SERVICE = "Selected service: {}"
CLI_INVALID_SELECTION_NUMBER = (
    "Invalid selection. Please enter a number between 1 and {}"
)
CLI_INVALID_SERVICE_NAME = "Invalid service name: {}"
CLI_USING_PREFIX = "Using prefix: {}"
CLI_ERROR_SERVICE_OR_PREFIX = "Error: Either service or prefix must be specified"
CLI_VERSION_INCREMENT_TYPE = "Version increment type:"
CLI_VERSION_TYPE_MAJOR = "1. major - Breaking changes"
CLI_VERSION_TYPE_MINOR = "2. minor - New features, backwards compatible"
CLI_VERSION_TYPE_PATCH = "3. patch - Bug fixes, backwards compatible"
CLI_INVALID_VERSION_TYPE = "Invalid version type: {}"
CLI_SELECTED_VERSION_TYPE = "Selected version type: {}"
CLI_FINDING_LATEST_VERSION = "Finding latest version for {}"
CLI_LOOKING_FOR_PREFIX = "Looking for tags with prefix: {}"
CLI_FOUND_TAGS = "Found {} matching tags"
CLI_VALID_VERSIONS_FOUND = "Valid versions found:"
CLI_VERSION_TAG_ENTRY = "  {} (from tag: {})"
CLI_HIGHEST_VERSION_FOUND = "✅ Highest version found: "
CLI_HIGHEST_VERSION_TAG = " (from tag: {})"
CLI_NO_VALID_VERSION_TAGS = (
    "⚠️ No valid semantic version tags found. Starting with version 0.0.0"
)
CLI_VERSION_UPDATE_SUMMARY = "========== VERSION UPDATE SUMMARY =========="
CLI_SERVICE_LINE = "Service:        {}"
CLI_CURRENT_VERSION = "Current version: {}"
CLI_NEW_VERSION = "New version:     {}"
CLI_NEW_TAG = "New tag:         {}"
CLI_SUMMARY_SEPARATOR = "======================================="
CLI_TAG_CREATED_LOCALLY = "Tag {} created locally."
CLI_FAILED_TO_CREATE_TAG = "Failed to create tag. Exiting."
CLI_ERROR_CREATING_TAG = "Error creating tag: {}"
CLI_PUSHING_TAG = "Pushing tag to origin..."
CLI_PUSH_SUCCESS = "✅ SUCCESS: Tag {} pushed to origin."
CLI_WORKFLOW_TRIGGERED = "The corresponding workflow should now be triggered."
CLI_SERVICE_LINK = "You can check the new {} version at: {}"
CLI_PUSH_ERROR = "❌ ERROR PUSHING TAG"
CLI_PUSH_ERROR_SEPARATOR = "-------------------------------------"
CLI_TAG_LOCALLY_NOT_PUSHED = (
    "The tag was created locally but could not be pushed to remote repository."
)
CLI_CHECK_PERMISSIONS = (
    "Check your internet connection or repository access permissions."
)
CLI_PUSH_LATER = "To push later, use: git push origin {}"
CLI_TAG_NOT_PUSHED = "Tag was created locally but not pushed."
CLI_OPERATION_CANCELLED = "Operation cancelled."

# Core messages
CORE_GIT_TAG_ERROR = (
    "Error: Failed to retrieve git tags. Make sure this is a git repository."
)
