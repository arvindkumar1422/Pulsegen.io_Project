from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from src.crawler import Crawler
from src.extractor import Extractor
import uvicorn

app = FastAPI(
    title="Pulse Module Extractor API",
    description="API for extracting structured modules from documentation URLs.",
    version="1.0.0"
)

class ExtractionRequest(BaseModel):
    urls: List[str]
    max_depth: int = 1
    max_pages: int = 15
    model: str = "gpt-4o"

class ExtractionResponse(BaseModel):
    modules: List[Dict[str, Any]]
    pages_crawled: int

@app.post("/extract", response_model=ExtractionResponse)
async def extract_modules(request: ExtractionRequest):
    try:
        # Crawl
        crawler = Crawler(request.urls, max_depth=request.max_depth, max_pages=request.max_pages)
        crawler.crawl()
        content_map = crawler.get_content()
        
        if not content_map:
            raise HTTPException(status_code=400, detail="No content found to extract.")

        # Extract
        full_text = "\n\n".join(content_map.values())
        extractor = Extractor(model=request.model)
        modules = extractor.extract(full_text)
        
        return {
            "modules": modules,
            "pages_crawled": len(content_map)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
