import json
from datetime import datetime

import requests

SCRATCH_URL = "https://scratch.mit.edu"
API_URL = "https://api.scratch.mit.edu"
UPLOADS_URL = "https://uploads.scratch.mit.edu"
SITE_API = f"{SCRATCH_URL}site-api"
SITE_USERS = f"{SITE_API}/users"
PROXY = f"{API_URL}/proxy"
USERS = f"{API_URL}/users"
PROJECTS = f"{API_URL}/projects"
STUDIOS = f"{API_URL}/studios"
GET_IMAGE = f"{UPLOADS_URL}/get_image"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36"}


class InvalidUserException(Exception):
    pass


class Project:
    def __init__(self, project_id: int = None, json: dict = None):
        if project_id is None:
            if json is None:
                raise Exception("need paramaters")
            else:
                self.data = json
        else:
            self.data = {"id": project_id}
            self.update_data()

    def update_data(self):
        self.data = requests.get(f"{PROJECTS}/{self.id()}").json()

    def id(self) -> int:
        return self.data["id"]

    def title(self) -> str:
        return self.data["title"]

    def notes_and_credits(self) -> str:
        return self.data["description"]

    def instructions(self) -> str:
        return self.data["instructions"]

    def is_public(self) -> bool:
        return self.data["public"]

    def comments_allowed(self) -> bool:
        return self.data["comments_allowed"]

    def author(self):
        return User(json=self.data["author"])

    def project_thumbnail_url(self, width: int = 480, height: int = 360) -> str:
        return f"{GET_IMAGE}/project/{self.id()}_{width}x{height}.png"

    def created_datetime(self) -> datetime:
        return datetime.strptime(self.data["history"]["created"],
                                 "%Y-%m-%dT%H:%M:%S.%fZ")

    def modified_datetime(self) -> datetime:
        return datetime.strptime(self.data["history"]["modified"],
                                 "%Y-%m-%dT%H:%M:%S.%fZ")

    def shared_datetime(self) -> datetime:
        return datetime.strptime(self.data["history"]["shared"],
                                 "%Y-%m-%dT%H:%M:%S.%fZ")

    def views(self) -> int:
        return self.data["stats"]["views"]

    def loves(self) -> int:
        return self.data["stats"]["loves"]

    def favorites(self) -> int:
        return self.data["stats"]["favorites"]

    def remixes_count(self) -> int:
        return self.data["stats"]["remixes"]

    def remix_parent(self) -> int:
        return self.data["remix"]["parent"]

    def remix_root(self) -> int:
        return self.data["remix"]["root"]

    def visibility(self) -> bool:
        return self.data["visibility"]

    def is_published(self) -> bool:
        return self.data["is_published"]

    def get_comments(self) -> list:
        comments = []
        offset = 0
        while True:
            response = requests.get(
                f"""{USERS}/{self.author().username}/
                projects/{self.id()}/
                comments/?limit=40&offset={offset}"""
            ).json()
            for comment in response:
                comments.append(CommentMessage(comment))
            if len(response) < 40:
                break
            offset += 40
        return comments

    def love(self, session) -> dict:
        return requests.post(
            f"""{PROXY}/projects/{self.id()}/loves/
            user/{session.username}""",
            headers=session.headers
        ).json()

    def unlove(self, session) -> dict:
        return requests.delete(
            f"""{PROXY}/projects/{self.id()}/loves/
            user/{session.username}""",
            headers=session.headers
        ).json()

    def favorite(self, session) -> dict:
        return requests.post(
            f"""{PROXY}/projects/{self.id()}/favorites/
            user/{session.username}""",
            headers=session.headers
        ).json()

    def unfavorite(self, session) -> dict:
        return requests.delete(
            f"""{PROXY}/projects/{self.id()}/favorites/
            user/{session.username}""",
            headers=session.headers
        ).json()

    def get_remixes(self) -> list:
        projects = []
        offset = 0
        while True:
            response = requests.get(
                f"""{PROJECTS}/{self.id()}/
                remixes/?limit=40&offset={offset}"""
            ).json()
            for project in response:
                projects.append(Project(json=project))
            if len(response) < 40:
                break
            offset += 40
        return projects

    def post_comment(self, session, content, parent_id="", commentee_id="") -> dict:
        json_headers = dict(session.headers)
        json_headers["accept"] = "application/json"
        json_headers["Content-Type"] = "application/json"
        json_headers["referer"] += f"projects/{self.id()}"
        return requests.post(
            f"{PROXY}/comments/project/{self.id()}/",
            headers=json_headers,
            data=json.dumps({
                "commentee_id": commentee_id,
                "content": content,
                "parent_id": parent_id,
            })
        ).json()


class User:
    def __init__(self, username: str = None, json: dict = None) -> None:
        if username is None:
            if json is None:
                raise Exception("Need paramaters to load user")
            else:
                self.username = json["username"]
                self.data = json
        else:
            self.username = username
            self.data = requests.get(f"{API_URL}/users/{self.username}").json()
            if "code" in self.data:
                raise InvalidUserException("That user doesn't exist")

    def update_data(self) -> None:
        self.data = requests.get(f"{API_URL}/users/{self.username}").json()
        if "code" in self.data:
            if self.data["code"] == "ResourceNotFound":
                raise Exception("That user doesn't exist")

    def joined_datetime(self) -> datetime:
        return datetime.strptime(
            self.data["history"]["joined"],
            "%Y-%m-%dT%H:%M:%S.%fZ")

    def id(self) -> int:
        return self.data["id"]

    def country(self) -> str:
        return self.data["profile"]["country"]

    def message_count(self) -> int:
        return requests.get(
            f"{USERS}/{self.username}/messages/count",
            headers=HEADERS
        ).json()["count"]

    def avatar_url(self, avatar_size: int) -> str:
        return f"{GET_IMAGE}/user/{self.id()}_{avatar_size}x{avatar_size}.png"

    def scratchteam(self) -> bool:
        return self.data["scratchteam"]

    def status(self) -> str:
        return self.data["profile"]["status"]

    def bio(self) -> str:
        return self.data["profile"]["bio"]

    def get_projects(self) -> list[Project]:
        projects = []
        for p in requests.get(f"{USERS}/{self.username}/projects/").json():
            projects.append(Project(project_id=p["id"]))
        return projects

    def get_favorite_projects(self) -> list[Project]:
        projects = []
        offset = 0
        while True:
            response = requests.get(
                f"{USERS}/{self.username}/favorites/?limit=40&offset={offset}"
            ).json()
            for project in response:
                projects.append(Project(json=project))
            if len(response) < 40:
                break
            offset += 40
        return projects

    def get_followers(self) -> list:
        users = []
        offset = 0
        while True:
            response = requests.get(
                f"{USERS}/{self.username}/followers/?limit=40&offset={offset}"
            ).json()
            for user in response:
                users.append(User(json=user))
            if len(response) < 40:
                break
            offset += 40
        return users

    def get_follower_count(self) -> int:
        followers = str(requests.get(
            f"{SCRATCH_URL}/users/{self.username}/followers", headers=HEADERS
        ).content)

        d = "Followers ("
        index = followers.index(d) + len(d)
        followers = followers[index:]
        index = followers.index(")")
        followers = followers[:index]
        return int(followers)

    def get_following(self) -> list:
        users = []
        offset = 0
        while True:
            response = requests.get(
                f"{USERS}/{self.username}/following/?limit=40&offset={offset}"
            ).json()
            for user in response:
                users.append(User(json=user))
            if len(response) < 40:
                break
            offset += 40
        return users

    def post_comment(self, session, content: str,
                     reply_message_id="", commentee_id="") -> None:
        requests.post(
            f"{SITE_API}/comments/user/{self.username}/add/",
            headers=session.headers,
            data=json.dumps({
                "commentee_id": commentee_id,
                "content": content,
                "parent_id": reply_message_id,
            })
        )

    def follow(self, session) -> dict:
        return requests.put(
            f"""{SITE_USERS}/followers/{self.username}/add/?usernames={
            session.username}""",
            headers=session.headers
        ).json()

    def unfollow(self, session) -> dict:
        return requests.put(
            f"""{SITE_USERS}/followers/{self.username}/remove/
            ?usernames={session.username}""",
            headers=session.headers
        ).json()

    def report(self, session, field) -> None:
        requests.post(
            f"{SITE_USERS}/all/{self.username}/report/",
            headers=session.headers,
            data=json.dumps({"selected_field": field})
        )

    def set_bio(self, session, content) -> requests.Response:
        return requests.put(
            f"{SITE_USERS}/all/{self.username}",
            data=json.dumps({"bio": content}),
            headers=session.headers
        )

    def set_status(self, session, content) -> requests.Response:
        return requests.put(
            f"https://scratch.mit.edu/site-api/users/all/{self.username}",
            data=json.dumps({"status": content}),
            headers=session.headers
        )

    def set_featured_project(self, session, project, label="") -> None:
        """
        label options:
            featured project: empty string
            featured tutorial: 0
            work in progress: 1
            remix this: 2
            my favorite things: 3
            why i scratch: 4
        """
        json_headers = dict(session.headers)
        json_headers["referer"] += f"users/{self.username}"
        requests.put(
            f"{SITE_USERS}/all/{self.username}",
            data=json.dumps({
                "featured_project": project.project_id(),
                "featured_project_label": label
            }),
            headers=session.headers
        )


def get_user(username: str):
    return User(json=requests.get(f"{USERS}/{username}").json())


def get_project(id: int | str):
    return Project(json=requests.get(f"{PROJECTS}/{id}").json())


class Studio:
    def __init__(self, studio_id: int = None, json: str = None) -> None:
        if studio_id is None:
            if json is None:
                raise Exception("need paramaters")
            else:
                self.data = json
        else:
            self.data = {"id": studio_id}
            self.update_data()

    def update_data(self) -> None:
        request = requests.get(f"{STUDIOS}/{self.studio_id()}")
        self.data = request.json()

    def studio_id(self) -> int:
        return self.data["id"]

    def title(self) -> str:
        return self.data["title"]

    def host_id(self) -> int:
        return self.data["host"]

    def description(self) -> str:
        return self.data["description"]

    def visibility(self) -> str:
        return self.data["visibility"]

    def is_public(self) -> bool:
        return self.data["public"]

    def is_open_to_all(self) -> bool:
        return self.data["open_to_all"]

    def comments_allowed(self) -> bool:
        return self.data["comments_allowed"]

    def image_url(self, width=200, height=130) -> str:
        return f"{GET_IMAGE}/gallery/{self.studio_id()}_{width}x{height}.png"

    def created_datetime(self) -> datetime:
        return datetime.strptime(self.data["history"]["created"],
                                 "%Y-%m-%dT%H:%M:%S.%fZ")

    def modified_datetime(self) -> datetime:
        return datetime.strptime(self.data["history"]["modified"],
                                 "%Y-%m-%dT%H:%M:%S.%fZ")

    def comments_count(self) -> int:
        return self.data["stats"]["comments"]

    def followers_count(self) -> int:
        return self.data["stats"]["followers"]

    def managers_count(self) -> int:
        return self.data["stats"]["managers"]

    def projects_count(self) -> int:
        return self.data["stats"]["projects"]


def get_studio(id: int | str):
    return Studio(json=requests.get(f"{STUDIOS}/{id}").json())


class Message:
    def __init__(self, json: str) -> None:
        self.json = json

    def id(self) -> int:
        return self.json["id"]

    def datetime(self) -> datetime:
        return datetime.strptime(self.json["datetime_created"],
                                 "%Y-%m-%dT%H:%M:%S.%fZ")

    def actor(self) -> User:
        return User(username=self.json["actor_username"])

    def type(self) -> str:
        return self.json["type"]


class FollowUserMessage(Message):
    def followed_user(self) -> User:
        return User(username=self.json["followed_username"])


class CommentMessage(Message):
    def project(self) -> Project:
        return Project(project_id=self.json["comment_obj_id"])

    def comment(self):
        return self.json["comment_fragment"]


class FavoriteProjectMessage(Message):
    def project(self) -> Project:
        return Project(project_id=self.json["project_id"])


class LoveProjectMessage(Message):
    def project(self) -> Project:
        return Project(project_id=self.json["project_id"])


class RemixProjectMessage(Message):
    def original_project(self) -> Project:
        return Project(project_id=self.json["parent_id"])

    def remix_project(self) -> Project:
        return Project(project_id=self.json["project_id"])


class StudioActivityMessage(Message):
    def studio(self) -> Studio:
        return Studio(studio_id=self.json["gallery_id"])
