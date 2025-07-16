from elasticsearch import Elasticsearch, helpers
import json

# ElasticSearch connection (adjust host/port if needed)
es = Elasticsearch("http://localhost:9200")

INDEX_NAME = "intellipart"

def create_index():
    """
    Creates the index with a mapping suitable for your data.
    """
    if es.indices.exists(index=INDEX_NAME):
        print(f"Index '{INDEX_NAME}' already exists. Deleting and recreating...")
        es.indices.delete(index=INDEX_NAME)

    mapping = {
        "mappings": {
            "properties": {
                "system": {"type": "keyword"},
                "part": {"type": "text"},
                "attributes": {"type": "object"}
            }
        }
    }
    es.indices.create(index=INDEX_NAME, body=mapping)
    print(f"Index '{INDEX_NAME}' created.")

def load_data(jsonl_path):
    """
    Loads data from a JSONL file.
    """
    with open(jsonl_path, "r") as f:
        for line in f:
            yield json.loads(line)

def bulk_ingest(jsonl_path):
    """
    Bulk ingest documents into ElasticSearch.
    """
    actions = []
    for doc in load_data(jsonl_path):
        actions.append({
            "_index": INDEX_NAME,
            "_source": doc
        })
    helpers.bulk(es, actions)
    print(f"Ingested {len(actions)} documents into '{INDEX_NAME}'.")

def test_search(query_text):
    """
    Basic search for demonstration.
    """
    resp = es.search(
        index=INDEX_NAME,
        query={
            "multi_match": {
                "query": query_text,
                "fields": ["system", "part", "attributes.*"]
            }
        }
    )
    print("Search results:")
    for hit in resp["hits"]["hits"]:
        print(hit["_source"])

if __name__ == "__main__":
    # 1. Create index
    create_index()
    # 2. Ingest your dataset (now using training Dataset.jsonl)
    bulk_ingest("data/training Dataset.jsonl")
    # 3. Interactive search loop
    print("\nType your search query (or 'exit' to quit):")
    while True:
        user_query = input("> ")
        if user_query.lower() == "exit":
            break
        test_search(user_query)