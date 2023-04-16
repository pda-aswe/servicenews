import requests
import json
import os

class WorldNewsApiCaller:
    def __init__(self):
        self.baseURL = "https://api.worldnewsapi.com/search-news?"
        self.apiKey = self.__loadAPIKey()

    def __loadAPIKey(self):
        if os.path.exists('key.txt'):
            with open('key.txt') as f:
                return f.readline().strip('\n')
        else:
            print("api key file missing")
            quit()
    
    def newsRequest(self, numberOfArticles: int, location: dict = None):
        # Make sure input parameters are correct
        if numberOfArticles > 100 or numberOfArticles < 1:
            return -1

        urlRequest = self.baseURL + "number=" + str(numberOfArticles) + "&api-key=" + self.apiKey
        if(location is not None):
            if('longitude' in location and 'latitude' in location):
                urlRequest += "&location-filter=" + str(location['latitude']) + ',' + str(location['longitude']) + ',100'

        response = requests.post(urlRequest)
        if response.status_code == 200:
            try:
                newsData = json.loads(response.text)
            except:
                return -1

            newsResult = []
            if "news" in newsData:
                for article in newsData["news"]:
                    newsResult.append({
                        "summary": article["summary"],
                        "text": article["text"]
                    })
                return newsResult
            
        return -1