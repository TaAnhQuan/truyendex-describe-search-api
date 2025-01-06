from django.db import models

# Create your models here.
class Manga(models.Model):
    manga_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=100)
    embedding = models.CharField(max_length=100000)

    def __str__(self):
        return self.title
    
    class Meta:
        managed = False
        db_table = 'manga'