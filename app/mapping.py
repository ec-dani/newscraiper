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

def get_llm():
    print("Using Ollama LLM")
    llm = ChatOllama(model = "llama3:8b",temperature = 0, format='json',verbose=True)
    return llm

def map_news_extractor(splits, task_name ):
    llm= get_llm()
    map_prompt_template = ChatPromptTemplate([
        ("system", map_prompt),
        ("human", "{text}")
    ])
    map_chain = map_prompt_template | llm | JsonOutputParser()

    mapped_results = []
    for i,split in enumerate(splits):
        try:
            print(f"---------MAPING chunk {i}; {task_name}---------------")
            result = map_chain.invoke({"text": split})
            result["task_name"] = task_name
            mapped_results.append(result)
            insert_article(result)
        except Exception as e:
            print(f"Error map: {e}")
    return mapped_results