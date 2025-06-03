# NewScrAIper 

A (MVP) web application to extract data from articles from different digital newspapers using an LLM.
You can schedule a task selecting the period and the url. The task will be executed at 10pm UTC time 
> Note:
NewScrAIper is a state-of-the-art application, using the latest technologies, such as:

- [Langchain](https://www.langchain.com): an open-source framework designed to build apps powered by LLMs.
- [Ollama](https://ollama.com): a locally deployed AI model runner, allowing us to use LLMs easily on our computer.
- [Crawl49](https://github.com/unclecode/crawl4ai): an open-source crawler that creates easy-to-read inputs for the LLM.

Other well-known technologies:

- [MongoDB](https://www.mongodb.com)
- [FastAPI](https://fastapi.tiangolo.com)
- [Celery](https://docs.celeryq.dev)
- [Streamlit](https://streamlit.io/)


---

## Getting Started

After you clone the repository:

```bash
git clone https://github.com/ec-dani/newsscraiper.git
```

### 1. Configure the LLM

First, check the creation of the LLM instance. In this case, we are using the model `llama3:8B`.

Go to the `get_llm()` function in the [`mapping.py`] file and change the model you want to use.  
> Note: The model must already be pulled using Ollama.

### 2. Check the Database Connection

Ensure your MongoDB database connection settings are correct.

---

## Run the Application

Once you’ve saved your changes, run the following command:

```bash
docker-compose up --build
```


Now you have the app ready! 🙌
