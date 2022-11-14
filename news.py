from datetime import datetime

import requests


class News:
    def __init__(self, json):
        self.data = json

    def id(self):
        return self.data["id"]

    def datetime(self):
        return datetime.strptime(self.data["stamp"], "%Y-%m-%dT%H:%M:%S.%fZ")

    def headline(self):
        return self.data["headline"]

    def url(self):
        return self.data["url"]

    def image_url(self):
        return self.data["image"]

    def description(self):
        return self.data["copy"]


def get_news():
    news = []
    response = requests.get("https://api.scratch.mit.edu/news/").json()
    for item in response:
        news.append(News(json=item))
    return news
