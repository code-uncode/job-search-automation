import json
import os
import subprocess
import re
from typing import Optional, Dict, Any

class LLMInterface:
    """Interface to handle all AI-related tasks via the local 'gemini' CLI."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

    def _log_debug(self, filename: str, content: str):
        return
        
        """Helper to save debug data to the dev-test folder."""
        debug_path = os.path.join("dev-test", filename)
        try:
            with open(debug_path, "w") as f:
                f.write(content)
        except Exception as e:
            # We don't want debug logging to crash the app
            pass

    def _call_gemini_cli(self, prompt: str, debug_id: Optional[str] = None) -> str:
        """Calls the 'gemini' CLI command and returns the output string."""
        if debug_id:
            self._log_debug(f"{debug_id}_prompt.txt", prompt)
            
        try:
            # Use -p flag for non-interactive mode
            result = subprocess.run(
                ["gemini", "-p", prompt],
                capture_output=True,
                text=True,
                check=True
            )
            output = result.stdout
            
            if debug_id:
                self._log_debug(f"{debug_id}_output.txt", output)
                
            return output
        except subprocess.CalledProcessError as e:
            raise Exception(f"Gemini CLI call failed: {e.stderr}")

    def _extract_json(self, text: str) -> Any:
        """Extracts the first JSON object or list found in a string, attempting to fix truncation."""
        # Find JSON block using regex, handling potential markdown markers
        match = re.search(r"```json\s*([\[\{].*?[\]\}])\s*```", text, re.DOTALL)
        if not match:
            # Try to find anything that looks like JSON start
            match = re.search(r"([\[\{].*)", text, re.DOTALL)
            
        if match:
            json_str = match.group(1).strip()
            
            # If it's a markdown block that was truncated, remove the trailing markers
            if json_str.endswith("```"):
                json_str = json_str[:-3].strip()

            # Attempt to fix truncated JSON by closing brackets/braces
            stack = []
            for char in json_str:
                if char in "[{":
                    stack.append(char)
                elif char in "]}":
                    if stack:
                        stack.pop()
            
            # Close remaining brackets/braces in reverse order
            while stack:
                opening = stack.pop()
                if opening == "[":
                    json_str += "]"
                elif opening == "{":
                    json_str += "}"

            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                raise Exception(f"Failed to parse extracted JSON: {json_str}")
        raise Exception(f"No JSON found in Gemini output: {text}")

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
        output = self._call_gemini_cli(prompt, debug_id="persona_extraction")
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
        output = self._call_gemini_cli(prompt, debug_id="job_scoring")
        return self._extract_json(output)

    def extract_structured_data(self, text: str, schema_description: str, debug_id: Optional[str] = None) -> Any:
        """Uses LLM to extract structured data from raw text based on a schema description."""
        prompt = f"""
        Analyze the following text and extract structured data based on this description:
        {schema_description}

        Return ONLY a JSON object or list of objects.

        Text:
        {text}
        """
        output = self._call_gemini_cli(prompt, debug_id=debug_id)
        return self._extract_json(output)
