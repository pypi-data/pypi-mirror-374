import typer
from pathlib import Path
from typing_extensions import Annotated


app = typer.Typer(
    add_completion=False,
    help="A CLI tool to generate .env.sample files from .env files.",
    invoke_without_command=True,
)


@app.command()
def main(
    file: Annotated[str, typer.Option(help="The .env file to read from")] = ".env",
    sample: Annotated[
        str, typer.Option(help="The .env.sample file to create")
    ] = ".env.sample",
) -> None:
    """
    Generate a .env.sample file from the existing .env file.
    """
    # Convert file paths to Path objects for better handling
    env_path = Path(file)
    sample_path = Path(sample)

    # Check if the source .env file exists
    if not env_path.exists():
        typer.echo(f"Error: {file} file not found.", err=True)
        raise typer.Exit(code=1)

    # Check if the sample file already exists and prompt for overwrite
    if sample_path.exists():
        overwrite = typer.confirm(
            f"File {sample} already exists. Overwrite?", default=True
        )
        if not overwrite:
            typer.echo("Operation cancelled.")
            raise typer.Exit(code=0)

    try:
        # Open the .env file and prepare to generate the sample
        with env_path.open("r", encoding="utf-8") as env_file:
            typer.echo(f"Generating {sample} from {file}...")
            sample_lines = []

            # Process each line in the .env file
            for line in env_file:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    # Preserve comments and empty lines
                    sample_lines.append(line)
                elif "=" in line:
                    # Extract the key and create a sample line with empty value
                    if stripped.startswith("export "):
                        key_part = stripped[7:].split("=", 1)[0].strip()
                    else:
                        key_part = line.split("=", 1)[0].strip()
                    sample_lines.append(f"{key_part}=\n")
                else:
                    # Preserve other lines as-is
                    sample_lines.append(line)

            # Write the sample lines to the output file
            with sample_path.open("w", encoding="utf-8") as sample_file:
                sample_file.writelines(sample_lines)

            typer.echo(f"{sample} created successfully!")

    # Handle specific exceptions
    except PermissionError:
        typer.echo(f"Error: Permission denied for {file} or {sample}.", err=True)
        raise typer.Exit(code=1)

    except UnicodeDecodeError:
        typer.echo(f"Error: Encoding issue with {file}. Ensure it's UTF-8.", err=True)
        raise typer.Exit(code=1)

    except Exception as e:
        typer.echo(f"An unexpected error occurred: {e}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
