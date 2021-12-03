from django.db import models


class Category(models.Model):
    name = models.CharField(
        max_length=256,
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
    )

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=256,
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
    )

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=256,
    )
    year = models.DateField()
    description = models.CharField(
        max_length=1000,
        null=True,
        blank=True,
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        related_name='title',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='title',
    )

    def __str__(self):
        return self.name
