# Gemini Project Context: Job Search Automation Agent

This project is a Python-based CLI tool designed to automate the job search process by leveraging AI for candidate profiling and intelligent job matching. It uses web scraping to find recent job listings and AI to evaluate their suitability based on a user's resume.

## Project Overview

- **Purpose**: Automate job discovery, filtering, and tracking.
- **Main Technologies**:
  - **Python 3.10+**: Core programming language.
  - **Typer & Rich**: CLI framework and terminal formatting.
  - **pypdf**: PDF parsing for resumes.
  - **Crawl4AI**: Asynchronous web crawling and structured data extraction.
  - **Gemini (via Gemini CLI)**: AI logic for persona extraction and job scoring.
  - **JSON/JSONL**: Data storage for configuration, candidate persona, and job ledger.

## Architecture

- **`main.py`**: Entry point for the CLI, managing commands like `init`, `search`, and `cleanup`.
- **`src/`**:
  - **`ai_module.py`**: Interface for AI tasks using the local `gemini` CLI.
  - **`pdf_parser.py`**: Logic for extracting text from PDF resumes.
  - **`ledger_ops.py`**: Operations for managing the job ledger (`data/ledger.jsonl`) and archiving old entries.
  - **`providers/`**: Pluggable architecture for job board scrapers (e.g., `linkedin.py`).
- **`data/`**:
  - **`config.json`**: General application settings.
  - **`locations.json`**: Target cities and countries for job searches.
  - **`persona.json`**: Structured representation of the candidate's profile.
  - **`ledger.jsonl`**: Record of discovered jobs and their application status.

## Building and Running

### Prerequisites
- Python 3.10+
- Gemini CLI installed and configured.
- Playwright (required by Crawl4AI).

### Key Commands

- **Initialize Persona**:
  ```bash
  python main.py init <path_to_resume.pdf>
  ```
  Parses the resume, generates a candidate persona, and asks for user confirmation.

- **Search for Jobs**:
  ```bash
  python main.py search
  ```
  Scrapes enabled job boards for matches based on the candidate persona and target locations.

- **Cleanup Ledger**:
  ```bash
  python main.py cleanup --retention-days 30
  ```
  Archives unapplied job entries older than the specified retention period.

- **Install Dependencies**:
  ```bash
  pip install -r requirements.txt
  python -m crawl4ai.setup  # (Placeholder for Crawl4AI/Playwright initialization)
  ```

## Development Conventions

- **CLI-First**: All functionality is exposed via the Typer-based CLI.
- **Asynchronous Discovery**: Job searching and crawling are implemented using `asyncio` for efficiency.
- **Data Deduplication**: Jobs are hashed using (Company Name + Job Title) to prevent duplicate entries in the ledger.
- **User Validation**: Critical steps like persona generation require explicit user confirmation.
- **Environment Management**: Use a virtual environment (`venv/`) for dependency isolation.
