from pymongo import MongoClient
from pprint import pprint
from datetime import datetime



def get_db():
    collection_name = "news"
    client = MongoClient("mongodb://mongodb:27017/")
    # print("SERVER INFO")
    # pprint(client.server_info())
    db = client["noticias"]
    collection = db[collection_name]
    return collection

def check_date(article):
    article_date = article.get("date","")
    return article_date and datetime.strptime(article_date,"%Y-%m-%d").date() > datetime.now().date()

def check_article(article,collection):
    if not article.get("title"):
        return False
    if not article.get("url"):
        return False
    if collection.find_one({"url": article["url"]}):
        return False
    # if check_date(article):
    #     return False
    #Verificarque la fecha este en el periodo que dice el usuario.
    return True

def insert_article(article):
    collection = get_db()
    insert = check_article(article,collection)
    if not insert:
        return
    try:
        collection.insert_one(article)
        print(f"Inserted article: {article}")
    except Exception as e:
        print(f"Error inserting article: {e}")

def get_task_articles(task_name):
    collection = get_db()
    articles = list(collection.find({"task_name": task_name}))
    if not articles:
        return []
    for article in articles:
        if '_id' in article:
            article['_id'] = str(article['_id'])
    return articles