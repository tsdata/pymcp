from typing import Optional
import os
from dataclasses import dataclass
from mcp import MCPServer

@dataclass
class TavilySearchRequest:
    query: str
    search_depth: Optional[str] = "basic"
    max_results: Optional[int] = 5
    api_key: Optional[str] = None

class TavilySearchServer(MCPServer):
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY environment variable is not set")

    async def handle_search(self, request: TavilySearchRequest) -> dict:
        """
        Performs web search using the Tavily API.
        
        Args:
            request: Search request parameters
            
        Returns:
            Dictionary containing search results
        """
        import httpx

        api_key = request.api_key or self.api_key
        url = "https://api.tavily.com/search"
        
        headers = {
            "content-type": "application/json",
            "api-key": api_key
        }
        
        params = {
            "query": request.query,
            "search_depth": request.search_depth,
            "max_results": request.max_results
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=params, headers=headers)
            response.raise_for_status()
            return response.json()

if __name__ == "__main__":
    server = TavilySearchServer()
    server.run() 