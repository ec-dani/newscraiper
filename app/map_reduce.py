from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import JsonOutputParser
from typing import List
from mongodb import insert_article
import json


map_prompt = """
You are an expert web scraper. I want you to analyze the following text written in Markdown format, which represents a series of news articles from a digital newspaper.

            Your task is to extract the following information for **each news article**:

            1. **Title**: The text inside the second-level heading (`##`) which also contains a link.  
            2. **Author**: The name of the author, which appears just below the headline, usually as a hyperlink.  
            3. **Lead paragraph**: The plain text that appears immediately after the author, summarizing or introducing the article.
            4. **URL**: The hyperlink associated with the headline.
            5. **Date**: Extract the date from the article's URL in `YYYY-MM-DD` format (e.g., if the URL is `https://elpais.com/espana/2025-04-16/...`, the date is `2025-04-16`).

            Present the extracted data in the following structured JSON format:
            {{
            "title": "",
            "author": "",
            "lead": "",
            "url": "",
            "date": ""
            }}

         DONT MAKE THINGS UP. IF YOU CAN NOT EXTRACT THE DATA LEAVE THE FIELD EMPTY.
         JUST RETURN THE JSON DATA WITHOUT ANY ADDITIONAL TEXT OR EXPLANATION.
"""

reduce_prompt = """
You are an expert data consolidator. Merge the following extracted news article JSON data into a comprehensive list. 

Ensure:
- No duplicate entries
- Preserve the original order of articles
- If multiple extractions have similar data, keep the most complete one

Return the final list of news article extractions as a JSON array WITHOUT ANY ADDITIONAL TEXT OR EXPLANATION.
"""
def create_map_reduce_news_extractor(splits ):
    print("Using Ollama LLM")
    llm = ChatOllama(base_url="http://192.168.1.52:11434",model = "llama3:8b",temperature = 0, format='json',verbose=True)

    # Map Prompt for individual document extraction
    map_prompt_template = ChatPromptTemplate([
        ("system", map_prompt),
        ("human", "{text}")
    ])
    # Create map chain
    map_chain = map_prompt_template | llm | JsonOutputParser()

    # Create reduce chain
    mapped_results = []
    for i,split in enumerate(splits):
        try:
            print(f"---------MAPING chunk {i}---------------")
            result = map_chain.invoke({"text": split})
            #Meter en BD
            # with open("./data/elpais_map.json", "a",encoding='utf-8') as f:
            #     f.write(json.dumps(result, ensure_ascii=False) + ",\n")
            #     f.close()
            mapped_results.append(result)
            insert_article(result)
        except Exception as e:
            print(f"Error map: {e}")
    return mapped_results