import typer

ftb_command = typer.Typer()

@ftb_command.command()
def placeholder():
    """Placeholder command for FTB plugin."""
    typer.echo("FTB plugin is not yet implemented.")

def fetch_mod(slug):
    # Placeholder for FTB mod logic
    pass
