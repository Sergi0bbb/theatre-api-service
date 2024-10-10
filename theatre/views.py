from datetime import datetime

from rest_framework import mixins, viewsets
from rest_framework.viewsets import GenericViewSet

from theatre.models import Genre, Actor, Play, TheatreHall
from theatre.serealizers import (
    GenreSerializer,
    ActorSerializer,
    PlaySerializer,
    PlayListSerializer,
    PlayDetailSerializer, TheatreHallSerializer
)


class GenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class ActorViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


class PlayViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Play.objects.prefetch_related("genres", "actors")
    serializer_class = PlaySerializer

    @staticmethod
    def _params_to_ints(qs):
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "list":
            title = self.request.query_params.get("title")
            genre_id = self.request.query_params.get("genre")
            actor_id = self.request.query_params.get("actor")
            if title:
                queryset = queryset.filter(title__icontains=title)
            if genre_id:
                queryset = queryset.filter(genres__id=genre_id)
            if actor_id:
                queryset = queryset.filter(actors__id=actor_id)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer
        elif self.action == "retrieve":
            return PlayDetailSerializer
        return PlaySerializer


class TheatreHallViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer


