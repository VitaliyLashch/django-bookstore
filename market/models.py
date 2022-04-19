from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Author(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name


class ActivationLink(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    link = models.CharField(max_length=36)

    def __str__(self):
        return str(self.user) + ":" + self.link

class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    book = models.ForeignKey(
        "Book",
        on_delete=models.CASCADE,
        related_name="comments"
    )
    score = models.PositiveSmallIntegerField(
        choices=(
            (1, "★☆☆☆☆"),
            (2, "★★☆☆☆"),
            (3, "★★★☆☆"),
            (4, "★★★★☆"),
            (5, "★★★★★"),
        )
    )
    title = models.CharField(max_length=180)
    content = models.CharField(max_length=900)
    timestamp = models.DateField(auto_now_add=True)

    def __str__(self):
        return ", ".join((str(self.author), str(self.book)))

    class Meta:
        ordering = ["-timestamp"]
        unique_together = ("author", "book",)


class Book(models.Model):
    title = models.CharField(max_length=180)
    authors = models.ManyToManyField("Author", related_name="books")
    categories = models.ManyToManyField("Category", related_name="books")
    cover = models.ImageField(upload_to="covers")
    price = models.PositiveIntegerField()
    printed_year = models.PositiveSmallIntegerField()
    holders = models.ManyToManyField(
        User,
        related_name="books",
        blank=True,
        editable=False
    )
    holders_count = models.PositiveIntegerField(default=0, editable=False)
    shoppers = models.ManyToManyField(
        User,
        related_name="shopping_cart",
        blank=True,
        editable=False
    )
    score = models.FloatField(default=0, editable=False)

    def __str__(self):
        authors = ", ".join([str(author) for author in self.authors.all()])
        return ", ".join((
            self.title,
            authors,
            str(self.printed_year)
        ))
