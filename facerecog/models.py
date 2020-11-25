from django.db import models
from picklefield.fields import PickledObjectField

# Create your models here.
class RegisterFaces(models.Model):
    face_features_names = PickledObjectField()

class RecognizeLogs(models.Model):
    name = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name