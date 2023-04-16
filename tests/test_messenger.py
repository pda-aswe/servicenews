from src import messenger
from unittest.mock import patch, ANY, MagicMock
import json

@patch("api_caller.WorldNewsApiCaller")
def test_connect(_):
    obj = messenger.Messenger()
    with patch.object(obj, 'mqttConnection') as mock_connect:
        obj.connect()
        mock_connect.connect.assert_called_with("localhost",1883,60)

@patch("api_caller.WorldNewsApiCaller")
def test_disconnect(_):
    obj = messenger.Messenger()
    with patch.object(obj, 'connected', True), patch.object(obj, 'mqttConnection') as mock_connect:
        obj.disconnect()
        mock_connect.disconnect.assert_called()

@patch("api_caller.WorldNewsApiCaller")
def test_foreverLoop(_):
    obj = messenger.Messenger()
    with patch.object(obj, 'mqttConnection') as mock_connect:
        obj.foreverLoop()
        mock_connect.loop_forever.assert_called()

@patch("api_caller.WorldNewsApiCaller")
def test_onMQTTconnect(_):
    obj = messenger.Messenger()
    mock_client = MagicMock()
    obj._Messenger__onMQTTconnect(mock_client,None,None,None)
    mock_client.subscribe.assert_called_with([("req/news/<Anzahl der Artikel>",0), ("location/current", 0)])

@patch("api_caller.WorldNewsApiCaller")
def test_onMQTTMessage(_):
    obj = messenger.Messenger()
    obj._Messenger__onMQTTMessage(MagicMock(),None,None)

class DummyMSG:
    def __init__(self):
        self.payload = ""

    def set_payload(self,data):
        self.payload = str.encode(data)

@patch("api_caller.WorldNewsApiCaller")
def test_newsServiceCallback(mockApiService):
    obj = messenger.Messenger()
    responseData = DummyMSG()
    msgData = {"numArticles":1}
    responseData.set_payload(json.dumps(msgData))

    with patch.object(obj, 'newsApiCaller') as mockApiService:
        mockApiService.newsRequest.return_value = {
            "summary": "Lorem ipsum dolor",
            "text": "Lorem ipsum dolor"
        }
        obj._Messenger__newsServiceCallback(None,None,responseData)
        mockApiService.newsRequest.assert_called_with(1, None)

@patch("api_caller.WorldNewsApiCaller")
def test_locationUpdateCallback(_):
    obj = messenger.Messenger()
    dummyLocationMsg = DummyMSG()
    msgData = {
        'latitude': 1.0,
        'longitude': 2.0
    }
    dummyLocationMsg.set_payload(json.dumps(msgData))
    obj._Messenger__locationUpdateCallback(None, None, dummyLocationMsg)
    assert(obj.location == msgData)