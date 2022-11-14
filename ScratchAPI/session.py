import json
import re

import requests

from ScratchAPI import User, CommentMessage, FollowUserMessage, LoveProjectMessage, RemixProjectMessage, StudioActivityMessage, FavoriteProjectMessage, CloudSession


class Session:
    def __init__(self, username, password):
        self.login(username, password)
        self.headers = {
            "Cookie": f"scratchcsrftoken={self.csrf_token};scratchlanguage=en;scratchsessionsid={self.session_id};",
            "x-csrftoken": self.csrf_token,
            "X-Token": self.token,
            "x-requested-with": "XMLHttpRequest",
            "referer": "https://scratch.mit.edu/"
        }

    def login(self, username, password):
        self.username = username
        login_request = requests.post(
            "https://scratch.mit.edu/login/",
            data=json.dumps({
                "username": username,
                "password": password
            }),
            headers={
                "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
                "x-csrftoken": "a",
                "x-requested-with": "XMLHttpRequest",
                "referer": "https://scratch.mit.edu"
            }
        )
        
        if login_request.json()[0]["success"] == 0:
            raise Exception(login_request.json()[0]["msg"])
        else:
            self.session_id = re.search(
                '"(.*)"',
                login_request.headers["Set-Cookie"]
            ).group()
            self.token = login_request.json()[0]["token"]

        csrf_token_request = requests.get("https://scratch.mit.edu/csrf_token/", headers={
            "Cookie": "scratchlanguage=en;permissions=%7B%7D;",
            "x-requested-with": "XMLHttpRequest",
            "referer": "https://scratch.mit.edu",
        })
        self.csrf_token = re.search(
            "scratchcsrftoken=(.*?);",
            csrf_token_request.headers["Set-Cookie"]
        ).group(1)
        self.user = User(username)

    def get_messages(self):
        messages = []
        offset = 0
        while True:
            response = requests.get(
                f"https://api.scratch.mit.edu/users/{self.username}/messages/?limit=40&offset={str(offset)}",
                headers=self.headers
            ).json()
            for message in response:
                if message["type"] == "addcomment":
                    messages.append(CommentMessage(message))
                elif message["type"] == "followuser":
                    messages.append(FollowUserMessage(message))
                elif message["type"] == "favoriteproject":
                    messages.append(FavoriteProjectMessage(message))
                elif message["type"] == "loveproject":
                    messages.append(LoveProjectMessage(message))
                elif message["type"] == "remixproject":
                    messages.append(RemixProjectMessage(message))
                elif message["type"] == "studioactivity":
                    messages.append(StudioActivityMessage(message))
                else:
                    print("unknown message: " + message["type"])
            if len(response) < 40:
                break
            offset += 40
        return messages

    def connect_project(self, project_id):
        return CloudSession(self, project_id)
