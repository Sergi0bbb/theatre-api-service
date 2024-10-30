from django.test import TestCase

from theatre.models import (
    Genre,
    Actor,
    Play,
    TheatreHall,
    Performance,
    Ticket,
    Reservation
)
from theatre.serializers import (
    GenreSerializer,
    ActorSerializer,
    PlaySerializer,
    TheatreHallSerializer,
    PerformanceSerializer,
    TicketSerializer,
    ReservationSerializer
)
from user.models import User


def sample_genre(name="Drama"):
    return Genre.objects.create(name=name)


def sample_actor(first_name="Test", last_name="Actor"):
    return Actor.objects.create(first_name=first_name, last_name=last_name)


def sample_play(
        title="TestPlay",
        description="Test description",
        duration=90,
        genre=None,
        actor=None
):
    play = Play.objects.create(
        title=title,
        description=description,
        duration=duration
    )
    if genre:
        play.genres.add(genre)
    if actor:
        play.actors.add(actor)
    return play


def sample_theatre_hall(name="Main Hall", rows=20, seats_in_row=30):
    return TheatreHall.objects.create(
        name=name,
        rows=rows,
        seats_in_row=seats_in_row
    )


def sample_performance(play, theatre_hall, show_time="2024-10-14T20:00:00Z"):
    return Performance.objects.create(
        play=play,
        theatre_hall=theatre_hall,
        show_time=show_time
    )


def sample_reservation(user):
    return Reservation.objects.create(user=user)


def sample_ticket(row=1, seat=1, performance=None, reservation=None):
    return Ticket.objects.create(
        row=row,
        seat=seat,
        performance=performance,
        reservation=reservation
    )


class GenreSerializerTest(TestCase):
    def setUp(self):
        self.genre = sample_genre()
        self.serializer = GenreSerializer(instance=self.genre)

    def test_serialized_data(self):
        data = self.serializer.data
        self.assertEqual(data["name"], "Drama")


class ActorSerializerTest(TestCase):
    def setUp(self):
        self.actor = sample_actor()
        self.serializer = ActorSerializer(instance=self.actor)

    def test_serialized_data(self):
        data = self.serializer.data
        self.assertEqual(data["first_name"], "Test")
        self.assertEqual(data["last_name"], "Actor")


class PlaySerializerTest(TestCase):
    def setUp(self):
        self.genre = sample_genre()
        self.actor = sample_actor()
        self.play = sample_play(genre=self.genre, actor=self.actor)
        self.serializer = PlaySerializer(instance=self.play)

    def test_serializer_data(self):
        data = self.serializer.data
        self.assertEqual(data["title"], "TestPlay")
        self.assertEqual(data["description"], "Test description")


class TheatreHallSerializerTest(TestCase):
    def setUp(self):
        self.theatre_hall = sample_theatre_hall()
        self.serializer = TheatreHallSerializer(instance=self.theatre_hall)

    def test_serializer_data(self):
        data = self.serializer.data
        self.assertEqual(data["name"], "Main Hall")
        self.assertEqual(data["rows"], 20)
        self.assertEqual(data["seats_in_row"], 30)


class PerformanceSerializerTest(TestCase):
    def setUp(self):
        self.genre = sample_genre()
        self.actor = sample_actor()
        self.play = sample_play(genre=self.genre, actor=self.actor)
        self.theatre_hall = sample_theatre_hall()
        self.performance = sample_performance(
            play=self.play,
            theatre_hall=self.theatre_hall
        )
        self.serializer = PerformanceSerializer(instance=self.performance)

    def test_serializer_data(self):
        data = self.serializer.data
        self.assertEqual(data["play"], self.performance.play.id)
        self.assertEqual(
            data["theatre_hall"],
            self.performance.theatre_hall.id
        )


class TicketSerializerTest(TestCase):
    def setUp(self):
        self.genre = sample_genre()
        self.actor = sample_actor()
        self.play = sample_play(genre=self.genre, actor=self.actor)
        self.theatre_hall = sample_theatre_hall()
        self.performance = sample_performance(
            play=self.play,
            theatre_hall=self.theatre_hall
        )
        self.user = User.objects.create_user(
            email="testu@u.com",
            password="password123"
        )
        self.reservation = sample_reservation(user=self.user)
        self.ticket = sample_ticket(
            performance=self.performance,
            reservation=self.reservation
        )
        self.serializer = TicketSerializer(instance=self.ticket)

    def test_serializer_data(self):
        data = self.serializer.data
        self.assertEqual(data["row"], 1)
        self.assertEqual(data["seat"], 1)


class ReservationSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testu@u.com",
            password="password123"
        )
        self.genre = sample_genre()
        self.play = sample_play(genre=self.genre)
        self.theatre_hall = sample_theatre_hall()
        self.performance = sample_performance(
            play=self.play,
            theatre_hall=self.theatre_hall
        )
        self.ticket_data = [{
            "row": 1,
            "seat": 1,
            "performance": self.performance.id
        }]
        self.serializer = ReservationSerializer(data={
            "user": self.user.id,
            "tickets": self.ticket_data
        })

    def test_create_reservation_with_tickets(self):
        self.serializer.is_valid(raise_exception=True)
        reservation = self.serializer.save()
        self.assertEqual(reservation.tickets.count(), 1)
