import json
import os
import subprocess
import re
from typing import Optional, Dict, Any

class LLMInterface:
    """Interface to handle all AI-related tasks via the local 'gemini' CLI."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

    def _call_gemini_cli(self, prompt: str) -> str:
        """Calls the 'gemini' CLI command and returns the output string."""
        try:
            # Use -p flag for non-interactive mode
            result = subprocess.run(
                ["gemini", "-p", prompt],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise Exception(f"Gemini CLI call failed: {e.stderr}")

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extracts the first JSON object found in a string."""
        # Find JSON block using regex, handling potential markdown markers
        match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
        if not match:
            match = re.search(r"(\{.*?\})", text, re.DOTALL)
            
        if match:
            json_str = match.group(1)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                raise Exception(f"Failed to parse extracted JSON: {json_str}")
        raise Exception(f"No JSON object found in Gemini output: {text}")

    def generate_persona(self, resume_text: str) -> Dict[str, Any]:
        """
        Generates a structured candidate persona from resume text.
        """
        prompt = f"""
        Extract a comprehensive Candidate Persona from the following resume text.
        Return ONLY a JSON object with the following fields:
        - name: Full name
        - summary: Professional summary (1-2 sentences)
        - core_skills: List of top 10 technical skills
        - experience_level: e.g., Junior, Mid, Senior, Lead
        - job_titles: List of target job titles based on experience
        - key_achievements: List of top 3 achievements
        - technical_stack: A more detailed list of tools and languages

        Resume Text:
        {resume_text}
        """
        output = self._call_gemini_cli(prompt)
        return self._extract_json(output)

    def score_job(self, persona: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """
        Calculates a match score (0-100) between a persona and a job description.
        Returns a dict with 'score' and 'reasoning'.
        """
        persona_json = json.dumps(persona)
        prompt = f"""
        Compare the following Candidate Persona with the Job Description.
        Calculate a match score between 0 and 100.
        Return ONLY a JSON object with:
        - score: A number between 0 and 100
        - reasoning: A brief explanation for the score (1-2 sentences)

        Candidate Persona:
        {persona_json}

        Job Description:
        {job_description}
        """
        output = self._call_gemini_cli(prompt)
        return self._extract_json(output)
