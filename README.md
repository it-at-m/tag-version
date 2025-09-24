# tag_version

[![Made with love by it@M][made-with-love-shield]][itm-opensource]
<!-- feel free to add more shields, style 'for-the-badge' -> see https://shields.io/badges -->

A Python package for managing Git version tags using semantic versioning per command line.

## Features

- Create semantic version tags (`major.minor.patch`)
- Native git interaction
  - Automatic detection of the latest version
  - Git tag creation and pushing to remote repositories
- Nice to use
  - Interactive service selection and version type input
  - Colorful terminal output for better user experience
- Easy to configure
  - Configurable services and prefix format via pyproject.toml
  - Support for custom tag prefixes

### Built With

- uv

## Set up

### Using pip

```bash
pip install tag_version
```

### Using uv (recommended)

```bash
uv add tag_version
```

### From source

```bash
git clone https://github.com/it-at-m/tag-version.git
cd tag-version
pip install .
```

## Usage

### Interactive Mode

Simply run the command without parameters for interactive prompts:

```bash
tag-version
```

With uv:

```bash
uv run tag-version
```

### Basic Usage

```bash
tag-version --service frontend --version-type patch 
```

When using uv:

```bash
uv run tag-version --service frontend --version-type patch
```

### Command Line Options

```bash
Options:
  -s, --service TEXT             Service to tag (frontend, core, assistant, 
                                 assistant-migrations)
  -t, --version-type [major|minor|patch]
                                 Version increment type (major, minor, patch)
  -p, --prefix TEXT              Custom prefix for the tag (overrides the 
                                 configured prefix_format)
  -y, --yes                      Skip confirmation prompts and automatically 
                                 proceed
  --services-list TEXT           Comma-separated list of available services 
                                 (overrides defaults)
  --no-push                      Don't push the tag to remote repository
  --help                         Show this message and exit
```

## Examples

### Create a patch version for the frontend service

```bash
tag-version -s frontend -t patch
```

### Create a major version with a custom prefix

```bash
tag-version --prefix custom-project- --version-type major
```

### Non-interactive mode with automatic confirmation

```bash
tag-version --service core --version-type minor --yes
```

### Use custom services list

```bash
tag-version --services-list "api,ui,database" --service api --version-type minor
```

## Configuration

`tag-version` can be configured via the `pyproject.toml` file. Add a `[tag_version]` section with the following options:

```toml
[tool.tag_version]
# List of available services
services = ["api", "ui", "backend", "database"]

# Format for tag prefixes - {service} will be replaced with the service name
prefix_format = "myproject-{service}-"

# Links to service resources shown after successful tag push
[tool.tag_version.service_links]
api = "https://github.com/myorg/myproject/pkgs/container/myproject-api"
ui = "https://github.com/myorg/myproject/pkgs/container/myproject-ui" 
backend = "https://github.com/myorg/myproject/pkgs/container/myproject-backend"
database = "https://github.com/myorg/myproject/pkgs/container/myproject-database"
```

## Development

### Setup Development Environment

Using uv (recommended):

```bash
git clone https://github.com/it-at-m/tag-version.git
cd tag-version
uv sync
```

### Running Tests

The project uses pytest for testing. You can run the tests using:

```bash
# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run tests with coverage report
uv run pytest --cov=tag_version

# Run specific test files
uv run pytest tests/test_tagger.py

# Run a specific test function
uv run pytest tests/test_tagger.py::test_filter_tags_by_prefix
```

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please open an issue with the tag "enhancement", fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Open an issue with the tag "enhancement"
2. Fork the Project
3. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
4. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
5. Push to the Branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

More about this in the [CODE_OF_CONDUCT](/CODE_OF_CONDUCT.md) file.

## License

Distributed under the MIT License. See [LICENSE](LICENSE) file for more information.

## Contact

it@M - <opensource@muenchen.de>

<!-- project shields / links -->
[made-with-love-shield]: https://img.shields.io/badge/made%20with%20%E2%9D%A4%20by-it%40M-yellow?style=for-the-badge
[itm-opensource]: https://opensource.muenchen.de/
