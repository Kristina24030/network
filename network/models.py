from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    following = models.ManyToManyField("self", symmetrical=False, blank=True, related_name="followers")

class Post(models.Model):
    content = models.CharField(max_length=300)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    date = date = models.DateTimeField(auto_now_add=True) 
    likes = models.ManyToManyField(User, blank=True, related_name="liked_posts")
    
    def __str__(self):
        return f"Post {self.id} made by {self.user} on {self.date.strftime('%d %b %Y %H:%M:%S')}"
    
