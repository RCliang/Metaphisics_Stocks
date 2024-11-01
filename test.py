import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://github.com/trending/python?since=daily")
        print(result.markdown)  # Print clean markdown content

if __name__ == "__main__":
    asyncio.run(main())