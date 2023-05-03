
# from djongo import models
# from bson import ObjectId

# class Article(models.Model):
#     title = models.CharField(max_length=200)
#     content = models.TextField()
#     author = models.CharField(max_length=100)
#     date = models.DateTimeField(auto_now_add=True)
#     slug = models.SlugField()
    
#     def __str__(self):
#         return self.title

#     class Meta:
#         indexes = [
#             models.Index(fields=['slug'], name='slug_idx', unique=True),
#         ]

