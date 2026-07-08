from pymongo import MongoClient
import json

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Database and Collection
db = client["BUYPLASTIC_db"]
collection = db["products_urls"]

# Read JSON file
with open("product_urls.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Prepare documents for MongoDB
if isinstance(data, list):

    # If the list contains strings (URLs)
    if data and isinstance(data[0], str):
        documents = [{"url": url} for url in data]

    # If the list already contains dictionaries
    elif data and isinstance(data[0], dict):
        documents = data

    else:
        raise TypeError("Unsupported JSON format.")

    collection.insert_many(documents)
    print(f"{len(documents)} documents inserted successfully.")

elif isinstance(data, dict):
    collection.insert_one(data)
    print("1 document inserted successfully.")

else:
    raise TypeError("JSON must contain a dictionary or a list.")

client.close()