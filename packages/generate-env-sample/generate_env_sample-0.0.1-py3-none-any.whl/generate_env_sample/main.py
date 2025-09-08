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

    env_path = Path(file)
    sample_path = Path(sample)

    if not env_path.exists():
        typer.echo(f"Error: {file} file not found.", err=True)
        raise typer.Exit(code=1)

    if sample_path.exists():
        overwrite = typer.confirm(
            f"File {sample} already exists. Overwrite?", default=True
        )
        if not overwrite:
            typer.echo("Operation cancelled.")
            raise typer.Exit(code=0)

    try:
        with env_path.open("r", encoding="utf-8") as env_file:
            typer.echo(f"Generating {sample} from {file}...")
            sample_lines = []

            for line in env_file:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    sample_lines.append(line)  # Preserve comments and empty lines
                elif "=" in line:
                    key = line.split("=", 1)[0].strip()
                    sample_lines.append(f"{key}=\n")
                else:
                    # Treat non-key lines as comments or skip
                    sample_lines.append(line)

            with sample_path.open("w", encoding="utf-8") as sample_file:
                sample_file.writelines(sample_lines)

            typer.echo(f"{sample} created successfully!")

    except PermissionError:
        typer.echo(
            f"Error: Permission denied for {file} or {sample}.", err=True
        )
        raise typer.Exit(code=1)

    except UnicodeDecodeError:
        typer.echo(
            f"Error: Encoding issue with {file}. Ensure it's UTF-8.", err=True
        )
        raise typer.Exit(code=1)

    except Exception as e:
        typer.echo(f"An unexpected error occurred: {e}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
