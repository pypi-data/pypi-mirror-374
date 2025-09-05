from unittest.mock import patch
from rtedata.client import Client
import pytest

@patch("rtedata.client.requests.post")
def test_get_access_token_success(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"access_token": "FAKE_TOKEN"}

    client = Client(client_id="dummy", client_secret="dummy")
    assert client.token == "FAKE_TOKEN"
    assert mock_post.call_args[0][0] == "https://digital.iservices.rte-france.com/token/oauth/"


@patch("rtedata.client.requests.post")
def test_get_access_token_failure(mock_post):
    mock_post.return_value.status_code = 401
    mock_post.return_value.text = "Unauthorized"

    with pytest.raises(Exception) as e:
        Client(client_id="bad", client_secret="bad")

    assert "Access token error" in str(e.value)
