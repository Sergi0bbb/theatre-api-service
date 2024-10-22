from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import (
    Genre,
    Actor,
    Play,
    TheatreHall,
    Performance,
    Reservation
)
from theatre.serializers import (
    GenreSerializer,
    ActorSerializer,
    PlayListSerializer,
    TheatreHallSerializer
)

User = get_user_model()


def sample_user(email="testu@u.com", password="password123"):
    user = User.objects.create_user(email=email, password=password)
    return user


def sample_admin_user(email="adminu@u.com", password="password123"):
    return User.objects.create_superuser(email=email, password=password)


def sample_genre(name="Drama"):
    return Genre.objects.create(name=name)


def sample_actor(first_name="Test", last_name="Actor"):
    return Actor.objects.create(first_name=first_name, last_name=last_name)


def sample_play(title="TestPlay", **params):
    return Play.objects.create(title=title, **params)


def sample_theatre_hall(name="Main Hall", rows=10, seats_in_row=10):
    return TheatreHall.objects.create(
        name=name,
        rows=rows,
        seats_in_row=seats_in_row
    )


def sample_performance(play, theatre_hall, show_time=None):
    return Performance.objects.create(
        play=play,
        theatre_hall=theatre_hall,
        show_time=show_time
    )


def sample_reservation(user):
    return Reservation.objects.create(user=user)


class GenreViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_admin_user()
        self.client.force_authenticate(user=self.user)

    def test_list_genres(self):
        sample_genre(name="Comedy")
        sample_genre(name="Tragedy")

        res = self.client.get(reverse("theatre:genre-list"))

        genres = Genre.objects.all().order_by("name")
        serializer = GenreSerializer(genres, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_genre(self):
        payload = {"name": "Musical"}
        res = self.client.post(reverse("theatre:genre-list"), payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)


class ActorViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_admin_user()
        self.client.force_authenticate(self.user)
        self.url = reverse("theatre:actor-list")

    def test_create_actor(self):
        payload = {
            "first_name": "Test",
            "last_name": "Actor"
        }
        res = self.client.post(self.url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["first_name"], payload["first_name"])
        self.assertEqual(res.data["last_name"], payload["last_name"])

    def test_list_actors(self):
        sample_actor(first_name="Test", last_name="Actor")
        sample_actor(first_name="Test2", last_name="Actor2")

        res = self.client.get(self.url)

        actors = Actor.objects.all().order_by("first_name")
        serializer = ActorSerializer(actors, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class PlayViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_admin_user()
        self.client.force_authenticate(self.user)

    def test_list_plays(self):
        genre = sample_genre()
        actor = sample_actor()
        sample_play(title="Play 1").genres.add(genre)
        sample_play(title="Play 2").actors.add(actor)

        res = self.client.get(reverse("theatre:play-list"))

        plays = Play.objects.all().order_by("title")
        serializer = PlayListSerializer(plays, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_play_as_non_admin(self):
        payload = {"title": "New Play", "description": "New Description"}
        res = self.client.post(reverse("theatre:play-list"), payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)


class TheatreHallViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_admin_user()
        self.client.force_authenticate(self.user)

    def test_list_theatre_halls(self):
        sample_theatre_hall(name="Main Hall")
        sample_theatre_hall(name="Secondary Hall")

        res = self.client.get(reverse("theatre:theatre_hall-list"))

        halls = TheatreHall.objects.all().order_by("name")
        serializer = TheatreHallSerializer(halls, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_theatre_hall(self):
        payload = {
            "name": "New Hall",
            "rows": 5,
            "seats_in_row": 20
        }
        res = self.client.post(reverse("theatre:theatre_hall-list"), payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)


class PerformanceViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_admin_user()
        self.client.force_authenticate(self.user)

    def test_create_performance(self):
        play = sample_play(title="Play 1")
        theatre_hall = sample_theatre_hall()

        payload = {
            "play": play.id,
            "theatre_hall": theatre_hall.id,
            "show_time": datetime.now()
        }

        res = self.client.post(reverse("theatre:performance-list"), payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
