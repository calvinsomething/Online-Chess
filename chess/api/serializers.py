from rest_framework import serializers
from .models import GameBoard


class GameBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameBoard
        fields = '__all__'