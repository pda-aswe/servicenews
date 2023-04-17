# News Service

Uses worldnewsapi to gather news.

## Datenstruktur des Topics req/news
'numArticles' is required to be between 1 to 100. 'location' is an optional argument
```json
{
  "numArticles": 1
  "location": {
    "latitude": 0.0
    "longitude": 0.0
  }
}
```

## Datenstruktur des Topics news/article
```json
{
   "summary": "Lorem ipsum dolor",
   "text": "Lorem ipsum dolor"
}
```
