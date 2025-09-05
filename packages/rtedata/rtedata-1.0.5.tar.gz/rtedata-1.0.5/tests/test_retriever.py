import json
from unittest.mock import patch
from rtedata.retriever import Retriever
from rtedata.catalog import Catalog
from rtedata.tools import Logger

@patch("rtedata.retriever.requests.get")
def test_retrieve_single_data_type(mock_get):
    dummy_token = "FAKE_TOKEN"
    logger = Logger().logger
    catalog = Catalog()

    retriever = Retriever(token=dummy_token, logger=logger, catalog=catalog)

    mock_get.return_value.status_code = 200
    with open("./tests/data/prices.json") as f:
        mock_get.return_value.json.return_value = json.load(f)
    
    result = retriever.retrieve(
        start_date="2024-01-01 00:00:00",
        end_date="2024-01-03 00:00:00",
        data_type="prices"
    )

    assert "prices" in result
    assert not result["prices"].empty

@patch("rtedata.retriever.requests.get")
def test_retrieve_handles_api_error(mock_get):
    dummy_token = "FAKE_TOKEN"
    logger = Logger().logger
    catalog = Catalog()
    retriever = Retriever(token=dummy_token, logger=logger, catalog=catalog)

    mock_get.return_value.status_code = 500
    mock_get.return_value.text = "Server error"

    result = retriever.retrieve(
        start_date="2024-01-01 00:00:00",
        end_date="2024-01-03 00:00:00",
        data_type="prices"
    )

    assert "prices" not in result
