from django.db import models


class Director(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Actor(models.Model):
    actor_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Movie(models.Model):
    movie_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    release_date = models.DateField()
    actors = models.ManyToManyField(Actor, through='Cast')
    box_office_collection_in_crores = models.FloatField()
    director = models.ForeignKey(Director, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Cast(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)
    is_debut_movie = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.actor.name} as {self.role} in {self.movie.name}"


class Rating(models.Model):
    movie = models.OneToOneField(Movie, on_delete=models.CASCADE)
    rating_one_count = models.PositiveIntegerField(default=0)
    rating_two_count = models.PositiveIntegerField(default=0)
    rating_three_count = models.PositiveIntegerField(default=0)
    rating_four_count = models.PositiveIntegerField(default=0)
    rating_five_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Ratings for {self.movie.name}"
