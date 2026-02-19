# Personal Job Search Automation Agent

A Python-based CLI tool to automate the job hunt process, leveraging AI for candidate profiling and intelligent job matching.

## CORE OBJECTIVES
1. **PROFILING**: Parse a PDF resume once to build a "Candidate Persona." Review and edit this persona before searching.
2. **DISCOVERY**: Scrape major job boards for "fresh" jobs (posted within the last 48 hours) matching the persona.
3. **FILTERING**: Use `locations.json` to limit results by city, country, or remote status.
4. **TRACKING**: Maintain a "Job Ledger" (`ledger.jsonl`) to prevent duplicates and track application status.
5. **OUTPUT**: Generate daily CSV/Markdown reports for review.

## CURRENT TECHNICAL STACK
- **Language**: Python 3.10+
- **PDF Parsing**: `pypdf`
- **Scraping**: `Crawl4AI` (for LLM-ready Markdown)
- **AI**: Gemini (Integrated via Gemini CLI or API)
- **Data**: JSONL for the ledger, JSON for config/persona, CSV for exports
- **Hashing**: MD5 (Company Name + Job Title) for deduplication

## LOGIC FLOW
- **Freshness**: Only process jobs posted within the last 48 hours.
- **Match Score**: Initial hardcoded minimum match score of 60%.
- **Retention**: Jobs marked `applied: 1` are kept; unapplied jobs older than 30 days are moved to `data/archive/`.

## INITIAL TARGET LOCATIONS
- EU (London, Dublin, Amsterdam, etc.)
- Singapore
- Canada

## INITIAL JOB BOARDS (To be implemented)
- LinkedIn, Indeed, Glassdoor, Reed.co.uk (UK), Jobs.ie (Ireland), MyCareersFuture (Singapore), Job Bank (Canada).

## UPCOMING FEATURES (Roadmap)
- [ ] **Configurable Platforms**: Allow users to enable/disable specific job boards via config.
- [ ] **Multi-Model Support**: Support for local models (ChatGPT Codex, Ollama) and other providers (OpenAI, Anthropic).
- [ ] **Extended Resume Support**: Add support for DOCX and Markdown formats.
- [ ] **Configurable Match Score**: Allow users to set their own minimum match threshold.
- [ ] **Auto-Cleanup**: Automated execution of the ledger archive/cleanup logic.
- [ ] **Advanced Scheduling**: Built-in cron-like functionality for periodic runs.

## TODO
- [x] Implement PDF resume parsing (`src/pdf_parser.py`).
- [x] Build Candidate Persona extractor (`src/ai_module.py`).
- [x] For the first run, ensure the persona is checked by the user. (Implemented in `main.py init`)
- [x] For subsequent runs, check with the user if the persona needs updating. (Implemented in `main.py search`)
- [ ] Add confidence score on skills for better job matching.
- [ ] Integrate Crawl4AI for discovery (`src/providers/`). (LinkedIn structure started)
- [x] Create hashing/deduplication engine (`src/ledger_ops.py`).
- [ ] Implement 48-hour freshness & 60% match score filters.
- [ ] Add CSV/Markdown report generation.
- [x] Implement "Archive" logic for ledger maintenance.
