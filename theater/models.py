from django.conf import settings
from django.db import models


class Genre(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class Actor(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Play(models.Model):
    title = models.CharField(max_length=150, unique=True)
    description = models.TextField()
    genres = models.ManyToManyField(Genre, related_name="plays", blank=True)
    actors = models.ManyToManyField(Actor, related_name="plays", blank=True)

    def __str__(self) -> str:
        return self.title


class TheatreHall(models.Model):
    name = models.CharField(max_length=150, unique=True)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()

    def __str__(self) -> str:
        return self.name


class Performance(models.Model):
    play = models.ForeignKey(
        Play,
        related_name="performances",
        on_delete=models.CASCADE
    )
    theatre_hall = models.ForeignKey(
        TheatreHall,
        related_name="performances",
        on_delete=models.CASCADE
    )
    show_time = models.DateTimeField()

    def __str__(self) -> str:
        return f"{self.play.title} at {self.show_time}"


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"Reservation by {self.user.username} on {self.created_at}"


class Ticket(models.Model):
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    performance = models.ForeignKey(
        Performance,
        related_name="tickets",
        on_delete=models.CASCADE
    )
    reservation = models.ForeignKey(
        Reservation,
        related_name="tickets",
        on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"{self.performance} (Row {self.row}, Seat {self.seat})"
