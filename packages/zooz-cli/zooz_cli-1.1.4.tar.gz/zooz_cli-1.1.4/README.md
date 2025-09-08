# Zooz CLI

A command-line interface tool for transferring Microsoft Power Pages sites between environments.

## Features

- Interactive environment selection from `pac auth list`
- Interactive site selection from `pac pages list`
- Automatic site ID detection from current environment
- Cross-platform compatibility (Mac/Windows/Linux)
- Simple and intuitive CLI interface
- Available as both Python and npm packages

## Prerequisites

- Microsoft Power Platform CLI (`pac`) installed and configured
- Either Python 3.7+ or Node.js 14+

### Installing Microsoft Power Platform CLI

**Windows:**
```bash
# Via winget
winget install Microsoft.PowerPlatformCLI

# Or via npm
npm install -g @microsoft/powerplatform-cli
```

**Mac/Linux:**
```bash
npm install -g @microsoft/powerplatform-cli
```

Or download from: https://aka.ms/PowerAppsCLI

## Installation

You can install Zooz CLI either via npm (recommended) or Python pip.

### Option 1: Install from npm (Recommended)

```bash
# Install globally
npm install -g zooz-cli-npm

# Or using yarn
yarn global add zooz-cli-npm
```

### Option 2: Install from Python PyPI

Install the latest version directly from PyPI:

```bash
pip install zooz-cli
```

Or with pip3:

```bash
pip3 install zooz-cli
```

### Install from source

1. Clone or download the project
2. Navigate to the project directory
3. Install the CLI tool:

```bash
pip install .
```

Or for development:

```bash
pip install -e .
```

## Usage

### Transfer Site Between Environments

Simply run the command and follow the interactive prompts:

```bash
zooz transfer-site
```

### Command Options

- `--download-path`: Path where to download the site (default: `./`)
- `--upload-path`: Path from where to upload the site (default: auto-detected from downloaded folder)

### Examples

```bash
# Basic usage with interactive prompts
zooz transfer-site

# With custom download path
zooz transfer-site --download-path ./downloads

# With both custom paths
zooz transfer-site --download-path ./downloads --upload-path ./uploads
```

## How it works

1. **Source Environment Selection**: Displays available environments from `pac auth list` and prompts for interactive selection
2. **Add New Environments**: Option to add new environments by entering "0" and providing environment URL
3. **Site Selection**: Shows available sites from `pac pages list` in the selected environment and prompts for interactive selection
4. **Download**: Downloads the selected site using `pac pages download`
5. **Auto-Detection**: Automatically finds the downloaded folder for upload
6. **Target Environment Selection**: Prompts for target environment selection
7. **Upload**: Uploads the site from the downloaded folder to the selected target environment using `pac pages upload`
8. **Cleanup**: Automatically deletes the downloaded folder after successful transfer

## Requirements

The tool expects:
- The `pac` CLI to be installed and authenticated with your environments
- Proper permissions to download from source and upload to target environments
- Access to Power Pages sites in both source and target environments

## Project Structure

```
zooz-cli/
├── bin/
│   └── zooz              # Executable wrapper
├── src/
│   └── cli.py           # Main CLI implementation
├── setup.py             # Installation script
└── README.md            # This file
```

## Development

To contribute to this project:

1. Clone the repository
2. Install in development mode: `pip install -e .`
3. Make your changes
4. Test with: `zooz transfer-site /path/to/test/project`

## License

MIT License

## Support

For issues and questions, please contact the development team.
