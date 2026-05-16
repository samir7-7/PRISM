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
        """
        Build a semantic-focused prompt for IBM watsonx.ai.
        
        This prompt is specifically designed to identify semantic risks:
        - Behavioral changes that break downstream assumptions
        - Enum/constant changes that affect dependent services
        - API contract changes that impact consumers
        - State transition changes that violate expectations
        """
        # Format impacted components with context
        impacted_list = '\n'.join([f"  - {comp}" for comp in impacted_components[:20]])
        
        prompt = f"""You are a semantic risk analyzer for code changes. Your goal is to identify BEHAVIORAL risks, not syntax errors.

CONTEXT:
This is a pull request in a microservices architecture where services communicate via events and APIs.

CHANGED FILES:
{', '.join(changed_files[:10])}

DEPENDENCY GRAPH ANALYSIS:
The following components are downstream dependencies that may be affected:
{impacted_list}

CODE CHANGES:
{diff_summary[:1500]}  # Include actual diff content

SEMANTIC RISK ANALYSIS REQUIRED:

1. **Behavioral Contract Violations**
   - Are there enum/constant value changes that downstream services depend on?
   - Are there API response field renames that consumers still reference?
   - Are there state transition changes that violate assumptions?

2. **Hidden Assumption Breaks**
   - Which impacted components make assumptions about the changed code's behavior?
   - Are there timing, ordering, or state assumptions that could break?
   - Are there data format expectations that changed?

3. **Cross-Service Impact**
   - Which downstream services will fail silently vs fail loudly?
   - Are there event consumers that expect specific field names or values?
   - Are there analytics or monitoring systems that depend on specific states?

4. **Regression Scenarios**
   - What specific test cases would catch these semantic breaks?
   - What edge cases arise from the behavioral change?

RESPONSE FORMAT:
Provide a structured analysis focusing on SEMANTIC risks (behavioral breaks), not syntactic issues.
Be specific about which downstream components are at risk and why.
Limit response to 400 words, prioritize highest-risk findings.
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
        
        # Make API call with retry logic
        max_retries = 3
        retry_delay = 1.0  # Start with 1 second
        
        for attempt in range(max_retries):
            try:
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
                        
            except (httpx.TimeoutException, httpx.HTTPStatusError) as e:
                # Check if it's a retryable error
                if isinstance(e, httpx.HTTPStatusError):
                    # Retry on 429 (rate limit), 503 (service unavailable), 502 (bad gateway)
                    if e.response.status_code not in [429, 502, 503]:
                        raise  # Don't retry on other HTTP errors
                
                # Last attempt - raise the error
                if attempt == max_retries - 1:
                    raise
                
                # Wait before retrying (exponential backoff)
                import asyncio
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Double the delay for next attempt
        
        # Fallback if all retries exhausted (should not reach here due to raise above)
        return "Analysis unavailable after retries."
    
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
