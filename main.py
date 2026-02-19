import json
import os
import asyncio
import typer
from rich import print
from typing import Optional, Dict, Any
from crawl4ai import AsyncWebCrawler

from src.pdf_parser import extract_text_from_pdf
from src.ai_module import LLMInterface
from src.providers.linkedin import LinkedInProvider

app = typer.Typer(help="Personal Job Search Automation Agent")
ai = LLMInterface()
PERSONA_PATH = "data/persona.json"
LOCATIONS_PATH = "data/locations.json"
CONFIG_PATH = "data/config.json"

def load_persona() -> Optional[Dict[str, Any]]:
    """Loads the persona from the JSON file if it exists."""
    if os.path.exists(PERSONA_PATH):
        try:
            with open(PERSONA_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return None
    return None

def load_locations() -> Dict[str, Any]:
    """Loads target locations from config."""
    if os.path.exists(LOCATIONS_PATH):
        try:
            with open(LOCATIONS_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"cities": ["London"], "countries": ["UK"], "remote": True}

def load_config() -> Dict[str, Any]:
    """Loads general configuration."""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"enabled_providers": ["linkedin"], "min_match_score": 60}

def run_persona_generation(resume_path: str) -> Dict[str, Any]:
    """Handles the extraction and parsing of the persona from a PDF."""
    if not resume_path.endswith(".pdf"):
        print("[red]Error: Only PDF resumes are supported at this time.[/red]")
        raise typer.Exit(code=1)
    
    print(f"[cyan]Reading resume from {resume_path}...[/cyan]")
    try:
        resume_text = extract_text_from_pdf(resume_path)
        print("[green]Resume successfully parsed.[/green]")
        
        print("[cyan]Generating candidate persona...[/cyan]")
        persona = ai.generate_persona(resume_text)
        return persona
    except Exception as e:
        print(f"[red]Error during persona generation: {str(e)}[/red]")
        raise typer.Exit(code=1)

@app.command()
def init(resume_path: str = typer.Argument(..., help="Path to your PDF resume")):
    """
    Initializes the agent by parsing your resume and creating a persona.
    """
    persona = run_persona_generation(resume_path)
    
    print("[yellow]Please review the generated persona:[/yellow]")
    print(json.dumps(persona, indent=4))
    
    confirm = typer.confirm("Does this persona look correct?", default=True)
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(PERSONA_PATH), exist_ok=True)
    
    with open(PERSONA_PATH, "w") as f:
        json.dump(persona, f, indent=4)
    
    if confirm:
        print(f"[green]Persona saved to {PERSONA_PATH}.[/green]")
    else:
        print(f"[yellow]Persona saved to {PERSONA_PATH}. Please edit it manually to correct any errors before running 'search'.[/yellow]")

async def async_search():
    """Async implementation of the search logic."""
    persona = load_persona()
    if not persona:
        print("[red]No persona found. Please run 'python main.py init <resume_path>' first.[/red]")
        return
    
    locations = load_locations()
    config = load_config()
    
    print(f"[cyan]Current Persona: {persona.get('name', 'Unknown')} ({persona.get('experience_level', 'N/A')})[/cyan]")
    
    update = typer.confirm("Would you like to update the persona before searching?", default=False)
    if update:
        resume_path = typer.prompt("Enter path to PDF resume")
        persona = run_persona_generation(resume_path)
        
        print("[yellow]New persona generated:[/yellow]")
        print(json.dumps(persona, indent=4))
        
        if typer.confirm("Save this new persona?", default=True):
            with open(PERSONA_PATH, "w") as f:
                json.dump(persona, f, indent=4)
            print(f"[green]Persona updated at {PERSONA_PATH}.[/green]")
        else:
            print("[yellow]Update cancelled. Using previous persona.[/yellow]")
            persona = load_persona()

    print(f"[green]Searching for jobs matching {persona.get('name')}...[/green]")
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        all_found_jobs = []
        if "linkedin" in config.get("enabled_providers", []):
            linkedin = LinkedInProvider(crawler)
            jobs = await linkedin.search_jobs(persona, locations)
            all_found_jobs.extend(jobs)
        
        if not all_found_jobs:
            print("[yellow]No new jobs found in this run.[/yellow]")
        else:
            print(f"[green]Found {len(all_found_jobs)} potential matches.[/green]")
            # Scoring and ledger logic to follow

@app.command()
def search():
    """
    Scrapes job boards for matching jobs and updates the ledger.
    """
    asyncio.run(async_search())

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
    from src.ledger_ops import archive_old_jobs
    print(f"[cyan]Cleaning up unapplied jobs older than {retention_days} days...[/cyan]")
    archive_old_jobs(retention_days)
    print("[green]Cleanup complete.[/green]")

if __name__ == "__main__":
    app()
