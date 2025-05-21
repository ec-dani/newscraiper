import requests
import asyncio
from map_reduce import create_map_reduce_news_extractor
from typing import List
from crawl4ai import AsyncWebCrawler, BrowserConfig ,CrawlResult, CrawlerRunConfig, DefaultMarkdownGenerator, PruningContentFilter
from langchain_text_splitters import MarkdownHeaderTextSplitter,RecursiveCharacterTextSplitter



async def basic_crawl(url="https://elpais.com/",name="elpais"):
    print(f"Entrando a basic_crawl")
    config = CrawlerRunConfig(
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
        browser_config = BrowserConfig(browser_mode="builtin", headless=True)
        async with AsyncWebCrawler(config=browser_config) as crawler:
            results: List[CrawlResult] = await crawler.arun(url=url,config=config)
            print("Results:")
            for i,result in enumerate(results):
                print(f"Result {i}:")
                print(f"success: {result.success}")
                if result.success:
                    print(f"{url}:")
                    print(f"Raw_markdown: {len(result.markdown.raw_markdown) }")
                    print(f"Fit_markdown: {len(result.markdown.fit_markdown) }")
                    # with open(f"./markdowns/{name}_fit_mardown.txt", "w",encoding='utf-8') as f:
                    #     f.write(result.markdown.fit_markdown)
                    #     print(f"Saved to {name}_fit_markdown.txt")
                    #     f.close()
                    # with open(f"./markdowns/{name}_markdown.txt", "w",encoding='utf-8') as g:
                    #     g.write(result.markdown.raw_markdown)
                    #     print(f"Saved to {name}_markdown.txt")
                    #     g.close()
                    
                else:
                    print(f"Error: {result.error_message}")
        return results[0].markdown.raw_markdown
    except Exception as e:
        print(f"Error in basic_Crawl: {e}")
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
    print(len(splits))
    return splits

async def main(url="https://elpais.com/",name="elpais"):
    try:
        print(f"Entrando crawl4AI con: {url}, {name}")
        # rawmarkdown= asyncio.run(basic_crawl(url,name))
        rawmarkdown= await basic_crawl(url,name)
        chunks= chunking(rawmarkdown)
        text_splits = [doc.page_content for doc in chunks]
        tests= text_splits[20:40]
        print("TEST")
        print(tests)
        result=create_map_reduce_news_extractor(tests)
        print("RESULT")
        print(result)
        return result
    except Exception as e:
        print(f"Error in main: {e}")
        raise

    