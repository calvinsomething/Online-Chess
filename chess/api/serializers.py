from rest_framework import serializers
from .models import SavedGame, GameBoard


class SavedGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedGame
        fields = '__all__'


class GameBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameBoard
        fields = '__all__'