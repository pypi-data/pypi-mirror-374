# generate-env-sample

A simple CLI tool to generate `.env.sample` files from existing `.env` files. This tool reads your `.env` file, preserves comments and empty lines, and creates a sample file with keys but without values.

## Features

- Preserves comments and empty lines from the original `.env` file.
- Generates a clean `.env.sample` with keys set to empty values.
- Built with Python and Typer.

## Installation


### Prerequisites
- Python 3.11 or higher

### Install from Source
1. Clone the repository:
   ```bash
   git clone https://github.com/heshinth/generate-env-sample.git
   cd generate-env-sample
   ```

2. Install dependencies using `uv` (recommended):
   ```bash
   uv sync
   ```

   Or using pip:
   ```bash
   pip install -e .
   ```

## Usage

Run the tool from the command line:

```bash
generate-env-sample
```

### Options
- `--file-name`: Specify the `.env` file to read from (default: `.env`)
- `--sample-name`: Specify the output `.env.sample` file (default: `.env.sample`)

### Examples

1. Generate `.env.sample` from the default `.env`:
   ```bash
   generate-env-sample
   ```

2. Use a custom `.env` file:
   ```bash
   generate-env-sample --file-name myenv.env --sample-name myenv.sample
   ```

3. Get help:
   ```bash
   generate-env-sample --help
   ```

## Example Input/Output

Given a `.env` file like:
```
# Database configuration
DB_HOST=localhost
DB_PORT=5432

# API keys
API_KEY=your_secret_key
```

The generated `.env.sample` will be:
```
# Database configuration
DB_HOST=
DB_PORT=

# API keys
API_KEY=
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on [GitHub](https://github.com/heshinth/generate-env-sample).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file