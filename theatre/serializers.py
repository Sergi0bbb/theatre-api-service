from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from theatre.models import (
    Genre,
    Actor,
    Play,
    TheatreHall,
    Performance,
    Ticket,
    Reservation
)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id", "name")


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ("id", "first_name", "last_name")


class PlayImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = ("id", "image")


class PlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = ("id", "title", "description", "genres", "actors")


class PlayListSerializer(PlaySerializer):
    genres = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name"
    )
    actors = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="full_name"

    )

    class Meta:
        model = Play
        fields = ("id", "title", "image", "genres", "actors")


class PlayDetailSerializer(PlaySerializer):
    genres = GenreSerializer(many=True, read_only=True)
    actors = ActorSerializer(many=True, read_only=True)

    class Meta:
        model = Play
        fields = (
            "id",
            "title",
            "description",
            "duration",
            "image",
            "genres",
            "actors",
        )


class TheatreHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreHall
        fields = ("id", "name", "rows", "seats_in_row")


class PerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Performance
        fields = ("id", "play", "theatre_hall", "show_time")


class PerformanceListSerializer(PerformanceSerializer):
    play_title = serializers.CharField(source="play.title")
    theatre_hall_name = serializers.CharField(source="theatre_hall.name")
    play_image = serializers.ImageField(source="play.image", read_only=True)
    theatre_hall_capacity = serializers.IntegerField(
        source="theatre_hall.capacity", read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Performance
        fields = (
            "id",
            "play_title",
            "theatre_hall_name",
            "show_time",
            "play_image",
            "theatre_hall_capacity",
            "tickets_available"
        )


class PerformanceDetailSerializer(PerformanceSerializer):
    play = PlayListSerializer(read_only=True)
    theatre_hall = TheatreHallSerializer(read_only=True)
    taken_places = serializers.SerializerMethodField()

    class Meta:
        model = Performance
        fields = (
            "id",
            "show_time",
            "play",
            "theatre_hall",
            "taken_places"
        )

    def get_taken_places(self, obj):
        tickets = Ticket.objects.filter(performance=obj)
        return TicketSeatsSerializer(tickets, many=True).data


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["performance"].theatre_hall,
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "performance")


class TicketListSerializer(TicketSerializer):
    performance = PerformanceListSerializer(read_only=True)


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True)

    class Meta:
        model = Reservation
        fields = ("id", "created_at", "tickets", "user")

    def create(self, validated_data: dict):
        with transaction.atomic():

            tickets_data = validated_data.pop("tickets")
            reservation = Reservation.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(reservation=reservation, **ticket_data)
        return reservation


class ReservationListSerializer(ReservationSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
