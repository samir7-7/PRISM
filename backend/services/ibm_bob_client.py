"""
IBM watsonx.ai client for semantic code analysis.
Integrates with IBM's Granite model for natural language insights.
"""
import httpx
import json
from typing import Dict, Any, Optional
from backend.config import settings


class IBMBobClient:
    """Client for IBM watsonx.ai API."""
    
    def __init__(self):
        self.api_key = settings.ibm_bob_api_key
        self.api_url = settings.ibm_bob_api_url
        self.project_id = settings.ibm_bob_project_id
        self.model_id = settings.ibm_bob_model_id
    
    async def analyze_code_changes(
        self,
        diff_summary: str,
        changed_files: list,
        impacted_components: list
    ) -> str:
        """
        Get semantic analysis of code changes from IBM watsonx.ai.
        
        Args:
            diff_summary: Summary of the code changes
            changed_files: List of changed file paths
            impacted_components: List of impacted component names
            
        Returns:
            Natural language analysis from IBM Bob
        """
        # Construct prompt for the model
        prompt = self._build_analysis_prompt(
            diff_summary, 
            changed_files, 
            impacted_components
        )
        
        try:
            response = await self._call_watsonx_api(prompt)
            return response
        except Exception as e:
            # Graceful degradation: return error message but don't fail
            return f"IBM watsonx.ai analysis unavailable: {str(e)}"
    
    def _build_analysis_prompt(
        self,
        diff_summary: str,
        changed_files: list,
        impacted_components: list
    ) -> str:
        """Build the prompt for IBM watsonx.ai."""
        prompt = f"""You are a senior software engineer reviewing a code change. Analyze the following pull request and provide insights on potential risks and recommendations.

Changed Files:
{', '.join(changed_files[:10])}  # Limit to first 10 files

Impacted Components:
{', '.join(impacted_components[:15])}  # Limit to first 15 components

Change Summary:
{diff_summary}

Please provide:
1. Semantic risks: What could break due to these changes?
2. Hidden dependencies: Are there non-obvious components that might be affected?
3. Testing recommendations: What specific scenarios should be tested?
4. Deployment considerations: Any special considerations for deploying this change?

Keep your response concise and actionable (max 300 words).
"""
        return prompt
    
    async def _call_watsonx_api(self, prompt: str) -> str:
        """
        Call IBM watsonx.ai API with the given prompt.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            Model's response text
        """
        # Construct API endpoint
        endpoint = f"{self.api_url}/ml/v1/text/generation?version=2023-05-29"
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Prepare request body
        body = {
            "model_id": self.model_id,
            "input": prompt,
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": 500,
                "min_new_tokens": 50,
                "temperature": 0.7,
                "top_k": 50,
                "top_p": 1,
                "repetition_penalty": 1.1
            },
            "project_id": self.project_id
        }
        
        # Make API call
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                endpoint,
                headers=headers,
                json=body
            )
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            # Extract generated text
            if "results" in result and len(result["results"]) > 0:
                return result["results"][0]["generated_text"].strip()
            else:
                return "No analysis generated."
    
    async def generate_test_scenarios(
        self,
        changed_files: list,
        impacted_components: list
    ) -> str:
        """
        Generate test scenarios using IBM watsonx.ai.
        
        Args:
            changed_files: List of changed file paths
            impacted_components: List of impacted component names
            
        Returns:
            Test scenarios as text
        """
        prompt = f"""As a QA engineer, generate specific test scenarios for the following code changes:

Changed Files:
{', '.join(changed_files[:10])}

Impacted Components:
{', '.join(impacted_components[:15])}

Generate 3-5 specific test scenarios that should be executed to verify this change. For each scenario, include:
- Test name
- Steps to execute
- Expected outcome
- Priority (HIGH/MEDIUM/LOW)

Format as a numbered list. Be specific and actionable.
"""
        
        try:
            response = await self._call_watsonx_api(prompt)
            return response
        except Exception as e:
            return f"Test scenario generation unavailable: {str(e)}"
    
    def format_insights_for_display(self, raw_insights: str) -> Dict[str, Any]:
        """
        Format raw insights into structured format for display.
        
        Args:
            raw_insights: Raw text from IBM watsonx.ai
            
        Returns:
            Structured insights dictionary
        """
        # Simple parsing - in production, use more sophisticated NLP
        sections = {
            'semantic_risks': '',
            'hidden_dependencies': '',
            'testing_recommendations': '',
            'deployment_considerations': ''
        }
        
        current_section = None
        lines = raw_insights.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            if 'semantic risk' in line_lower or 'risks:' in line_lower:
                current_section = 'semantic_risks'
            elif 'hidden depend' in line_lower or 'dependencies:' in line_lower:
                current_section = 'hidden_dependencies'
            elif 'testing' in line_lower or 'test' in line_lower:
                current_section = 'testing_recommendations'
            elif 'deployment' in line_lower or 'deploy' in line_lower:
                current_section = 'deployment_considerations'
            elif current_section and line.strip():
                sections[current_section] += line + '\n'
        
        return {
            'raw': raw_insights,
            'structured': sections
        }

# Made with Bob
