from pymongo import MongoClient
from pprint import pprint


#553a6a3a-ffeb-4646-a673-15de18aa0656
#bb197b4e-f4b7-4232-95d7-272bbad3ffcd
#4fa2890e-8f3a-44dd-801e-d5a66b2d9462
#e1b603ac-612e-41e6-9120-0d1a0c89737a

def get_db():
    collection_name = "news"
    client = MongoClient("mongodb://mongodb:27017/")
    print("SERVER INFO")
    pprint(client.server_info())
    db = client["noticias"]
    collection = db[collection_name]
    return collection

def check_article(article,collection):
    if not article.get("title"):
        return False
    if not article.get("url"):
        return False
    if collection.find_one({"url": article["url"]}):
        return False
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
