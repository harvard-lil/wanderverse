from django.db import models


class Book(models.Model):
    author = models.CharField(max_length=1000, null=True, blank=True)
    title = models.TextField(null=True, blank=True)

class Poem(models.Model):
    first_line = models.TextField(blank=True, null=True)
    first_book = models.ForeignKey(Book, related_name='first_line', on_delete=models.DO_NOTHING)
    second_line = models.TextField(blank=True, null=True)
    second_book = models.ForeignKey(Book, related_name='second_line', on_delete=models.DO_NOTHING)
