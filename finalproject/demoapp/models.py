from djongo import models

# Create your models here.
class USERS(models.Model):
    name = models.CharField(max_length=100)
    #email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)