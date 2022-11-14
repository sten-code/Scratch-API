# Scratch-API


## Example
```python
from ScratchAPI import User, Project


user = User("griffpatch")
project = Project(user.get_projects()[0].id())

#  User
print(user.joined_datetime())
print(user.id())
print(user.country())
print(user.message_count())
print(user.scratchteam())
print(user.scratchteam())
print(user.status())
print(user.get_follower_count())

print(user.get_projects())
print(user.get_favorite_projects())

print(user.get_followers())
print(user.get_following())


# Project
print(project.id())
print(project.title())
print(project.notes_and_credits())
print(project.instructions())
print(project.is_public())
print(project.comments_allowed())
print(project.author().username)
print(project.project_thumbnail_url())
print(project.created_datetime())

print(project.created_datetime())
print(project.modified_datetime())
print(project.shared_datetime())
print(project.views())
print(project.loves())
print(project.favorites())
print(project.remixes_count())
print(project.remix_parent())
print(project.remix_root())
print(project.visibility())
print(project.is_published())
print(project.visibility())

print(project.get_remixes())
print(project.get_comments())

```
