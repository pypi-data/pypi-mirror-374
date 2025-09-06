import asyncio
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
from .docs_fetcher import CrewAIDocsFetcher

# Create FastMCP server
mcp = FastMCP("crewai-mcp-server")

# Global fetcher instance
docs_fetcher: Optional[CrewAIDocsFetcher] = None

@mcp.resource("crewai://concepts/{concept}")
async def get_concept_resource(concept: str) -> str:
    """Get CrewAI concept documentation (agents, tasks, crews, flows, llms)"""
    global docs_fetcher
    
    if not docs_fetcher:
        docs_fetcher = CrewAIDocsFetcher()
        await docs_fetcher.__aenter__()
    
    content = await docs_fetcher.get_concept_content(concept)
    return content or f"Could not fetch content for {concept}"

@mcp.resource("crewai://tools/all")
async def get_tools_resource() -> str:
    """Get all CrewAI tools"""
    global docs_fetcher
    
    if not docs_fetcher:
        docs_fetcher = CrewAIDocsFetcher()
        await docs_fetcher.__aenter__()
    
    tools = await docs_fetcher.get_tools_by_category()
    content = "# CrewAI Tools\n\n"
    for category, tool_list in tools.items():
        content += f"## {category}\n"
        for tool in tool_list:
            content += f"- {tool}\n"
        content += "\n"
    return content

@mcp.resource("crewai://examples/templates")
async def get_templates_resource() -> str:
    """Get CrewAI code templates"""
    global docs_fetcher
    
    if not docs_fetcher:
        docs_fetcher = CrewAIDocsFetcher()
        await docs_fetcher.__aenter__()
    
    examples = await docs_fetcher.get_agent_examples()
    content = "# CrewAI Agent Templates\n\n"
    for name, code in examples.items():
        content += f"## {name.replace('_', ' ').title()}\n\n```python\n{code}\n```\n\n"
    return content

@mcp.tool()
async def search_crewai_docs(query: str) -> str:
    """Search across CrewAI documentation for specific topics, concepts, or examples"""
    global docs_fetcher
    
    if not docs_fetcher:
        docs_fetcher = CrewAIDocsFetcher()
        await docs_fetcher.__aenter__()
    
    results = await docs_fetcher.search_documentation(query)
    
    if not results:
        # Provide helpful suggestions for common queries
        if "sagemaker" in query.lower():
            return f"""No direct results found for: {query}

However, CrewAI supports SageMaker! Check:
- **Resource:** crewai://concepts/llms
- **Configuration:** Use model="sagemaker/<your-endpoint>"
- **Required:** AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION

Try searching for: 'llm', 'AWS', or 'model configuration'"""
        elif "aws" in query.lower():
            return f"""No direct results found for: {query}

CrewAI has AWS integration tools available:
- AWS S3 Tool
- Amazon Bedrock Tool
- SageMaker support via LLM configuration

Try searching for: 'cloud', 'bedrock', or 'llm'"""
        else:
            return f"No results found for: {query}\n\nTry searching for: agents, tasks, crews, flows, llms, or tools"
    
    content = f"# Search Results for: {query}\n\n"
    for result in results[:5]:  # Limit to top 5 results
        content += f"## {result['title']}\n"
        content += f"**Source:** {result['url']}\n\n"
        content += f"{result['snippet']}\n\n---\n\n"
    
    return content

@mcp.tool()
async def get_agent_template(
    role: str,
    goal: str,
    backstory: str = None,
    tools: List[str] = None
) -> str:
    """Generate a CrewAI agent configuration template with specified parameters"""
    if backstory is None:
        backstory = f"You are an expert {role} with extensive experience."
    if tools is None:
        tools = []
    
    tools_str = f"[{', '.join(tools)}]" if tools else "[]"
    
    template = f'''from crewai import Agent

{role.lower().replace(' ', '_')}_agent = Agent(
    role="{role}",
    goal="{goal}",
    backstory="{backstory}",
    tools={tools_str},
    verbose=True,
    allow_delegation=False
)'''
    
    return template

@mcp.tool()
async def get_crew_template(agents: List[str], process: str = "sequential") -> str:
    """Generate a CrewAI crew configuration template"""
    template = f'''from crewai import Crew, Process

# Define your agents first
{chr(10).join([f"{agent.lower().replace(' ', '_')}_agent = Agent(...)" for agent in agents])}

# Create the crew
crew = Crew(
    agents=[{', '.join([f"{agent.lower().replace(' ', '_')}_agent" for agent in agents])}],
    tasks=[],  # Add your tasks here
    process=Process.{process.upper()},
    verbose=True
)

# Execute the crew
result = crew.kickoff()'''
    
    return template

@mcp.tool()
async def list_crewai_tools(category: str = None) -> str:
    """List available CrewAI tools by category"""
    global docs_fetcher
    
    if not docs_fetcher:
        docs_fetcher = CrewAIDocsFetcher()
        await docs_fetcher.__aenter__()
    
    tools = await docs_fetcher.get_tools_by_category()
    
    if category and category in tools:
        content = f"# {category} Tools\n\n"
        for tool in tools[category]:
            content += f"- {tool}\n"
    else:
        content = "# CrewAI Tools by Category\n\n"
        for cat, tool_list in tools.items():
            content += f"## {cat}\n"
            for tool in tool_list:
                content += f"- {tool}\n"
            content += "\n"
    
    return content

@mcp.tool()
async def get_concept_guide(concept: str) -> str:
    """Get detailed guide for a specific CrewAI concept"""
    global docs_fetcher
    
    if not docs_fetcher:
        docs_fetcher = CrewAIDocsFetcher()
        await docs_fetcher.__aenter__()
    
    content = await docs_fetcher.get_concept_content(concept)
    
    if content:
        return content
    else:
        return f"Could not retrieve guide for: {concept}"

def main():
    """Main entry point"""
    mcp.run()

if __name__ == "__main__":
    main()