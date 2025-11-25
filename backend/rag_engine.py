"""RAG engine module for retrieval and test case generation."""
from typing import List, Dict
import numpy as np
from openai import OpenAI
import os


class PromptBuilder:
    """Build prompts for LLM."""
    
    def build_test_generation_prompt(self, query: str, context: List[dict]) -> str:
        """Construct prompt for test case generation."""
        context_text = "\n\n".join([
            f"Document: {chunk['metadata']['filename']}\n{chunk['content']}"
            for chunk in context
        ])
        
        prompt = f"""You are a QA testing expert. Based on the following documentation, generate test cases for the user's query.

DOCUMENTATION:
{context_text}

USER QUERY: {query}

Generate test cases in the following JSON format:
[
  {{
    "test_id": "TC-001",
    "feature": "Feature name",
    "test_scenario": "Detailed test scenario",
    "expected_result": "Expected outcome",
    "grounded_in": ["filename1.md", "filename2.txt"]
  }}
]

Requirements:
- Generate 3-5 relevant test cases
- Each test case must reference source documents in "grounded_in"
- Only use information from the provided documentation
- Be specific and actionable
- Include both positive and negative test scenarios where applicable

Return ONLY the JSON array, no additional text."""
        
        return prompt
    
    def build_script_generation_prompt(self, test_case: dict, html: str, context: List[dict]) -> str:
        """Construct prompt for Selenium script generation."""
        context_text = "\n\n".join([chunk['content'] for chunk in context])
        
        prompt = f"""You are a Selenium automation expert. Generate a Python Selenium script for the following test case.

TEST CASE:
- ID: {test_case.get('test_id', 'N/A')}
- Feature: {test_case.get('feature', 'N/A')}
- Scenario: {test_case.get('test_scenario', 'N/A')}
- Expected Result: {test_case.get('expected_result', 'N/A')}

HTML STRUCTURE:
{html[:2000]}  

ADDITIONAL CONTEXT:
{context_text}

Generate a complete, executable Python Selenium script that:
1. Uses correct element selectors from the HTML (prefer By.ID, then By.NAME, then By.CSS_SELECTOR)
2. Includes all necessary imports
3. Sets up the WebDriver
4. Implements the test scenario
5. Includes assertions for the expected result
6. Has proper error handling
7. Closes the driver at the end

Return ONLY the Python code, no markdown formatting or explanations."""
        
        return prompt


class RAGEngine:
    """Retrieval-Augmented Generation engine."""
    
    def __init__(self, vector_db, embedder, llm_client=None):
        self.vector_db = vector_db
        self.embedder = embedder
        self.llm_client = llm_client or OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.prompt_builder = PromptBuilder()
    
    def retrieve_context(self, query: str, top_k: int = 5) -> List[dict]:
        """Retrieve top-k relevant chunks for query."""
        # Generate query embedding
        query_embedding = self.embedder.model.encode([query], convert_to_numpy=True)[0]
        
        # Search vector database
        results = self.vector_db.search(query_embedding, top_k)
        
        return results
    
    def generate_test_cases(self, query: str, context: List[dict] = None) -> List[dict]:
        """Generate test cases grounded in retrieved context."""
        # Retrieve context if not provided
        if context is None:
            context = self.retrieve_context(query)
        
        print(f"DEBUG: Retrieved {len(context)} context chunks for query: {query}")
        if context:
            for i, chunk in enumerate(context[:3]):  # Show first 3
                print(f"DEBUG: Chunk {i+1}: {chunk['metadata'].get('filename', 'unknown')} - {chunk['content'][:100]}...")
        
        if not context:
            print("DEBUG: No context found, returning empty list")
            return []
        
        # Build prompt
        prompt = self.prompt_builder.build_test_generation_prompt(query, context)
        
        # Call LLM
        try:
            response = self.llm_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a QA testing expert that generates structured test cases."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            # Parse response
            import json
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            
            test_cases = json.loads(content)
            
            # Format test cases
            formatted_cases = []
            for tc in test_cases:
                formatted_cases.append(self.format_test_case(tc))
            
            return formatted_cases
        
        except Exception as e:
            print(f"Error generating test cases: {e}")
            return []
    
    def format_test_case(self, test_data: dict) -> dict:
        """Format test case with required fields."""
        return {
            'test_id': test_data.get('test_id', 'TC-000'),
            'feature': test_data.get('feature', ''),
            'test_scenario': test_data.get('test_scenario', ''),
            'expected_result': test_data.get('expected_result', ''),
            'grounded_in': test_data.get('grounded_in', [])
        }
