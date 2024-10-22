from django.db.models import QuerySet, Count, F
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from theatre.models import (
    Genre,
    Actor,
    Play,
    TheatreHall,
    Performance,
    Reservation
)
from theatre.pagination import ReservationPagination
from theatre.serializers import (
    GenreSerializer,
    ActorSerializer,
    PlaySerializer,
    PlayListSerializer,
    PlayDetailSerializer,
    TheatreHallSerializer,
    PerformanceSerializer,
    PerformanceListSerializer,
    PerformanceDetailSerializer,
    ReservationListSerializer,
    ReservationSerializer,
    PlayImageSerializer
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
        elif self.action == "upload_image":
            return PlayImageSerializer
        return self.serializer_class

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        movie = self.get_object()
        serializer = self.get_serializer(movie, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "title",
                type=OpenApiTypes.STR,
                description="Filter by play title (ex. ?title=Hamlet)",
            ),
            OpenApiParameter(
                "genre",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by genre id (ex. ?genre=2,5)",
            ),
            OpenApiParameter(
                "actor",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by actor id (ex. ?actor=2,5)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class TheatreHallViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer


class PerformanceViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        Performance.objects.all()
        .select_related("play", "theatre_hall")
        .annotate(
            tickets_available=(
                    F("theatre_hall__rows") * F("theatre_hall__seats_in_row")
                    - Count("tickets")
            )
        )
    )
    serializer_class = PerformanceSerializer

    def get_queryset(self):
        play_id = self.request.query_params.get("play")
        theatre_hall_id = self.request.query_params.get("theatre_hall")
        show_time = self.request.query_params.get("show_time")

        queryset = self.queryset

        if play_id:
            queryset = queryset.filter(play_id=play_id)

        if theatre_hall_id:
            queryset = queryset.filter(theatre_hall_id=theatre_hall_id)

        if show_time:
            queryset = queryset.filter(show_time=show_time)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PerformanceListSerializer
        if self.action == "retrieve":
            return PerformanceDetailSerializer
        return self.serializer_class

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "play",
                type=OpenApiTypes.INT,
                description="Filter by play id (ex. ?play=1)",
            ),
            OpenApiParameter(
                "theatre_hall",
                type=OpenApiTypes.INT,
                description="Filter by theatre hall id (ex. ?theatre_hall=3)",
            ),
            OpenApiParameter(
                "show_time",
                type=OpenApiTypes.STR,
                description="Filter by show time "
                            "(ex. ?show_time=2024-10-20T18:00:00)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ReservationViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Reservation.objects.prefetch_related(
        "tickets__performance__play",
        "tickets__performance__theatre_hall"
    )
    pagination_class = ReservationPagination
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        return (
            Reservation
            .objects
            .filter(user=self.request.user)
            .prefetch_related(
                "tickets__performance__play",
                "tickets__performance__theatre_hall"
            )
        )

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
