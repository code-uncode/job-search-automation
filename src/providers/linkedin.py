import asyncio
import json
import os
from typing import List, Dict, Any
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from src.providers.base_provider import JobProvider
from src.ai_module import LLMInterface

class LinkedInProvider(JobProvider):
    """LinkedIn job provider using Crawl4AI with interactive handling and AI fallback."""
    
    async def _log_debug(self, filename: str, content: str):
        """Helper to save debug data to the dev-test folder."""
        debug_path = os.path.join("dev-test", filename)
        try:
            with open(debug_path, "w") as f:
                f.write(content)
        except Exception:
            pass

    async def search_jobs(self, persona: Dict[str, Any], locations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Searches for jobs on LinkedIn and extracts structured data."""
        all_jobs = []
        titles = persona.get("job_titles", ["Software Engineer"])
        cities = locations.get("cities", ["London"])
        
        # Define extraction schema for LinkedIn job cards (Rule-based)
        schema = {
            "name": "LinkedIn Job Listing",
            "baseSelector": ".job-search-card",
            "fields": [
                {"name": "title", "selector": ".base-search-card__title", "type": "text"},
                {"name": "company", "selector": ".base-search-card__subtitle", "type": "text"},
                {"name": "location", "selector": ".job-search-card__location", "type": "text"},
                {"name": "link", "selector": "a.base-card__full-link", "type": "attribute", "attribute": "href"},
                {"name": "date_posted", "selector": "time", "type": "attribute", "attribute": "datetime"}
            ]
        }
        extraction_strategy = JsonCssExtractionStrategy(schema, verbose=True)

        # JS code to close popups and scroll
        js_code = """
        const closeButton = document.querySelector('button[aria-label="Dismiss"], .modal__dismiss, .btn-close');
        if (closeButton) { closeButton.click(); }
        window.scrollTo(0, document.body.scrollHeight / 2);
        """

        for title in titles[:1]:
            for city in cities[:1]:
                url = f"https://www.linkedin.com/jobs/search/?keywords={title.replace(' ', '%20')}&location={city.replace(' ', '%20')}&f_TPR=r172800"
                await self._log_debug("linkedin_search_url.txt", url)
                
                print(f"[cyan]Searching LinkedIn for: {title} in {city}...[/cyan]")
                
                result = await self.crawler.arun(
                    url=url,
                    extraction_strategy=extraction_strategy,
                    js_code=js_code,
                    wait_for=".job-search-card",
                    bypass_cache=True
                )
                
                if result.success and result.markdown:
                    await self._log_debug("linkedin_crawl_output.md", result.markdown)

                extracted_jobs = []
                if result.success and result.extracted_content:
                    try:
                        extracted_jobs = json.loads(result.extracted_content)
                    except Exception:
                        pass

                # Fallback to AI if rule-based failed
                if not extracted_jobs and result.success and result.markdown:
                    print(f"[yellow]Rule-based extraction failed. Falling back to AI parsing...[/yellow]")
                    try:
                        ai = LLMInterface()
                        schema_desc = "A list of job listings with 'title', 'company', 'location', 'link', and 'date_posted'."
                        # Use first 10k chars to avoid token limits
                        extracted_jobs = ai.extract_structured_data(
                            result.markdown[:10000], 
                            schema_desc, 
                            debug_id="linkedin_ai_extraction"
                        )
                    except Exception as e:
                        print(f"[red]AI fallback failed: {e}[/red]")

                if extracted_jobs:
                    for job in extracted_jobs:
                        job["source"] = "LinkedIn"
                        all_jobs.append(job)
                    print(f"[green]Successfully extracted {len(extracted_jobs)} jobs from {city}[/green]")
                    await self._log_debug("linkedin_final_jobs.json", json.dumps(extracted_jobs, indent=2))
                else:
                    print(f"[red]No jobs extracted for {city}[/red]")
        
        return all_jobs
