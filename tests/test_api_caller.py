import os
import pytest
from unittest.mock import Mock, patch
from src.api_caller import WorldNewsApiCaller

def test_init_no_key_file(capfd, monkeypatch):
    def mock_quit():
        pass

    monkeypatch.setattr(os.path, "exists", lambda x: False)
    monkeypatch.setattr("builtins.quit", mock_quit)

    WorldNewsApiCaller()

    captured = capfd.readouterr()
    assert "api key file missing" in captured.out

# Create a temporary key file for testing
@pytest.fixture(scope="module")
def create_key_file():
    key_file = "key.txt"
    with open(key_file, "w") as f:
        f.write("test_key")
    yield key_file
    os.remove(key_file)

def test_load_api_key(create_key_file, monkeypatch):
    def mock_init(self):
        self.baseURL = "https://api.worldnewsapi.com/search-news?"
        self.apiKey = None

    monkeypatch.setattr(WorldNewsApiCaller, "__init__", mock_init)
    api_caller = WorldNewsApiCaller()
    api_key = api_caller._WorldNewsApiCaller__loadAPIKey()
    assert api_key == "test_key"

def test_news_request_invalid_number_of_articles():
    api_caller = WorldNewsApiCaller()
    assert api_caller.newsRequest(-1) == -1
    assert api_caller.newsRequest(0) == -1
    assert api_caller.newsRequest(101) == -1

def test_news_request_invalid_location():
    api_caller = WorldNewsApiCaller()
    assert api_caller.newsRequest(1, {"longitude": 0}) == -1
    assert api_caller.newsRequest(1, {"latitude": 0}) == -1
    assert api_caller.newsRequest(1, {"lat": 0, "lon": 0}) == -1

@patch("api_caller.requests.get")
def test_news_request_success(mock_post):
    api_caller = WorldNewsApiCaller()
    response = Mock()
    response.status_code = 200
    response.text = '{"news": [{"summary": "Test summary", "text": "Test text"}]}'
    mock_post.return_value = response

    articles = api_caller.newsRequest(1)
    assert len(articles) == 1
    assert articles[0]["summary"] == "Test summary"
    assert articles[0]["text"] == "Test text"

@patch("api_caller.requests.get")
def test_news_request_invalid_json(mock_get):
    api_caller = WorldNewsApiCaller()
    response = Mock()
    response.status_code = 200
    response.text = '{"news": [{"summary": "Test summary", "text": "Test text"}'  # Missing closing brace
    mock_get.return_value = response

    articles = api_caller.newsRequest(1)
    assert articles == -1