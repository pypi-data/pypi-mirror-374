import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import markdown
import re

class CrewAIDocsFetcher:
    """Fetches and processes CrewAI documentation"""
    
    def __init__(self):
        self.base_url = "https://docs.crewai.com"
        self.cache = {}
        self.client = None
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch a single documentation page"""
        if url in self.cache:
            return self.cache[url]
        
        try:
            response = await self.client.get(url, follow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove navigation, headers, footers
            for tag in soup.find_all(['nav', 'header', 'footer', 'aside']):
                tag.decompose()
            
            # Get main content
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
            
            if main_content:
                content = main_content.get_text(separator='\n', strip=True)
            else:
                content = soup.get_text(separator='\n', strip=True)
            
            # Clean up content
            content = re.sub(r'\n\s*\n', '\n\n', content)
            content = content.strip()
            
            self.cache[url] = content
            return content
            
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    async def search_documentation(self, query: str) -> List[Dict[str, str]]:
        """Search across CrewAI documentation"""
        search_urls = [
            f"{self.base_url}/en/concepts/agents",
            f"{self.base_url}/en/concepts/tasks", 
            f"{self.base_url}/en/concepts/crews",
            f"{self.base_url}/en/concepts/flows",
            f"{self.base_url}/en/concepts/llms",  # Added LLMs page
            f"{self.base_url}/en/introduction",
            f"{self.base_url}/en/tools/overview"
        ]
        
        results = []
        query_lower = query.lower()
        
        for url in search_urls:
            content = await self.fetch_page(url)
            if content and query_lower in content.lower():
                # Extract relevant snippet
                lines = content.split('\n')
                relevant_lines = []
                
                for i, line in enumerate(lines):
                    if query_lower in line.lower():
                        start = max(0, i-2)
                        end = min(len(lines), i+3)
                        snippet = '\n'.join(lines[start:end])
                        relevant_lines.append(snippet)
                
                if relevant_lines:
                    results.append({
                        "url": url,
                        "title": self._extract_title(content),
                        "snippet": '\n---\n'.join(relevant_lines[:3])  # Top 3 matches
                    })
        
        return results
    
    def _extract_title(self, content: str) -> str:
        """Extract title from content"""
        lines = content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line and not line.startswith('#'):
                return line[:100]  # First non-header line, truncated
        return "CrewAI Documentation"
    
    async def get_agent_examples(self) -> Dict[str, str]:
        """Get agent configuration examples"""
        content = await self.fetch_page(f"{self.base_url}/en/concepts/agents")
        if not content:
            return {}
        
        examples = {}
        # Look for code blocks with agent examples
        code_pattern = r'```python\n(.*?)\n```'
        matches = re.findall(code_pattern, content, re.DOTALL)
        
        for i, match in enumerate(matches):
            if 'Agent(' in match:
                examples[f"example_{i+1}"] = match.strip()
        
        return examples
    
    async def get_tools_by_category(self) -> Dict[str, List[str]]:
        """Get CrewAI tools organized by category"""
        content = await self.fetch_page(f"{self.base_url}/en/tools/overview")
        if not content:
            return {}
        
        # Parse tools content to extract categories
        categories = {}
        current_category = None
        
        for line in content.split('\n'):
            line = line.strip()
            if line.endswith(':') and not line.startswith('-'):
                current_category = line[:-1]
                categories[current_category] = []
            elif line.startswith('-') and current_category:
                tool_name = line[1:].strip()
                categories[current_category].append(tool_name)
        
        return categories
    
    async def get_concept_content(self, concept: str) -> Optional[str]:
        """Get content for a specific concept (agents, tasks, crews, etc.)"""
        url = f"{self.base_url}/en/concepts/{concept}"
        return await self.fetch_page(url)