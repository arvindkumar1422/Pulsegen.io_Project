import argparse
import asyncio
import json
import sys
from src.crawler import Crawler
from src.extractor import Extractor
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Pulse Module Extractor CLI")
    parser.add_argument('--urls', nargs='+', required=True, help="One or more URLs to crawl")
    parser.add_argument('--depth', type=int, default=1, help="Crawling depth (default: 1)")
    parser.add_argument('--model', type=str, default="gpt-4o", help="OpenAI model to use")
    parser.add_argument('--output', type=str, default="output.json", help="Output JSON file path")

    args = parser.parse_args()

    print(f"🚀 Starting extraction for: {args.urls}")
    
    # 1. Crawl
    print("🕷️  Crawling...")
    crawler = Crawler(args.urls, max_depth=args.depth)
    crawler.crawl()
    content_map = crawler.get_content()
    
    if not content_map:
        print("❌ No content extracted. Exiting.")
        sys.exit(1)
        
    print(f"✅ Crawled {len(content_map)} pages.")
    
    # 2. Extract
    print("🧠 Analyzing with AI...")
    full_text = "\n\n".join(content_map.values())
    
    extractor = Extractor(model=args.model)
    try:
        modules = extractor.extract(full_text)
        
        # 3. Output
        print(json.dumps(modules, indent=2))
        
        with open(args.output, 'w') as f:
            json.dump(modules, f, indent=2)
        print(f"\n💾 Results saved to {args.output}")
        
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
