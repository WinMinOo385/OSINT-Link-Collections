# OLC - OSINT Link Collector

## Overview

OLC (OSINT Link Collector) is an enterprise-grade command-line interface tool designed for intelligence analysts, security researchers, and information professionals. The application provides systematic management and organization of Open Source Intelligence (OSINT) resources, enhanced with artificial intelligence-powered automatic classification capabilities through Cohere AI integration.

## Key Features

### Intelligent Classification
- Automated website analysis and categorization using Cohere AI's advanced language models
- Structured metadata extraction with minimal manual input
- Consistent classification schema across all entries

### Advanced Metadata Management
The system tracks comprehensive resource information:
- Resource identification (name, description, URL)
- Taxonomic classification (type, subtypes, tags)
- User role mapping and target audience identification
- Economic model classification (free, paid, freemium)
- Technical capabilities (API availability, data types)
- Internationalization support (language detection)
- Quality metrics (rating system with review counts)
- Account and authentication requirements

### Core Functionality
- Full CRUD operations (Create, Read, Update, Delete)
- Advanced search capabilities across multiple metadata fields
- Flexible input methods supporting both domain names and full URLs
- Unix pipe support for seamless integration with existing workflows
- Rich terminal interface with formatted table output

## Prerequisites

- Python 3.7+
- Cohere API key (get one at [cohere.com](https://cohere.com))

## Installation

### System Requirements
Ensure Python 3.7 or higher is installed on your system.

### Repository Setup

Clone or download the repository to your local system:
```bash
git clone <repository-url>
cd olc
```

Or download and extract the source files to your preferred directory.

### Quick Installation (Recommended)

The automated setup script provides a streamlined installation process:

```bash
# Set your Cohere API key
export COHERE_API_KEY='your_api_key_here'

# Execute the setup script
chmod +x setup.sh
./setup.sh
```

#### What the Setup Script Does

1. **Installation**: Moves OLC to `~/.olc` directory
2. **Virtual Environment**: Creates an isolated Python environment at `~/.olc/olcEnv`
3. **Dependencies**: Installs all required packages from `requirements.txt`
4. **Executable Wrapper**: Creates a global `olc` command at `~/.local/bin/olc`
5. **API Configuration**: Embeds your Cohere API key in the wrapper

#### Post-Installation

Ensure `~/.local/bin` is in your PATH:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

For permanent configuration, add to your shell profile:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Verify installation:
```bash
olc --help
```

### Manual Installation

#### Dependency Installation

Install the required Python packages using the requirements file:
```bash
pip install -r requirements.txt
```

For production environments, consider using a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Alternatively, install dependencies manually:
```bash
pip install cohere rich
```

#### API Configuration

Obtain a Cohere API key from [cohere.com](https://cohere.com) and configure it as an environment variable:

```bash
export COHERE_API_KEY='your_api_key_here'
```

For persistent configuration, add the environment variable to your shell profile:
```bash
echo "export COHERE_API_KEY='your_api_key_here'" >> ~/.bashrc
source ~/.bashrc
```

## Usage

After installation via `setup.sh`, use the `olc` command directly. For manual installation, use `./olc.py` or `python3 olc.py`.

### Adding Resources

#### Automated Classification
Provide only the URL for AI-powered automatic metadata extraction:
```bash
olc add -l example.com
```

#### Manual Entry
Specify complete metadata for precise control:
```bash
olc add -l example.com \
  -n "Example Site" \
  -d "Comprehensive example website for demonstration purposes" \
  -t "search-engine" \
  --sub osint research \
  --tags "search,investigation" \
  --roles "analyst,researcher" \
  --lang en \
  --cost free \
  --account true \
  --api false \
  --rating 4.5
```

#### Pipeline Integration
Accept input from stdin for batch processing:
```bash
echo "example.com" | olc add
```

### Listing Resources

Display all stored resources in a formatted table:
```bash
olc ls
```

Output includes:
- Sequential entry identifier
- Resource name
- URL
- Classification type
- Associated tags
- Quality rating

### Searching Resources

Execute full-text search across all metadata fields:
```bash
olc find "search term"
```

Search scope includes:
- Resource name
- URL and domain
- Description text
- Type and subtype classifications
- Tag associations
- User role mappings

### Viewing Detailed Information

Retrieve comprehensive metadata for a specific resource:
```bash
olc view -l example.com
```

Displays:
- Complete description
- All metadata attributes
- Temporal information (collection date and last modification)

### Updating Resources

Modify existing resource metadata:
```bash
olc edit -l example.com \
  -n "Updated Resource Name" \
  -d "Revised description reflecting current functionality" \
  --rating 5.0
```

Supports partial updates—only specified fields are modified.

### Removing Resources

Delete a resource from the collection:
```bash
olc rm -l example.com
```

Alternatively, accept input via stdin:
```bash
echo "example.com" | olc rm
```

## Command Reference

### Input Format Flexibility

All commands accept both domain names (`example.com`) and fully-qualified URLs (`https://example.com`). The system automatically normalizes input to ensure consistency.

### Add Command Options

| Option | Description |
|--------|-------------|
| `-l, --link` | Domain name or URL (required) |
| `-n, --name` | Name of the resource |
| `-d, --desc` | Description |
| `-t, --type` | Main type/category |
| `--sub` | One or more subtypes (space-separated) |
| `--tags` | Comma-separated tags |
| `--roles` | Comma-separated user roles |
| `--lang` | Language code (default: en) |
| `--cost` | Cost model: free, paid, or freemium |
| `--account` | Requires account: true or false |
| `--data_types` | Comma-separated data types |
| `--api` | API available: true or false |
| `--rating` | Rating from 0-5 |
| `--rating_count` | Number of ratings |

### Edit Command Options

Identical to add command parameters. The `-l, --link` option is mandatory to specify the target resource for modification.

## Data Persistence

### Storage Format

Resources are persisted in JSON format at:
```
./links.json
```

**Note**: When using the automated setup script, the data file is stored in the installation directory (`~/.olc/links.json`). The storage path can be customized by modifying the `DATA_FILE` variable in `olc.py`.

### Data Schema

Each resource entry adheres to the following structure:
```json
{
  "link": "https://example.com",
  "name": "Example Site",
  "description": "A great example website",
  "type": "search-engine",
  "subtypes": ["osint", "research"],
  "tags": ["search", "investigation"],
  "roles": ["analyst", "researcher"],
  "language": "en",
  "cost": "free",
  "requires_account": true,
  "data_types": ["web-data"],
  "api_available": false,
  "metrics": {
    "rating": 4.5,
    "rating_count": 0
  },
  "date_collected": "2025-10-04T13:00:00",
  "date_updated": "2025-10-04T13:00:00"
}
```

## Artificial Intelligence Integration

### Automated Metadata Extraction

When a resource is added with minimal input (URL only), the system leverages Cohere AI to perform:
- Website name identification
- Descriptive text generation
- Type and subtype classification
- Relevant tag suggestion
- Target user role determination
- Language detection
- Cost model identification
- Account requirement analysis
- API availability detection
- Data type categorization

### Model Configuration

The system utilizes Cohere's `command-a-03-2025` model with a temperature parameter of 0.3 to ensure consistent and deterministic classification results.

## Quality Assurance

### Test Execution

Execute the comprehensive test suite:
```bash
python test_olc.py
```

Alternatively, use the dedicated test runner:
```bash
python run_tests.py
```

### Test Coverage

The test suite validates:
- URL normalization and domain extraction algorithms
- Data persistence operations (load/save)
- Complete CRUD operation functionality
- AI integration and error handling
- Exception management and recovery
- Environment configuration validation

## Usage Examples

### Building a Resource Collection

Construct a comprehensive OSINT toolkit:
```bash
olc add -l shodan.io
olc add -l censys.io
olc add -l hunter.io
olc ls
```

### Targeted Resource Discovery

Locate specific tools by keyword:
```bash
olc find "search"
olc find "osint"
olc find "api"
```

### Quality Metric Updates

Update resource ratings based on operational experience:
```bash
olc edit -l shodan.io --rating 4.8 --rating_count 1
```

### Batch Processing

Import multiple resources from an external list:
```bash
cat domains.txt | while read domain; do
  echo "$domain" | olc add
done
```

## Troubleshooting

### API Key Configuration Error

**Symptom:**
```
✗ COHERE_API_KEY environment variable not set
```

**Resolution:** Configure the API key as documented in the Installation section.

### Data Corruption

**Symptom:** JSON decode errors or empty result sets.

**Resolution:** The application implements graceful degradation when encountering corrupted data files. Implement regular backup procedures for `links.json` to ensure data integrity.

### Duplicate Entry Prevention

**Symptom:**
```
✗ Entry for example.com already exists
```

**Resolution:** The system enforces unique URL constraints. Use the `edit` command to modify existing resources rather than attempting to create duplicates.

## License

This software is provided as-is for personal, educational, and professional use. Users are responsible for ensuring compliance with applicable terms of service for analyzed websites and API providers.

## Contributing

Contributions are welcome. Please submit issues for bug reports or feature requests. Pull requests should include appropriate test coverage and documentation updates.

## Support and Contact

This tool is designed for intelligence analysts, security researchers, and information professionals requiring systematic organization of OSINT resources. For technical support or feature requests, please use the project's issue tracking system.

## Acknowledgments

Built with:
- [Cohere AI](https://cohere.com) - Natural language processing and classification
- [Rich](https://github.com/Textualize/rich) - Terminal formatting and display
