import asyncio
import json
import os
from crawl4ai import AsyncWebCrawler
from src.providers.linkedin import LinkedInProvider

async def main():
    # Load persona
    with open("data/persona.json", "r") as f:
        persona = json.load(f)
    
    # Load locations
    with open("data/locations.json", "r") as f:
        locations = json.load(f)

    print(f"Testing LinkedIn fetch for {persona.get('name')}...")
    
    # We'll limit to 1 title and 1 city for the test to be fast
    test_locations = {
        "cities": [locations["cities"][0]],
        "countries": [locations["countries"][0]]
    }
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        provider = LinkedInProvider(crawler)
        
        # Test the direct crawl for debugging
        url = f"https://www.linkedin.com/jobs/search/?keywords=Software%20Engineer&location=London&f_TPR=r172800"
        result = await crawler.arun(url=url)
        
        if result.success:
            print(f"\n[DEBUG] Raw markdown length: {len(result.markdown)}")
            # Show first 1000 chars to identify selectors
            print(f"\n[DEBUG] Preview of markdown:\n{result.markdown[:1000]}...")
        else:
            print(f"Crawl failed: {result.error_message}")
            
        jobs = await provider.search_jobs(persona, test_locations)
        
        print(f"\nFound {len(jobs)} jobs.")
        for i, job in enumerate(jobs):
            print(f"{i+1}. {job.get('title')} at {job.get('company')} ({job.get('location')})")
            print(f"   Link: {job.get('link')}")
            if i >= 4: # Show first 5
                break

if __name__ == "__main__":
    asyncio.run(main())
