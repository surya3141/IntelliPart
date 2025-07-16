from src.data_ingestion.ingest import ingest

def test_ingest_txt():
    records = ingest("data/sample.txt")
    assert isinstance(records, list)