"""Selenium script generator module."""
from typing import Dict, List
from bs4 import BeautifulSoup
from openai import OpenAI
import os


class HTMLParser:
    """Parse HTML to extract element information."""
    
    def __init__(self):
        self.soup = None
        self.selectors = {}
    
    def parse_html(self, html_content: str):
        """Parse HTML using BeautifulSoup."""
        self.soup = BeautifulSoup(html_content, 'lxml')
        self.selectors = self.extract_selectors()
    
    def extract_selectors(self) -> Dict[str, List[dict]]:
        """Extract all IDs, names, and CSS selectors."""
        if not self.soup:
            return {}
        
        selectors = {
            'ids': [],
            'names': [],
            'classes': []
        }
        
        for element in self.soup.find_all(True):
            if element.get('id'):
                selectors['ids'].append({
                    'tag': element.name,
                    'id': element.get('id'),
                    'type': element.get('type', '')
                })
            if element.get('name'):
                selectors['names'].append({
                    'tag': element.name,
                    'name': element.get('name'),
                    'type': element.get('type', '')
                })
            if element.get('class'):
                selectors['classes'].append({
                    'tag': element.name,
                    'class': ' '.join(element.get('class'))
                })
        
        return selectors
    
    def find_element_info(self, element_type: str) -> dict:
        """Find selector information for specific element."""
        return self.selectors


class SeleniumScriptGenerator:
    """Generate Selenium scripts."""
    
    def __init__(self, html_parser: HTMLParser, rag_engine, llm_client=None):
        self.html_parser = html_parser
        self.rag_engine = rag_engine
        self.llm_client = llm_client or OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def generate_script(self, test_case: dict, html_content: str) -> str:
        """Generate complete Selenium script."""
        # Parse HTML if provided
        has_html = html_content and len(html_content) > 50
        if has_html:
            self.html_parser.parse_html(html_content)
        
        # Retrieve relevant context for test case
        context = self.rag_engine.retrieve_context(
            f"{test_case['feature']} {test_case['test_scenario']}", 
            top_k=3
        )
        
        # Build prompt
        prompt = self.rag_engine.prompt_builder.build_script_generation_prompt(
            test_case, html_content if has_html else "", context
        )
        
        # Generate script using LLM
        try:
            response = self.llm_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a Selenium automation expert that generates executable Python scripts. If HTML is not provided, generate a generic template with placeholder selectors."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            
            script = response.choices[0].message.content.strip()
            
            # Clean up script if wrapped in markdown
            if script.startswith('```'):
                lines = script.split('\n')
                script = '\n'.join(lines[1:-1]) if len(lines) > 2 else script
                if script.startswith('python'):
                    script = script[6:].strip()
            
            return script
        
        except Exception as e:
            return f"# Error generating script: {e}\n# Please check your OpenAI API key and try again."
    
    def validate_selectors(self, script: str, available_selectors: dict) -> bool:
        """Ensure script uses valid selectors from HTML."""
        # Extract selectors used in script
        import re
        
        # Find all By.ID, By.NAME, By.CSS_SELECTOR patterns
        id_pattern = r'By\.ID,\s*["\']([^"\']+)["\']'
        name_pattern = r'By\.NAME,\s*["\']([^"\']+)["\']'
        
        ids_in_script = set(re.findall(id_pattern, script))
        names_in_script = set(re.findall(name_pattern, script))
        
        available_ids = {sel['id'] for sel in available_selectors.get('ids', [])}
        available_names = {sel['name'] for sel in available_selectors.get('names', [])}
        
        # Check if all selectors in script are available
        invalid_ids = ids_in_script - available_ids
        invalid_names = names_in_script - available_names
        
        return len(invalid_ids) == 0 and len(invalid_names) == 0
