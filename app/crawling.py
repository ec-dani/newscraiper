import requests
import asyncio
from mapping import map_news_extractor

from typing import List
from crawl4ai import AsyncWebCrawler, BrowserConfig ,CrawlResult, CrawlerRunConfig, DefaultMarkdownGenerator, PruningContentFilter, CacheMode
from langchain_text_splitters import MarkdownHeaderTextSplitter,RecursiveCharacterTextSplitter



async def basic_crawl(url:str):
    print(f"Entrando a basic_crawl")
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        # magic=True,
        exclude_external_links=True,
        exclude_social_media_links=True,
        word_count_threshold=1,
        exclude_external_images=True,
        excluded_tags=['script', 'style','iframe', 'noscript', 'form', 'footer', 'aside','figure','picture','img','svg'],
        markdown_generator=DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(threshold=0.27),
        ),
    )
    try:
        print(f"Entrando a AsyncWebCrawler")
        #Error in basic_Crawl: database is locked.
        browser_config = BrowserConfig(browser_mode="managed", headless=True)
        async with AsyncWebCrawler(config=browser_config) as crawler:
            await asyncio.sleep(2.7)
            results: List[CrawlResult] = await crawler.arun(url=url,config=config)
            for i,result in enumerate(results):
                # print(f"Result {i}:")
                # print(f"success: {result.success}")
                if result.success:
                    print(f"URL: {url}")
                    print(f"Raw_markdown: {len(result.markdown.raw_markdown) }")
                    print(f"Fit_markdown: {len(result.markdown.fit_markdown) }")                    
                else:
                    print(f"Error: {result.error_message}")
        return results[0].markdown.raw_markdown
    except Exception as e:
        return f"Error in basic_Crawl: {e}"

def chunking(markdown_text):
    headers_to_split_on = [
        ("#", "Section"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
    md_header_splits = markdown_splitter.split_text(markdown_text)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    splits = text_splitter.split_documents(md_header_splits)
    print(f"Chunks: {len(splits)}")
    return splits

async def main(url:str, task_name:str):
    try:
        print(f"Entrando crawl4AI : {task_name}")
        rawmarkdown= await basic_crawl(url)
        chunks= chunking(rawmarkdown)
        text_splits = [doc.page_content for doc in chunks]
        # tests= text_splits[20:40]
        # print("TEST")
        # print(tests)
        result=map_news_extractor(text_splits,task_name)
        # print("RESULT CRAWL MAIN")
        # print(result)
        return result
    except Exception as e:
        print(f"Error in main: {e}")
        return f"Error in main crawl: {e}"

    