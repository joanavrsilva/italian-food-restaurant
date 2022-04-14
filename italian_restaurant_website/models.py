from django.db import models

from cloudinary.models import CloudinaryField

class Restaurant(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    opening_time = models.TimeField(auto_now=False, auto_now_add=False)
    closing_time = models.TimeField(auto_now=False, auto_now_add=False)
    menu = CloudinaryField('image', default='placeholder')

    def __str__(self):
        return self.name
