"""
OpenRouter client for semantic code analysis.
Integrates with OpenRouter API using minimax/minimax-m2.5:free model.
"""
import httpx
import json
from typing import Dict, Any, Optional
from backend.config import settings


class OpenRouterClient:
    """Client for OpenRouter API."""

    def __init__(self):
        self.api_key = settings.openrouter_api_key
        self.base_url = settings.openrouter_base_url
        self.model_id = settings.openrouter_model_id

    async def analyze_code_changes(
        self,
        diff_summary: str,
        changed_files: list,
        impacted_components: list
    ) -> str:
        """
        Get semantic analysis of code changes from OpenRouter.

        Args:
            diff_summary: Summary of the code changes
            changed_files: List of changed file paths
            impacted_components: List of impacted component names

        Returns:
            Natural language analysis from the AI model
        """
        prompt = self._build_analysis_prompt(
            diff_summary,
            changed_files,
            impacted_components
        )

        try:
            response = await self._call_openrouter_api(prompt)
            return response
        except Exception as e:
            return f"OpenRouter analysis unavailable: {str(e)}"

    def _build_analysis_prompt(
        self,
        diff_summary: str,
        changed_files: list,
        impacted_components: list
    ) -> str:
        """
        Build a semantic-focused prompt for the AI model.

        This prompt is specifically designed to identify semantic risks:
        - Behavioral changes that break downstream assumptions
        - Enum/constant changes that affect dependent services
        - API contract changes that impact consumers
        - State transition changes that violate expectations
        """
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
{diff_summary[:1500]}

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

    async def _call_openrouter_api(self, prompt: str) -> str:
        """
        Call OpenRouter API with the given prompt.

        Args:
            prompt: The prompt to send to the model

        Returns:
            Model's response text
        """
        endpoint = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/prism-project",
            "X-Title": "PRISM"
        }

        body = {
            "model": self.model_id,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a semantic risk analyzer for code changes in a microservices architecture."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }

        max_retries = 3
        retry_delay = 1.0

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        endpoint,
                        headers=headers,
                        json=body
                    )
                    response.raise_for_status()

                    result = response.json()

                    if "choices" in result and len(result["choices"]) > 0:
                        message = result["choices"][0]["message"]
                        content = message.get("content")
                        if content:
                            return content.strip()
                        reasoning = message.get("reasoning")
                        if reasoning:
                            return reasoning.strip()
                        return "No analysis generated."
                    else:
                        return "No analysis generated."

            except (httpx.TimeoutException, httpx.HTTPStatusError) as e:
                if isinstance(e, httpx.HTTPStatusError):
                    if e.response.status_code not in [429, 502, 503]:
                        raise

                if attempt == max_retries - 1:
                    raise

                import asyncio
                await asyncio.sleep(retry_delay)
                retry_delay *= 2

        return "Analysis unavailable after retries."

    async def generate_test_scenarios(
        self,
        changed_files: list,
        impacted_components: list
    ) -> str:
        """
        Generate test scenarios using OpenRouter.

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
            response = await self._call_openrouter_api(prompt)
            return response
        except Exception as e:
            return f"Test scenario generation unavailable: {str(e)}"

    def format_insights_for_display(self, raw_insights: str) -> Dict[str, Any]:
        """
        Format raw insights into structured format for display.

        Args:
            raw_insights: Raw text from the AI model

        Returns:
            Structured insights dictionary
        """
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
