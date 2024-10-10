from rest_framework import serializers

from theatre.models import Genre, Actor, Play, TheatreHall, Performance, Ticket


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id", "name")


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ("id", "first_name", "last_name")


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
        fields = ("id", "title", "genres", "actors")


class PlayDetailSerializer(PlaySerializer):
    genres = GenreSerializer(many=True, read_only=True)
    actors = ActorSerializer(many=True, read_only=True)

    class Meta:
        model = Play
        fields = (
            "id",
            "title",
            "description",
            "genres",
            "actors",
        )


class TheatreHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreHall
        fields = ("id", "name", "rows", "seats_in_row")


class PerformanceSerializer(serializers.ModelSerializer):
    plays = serializers.CharField(source="performance.play")
    theatre_halls = serializers.CharField(source="performance.theatre_hall")

    class Meta:
        model = Performance
        fields = ("id", "plays", "theatre_halls", "show_time")


class TicketSerializer(serializers.ModelSerializer):
    performance = serializers.CharField(source="ticket.performance")
    reservation = serializers.CharField(source="ticket.reservation")
    
    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "performance", "reservation"]

