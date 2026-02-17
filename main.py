import json
import os
import typer
from rich import print
from typing import Optional

from src.pdf_parser import extract_text_from_pdf
from src.ai_module import LLMInterface

app = typer.Typer(help="Personal Job Search Automation Agent")
ai = LLMInterface()

@app.command()
def init(resume_path: str = typer.Argument(..., help="Path to your PDF resume")):
    """
    Initializes the agent by parsing your resume and creating a persona.
    """
    if not resume_path.endswith(".pdf"):
        print("[red]Error: Only PDF resumes are supported at this time.[/red]")
        raise typer.Exit(code=1)
    
    print(f"[cyan]Reading resume from {resume_path}...[/cyan]")
    try:
        resume_text = extract_text_from_pdf(resume_path)
        print("[green]Resume successfully parsed.[/green]")
        
        print("[cyan]Generating candidate persona...[/cyan]")
        persona = ai.generate_persona(resume_text)
        
        persona_path = "data/persona.json"
        with open(persona_path, "w") as f:
            json.dump(persona, f, indent=4)
        
        print(f"[green]Persona saved to {persona_path}.[/green]")
        print("[yellow]Please review and edit the persona before running a search.[/yellow]")
        print(json.dumps(persona, indent=4))
        
    except Exception as e:
        print(f"[red]Error during initialization: {str(e)}[/red]")
        raise typer.Exit(code=1)

@app.command()
def search():
    """
    Scrapes job boards for matching jobs and updates the ledger.
    """
    # Logic for search and scraping (TBD)
    print("[yellow]Search functionality is currently being implemented.[/yellow]")

@app.command()
def report(format: str = "markdown"):
    """
    Generates a daily report of new job matches.
    """
    # Logic for report generation (TBD)
    print("[yellow]Report functionality is currently being implemented.[/yellow]")

@app.command()
def cleanup(retention_days: int = 30):
    """
    Archives old job entries in the ledger.
    """
    # Logic for ledger cleanup (TBD)
    print("[yellow]Cleanup functionality is currently being implemented.[/yellow]")

if __name__ == "__main__":
    app()
