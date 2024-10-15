from django.test import TestCase

from theatre.models import (
    Genre,
    Actor,
    Play,
    TheatreHall,
    Performance,
    Reservation,
    Ticket
)
from user.models import User


def sample_genre(name="Drama"):
    return Genre.objects.create(name=name)


def sample_actor(first_name="Test", last_name="Actor"):
    return Actor.objects.create(first_name=first_name, last_name=last_name)


def sample_play(title="TestPlay", description="Test description", duration=90):
    return Play.objects.create(
        title=title,
        description=description,
        duration=duration
    )


def sample_theatre_hall(name="Main Hall", rows=20, seats_in_row=30):
    return TheatreHall.objects.create(
        name=name,
        rows=rows,
        seats_in_row=seats_in_row
    )


def sample_performance(
        play=None,
        theatre_hall=None,
        show_time="2024-10-10T18:00:00Z"
):
    play = play or sample_play()
    theatre_hall = theatre_hall or sample_theatre_hall()
    return Performance.objects.create(
        play=play,
        theatre_hall=theatre_hall,
        show_time=show_time
    )


def sample_user(email="testu@u.com", password="password123"):
    return User.objects.create_user(email=email, password=password)


def sample_reservation(user):
    return Reservation.objects.create(user=user)


def sample_ticket(row=1, seat=1, performance=None, reservation=None):
    performance = performance or sample_performance()
    reservation = reservation or sample_reservation(sample_user())
    return Ticket.objects.create(
        row=row,
        seat=seat,
        performance=performance,
        reservation=reservation
    )


class GenreTest(TestCase):
    def setUp(self):
        self.genre = sample_genre()

    def test_str_method(self):
        self.assertEqual(str(self.genre), "Drama")


class ActorTest(TestCase):
    def setUp(self):
        self.actor = sample_actor()

    def test_str_method(self):
        self.assertEqual(str(self.actor), "Test Actor")

    def test_full_name_property(self):
        self.assertEqual(self.actor.full_name, "Test Actor")


class PlayTest(TestCase):
    def setUp(self):
        self.play = sample_play()

    def test_str_method(self):
        self.assertEqual(str(self.play), "TestPlay")


class TheatreHallTest(TestCase):
    def setUp(self):
        self.theatre_hall = sample_theatre_hall()

    def test_str_method(self):
        self.assertEqual(str(self.theatre_hall), "Main Hall")

    def test_capacity_property(self):
        self.assertEqual(self.theatre_hall.capacity, 600)


class PerformanceTest(TestCase):
    def setUp(self):
        self.performance = sample_performance()

    def test_str_method(self):
        self.assertEqual(
            str(self.performance),
            "TestPlay at 2024-10-10T18:00:00Z"
        )


class TicketTest(TestCase):
    def setUp(self):
        self.ticket = sample_ticket()

    def test_str_method(self):
        self.assertEqual(
            str(self.ticket),
            "TestPlay at 2024-10-10T18:00:00Z (Row 1, Seat 1)"
        )
