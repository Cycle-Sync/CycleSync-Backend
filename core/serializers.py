from rest_framework import serializers
from .models import Profile, Condition, Cycle, DailyEntry, Prediction, DemoRequest
from django.contrib.auth.models import User
from django_countries.serializers import CountryFieldMixin

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condition
        fields = ['id', 'name']

class ProfileSerializer(CountryFieldMixin, serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    medical_conditions = ConditionSerializer(many=True, read_only=True)
    medical_condition_ids = serializers.PrimaryKeyRelatedField(
        queryset=Condition.objects.all(), many=True, write_only=True, source='medical_conditions'
    )

    class Meta:
        model = Profile
        fields = [
            'id', 'user', 'date_of_birth', 'country', 'medical_conditions', 'medical_condition_ids',
            'last_ovulation', 'cycle_type', 'cycle_length', 'period_length', 'preferences',
            'profile_image'
        ]

    def update(self, instance, validated_data):
        medical_condition_ids = validated_data.pop('medical_conditions', None)
        instance = super().update(instance, validated_data)
        if medical_condition_ids is not None:
            instance.medical_conditions.set(medical_condition_ids)
        return instance

class CycleSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Cycle
        fields = [
            'id', 'user', 'start_date', 'end_date', 'predicted_next_start', 'cycle_length',
            'average_symptoms', 'phase', 'last_updated', 'needs_review'
        ]

class DailyEntrySerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    cycle = CycleSerializer(read_only=True)
    class Meta:
        model = DailyEntry
        fields = [
            'id', 'profile', 'date', 'cramps', 'cycle', 'bloating', 'tender_breasts', 'headache', 'acne',
            'mood', 'stress', 'energy', 'cervical_mucus', 'sleep_quality', 'libido', 'notes'
        ]

class PredictionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Prediction
        fields = ['id', 'user', 'prediction_date', 'predicted_start', 'confidence', 'actual_start']

#demo
class DemoRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DemoRequest
        fields = [
            "id",  "email", "datetime", "message", "created_at"
        ]
        read_only_fields = ["id", "created_at"]