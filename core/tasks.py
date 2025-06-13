# tasks for celery
from celery import shared_task
from django.contrib.auth.models import User
from .models import Profile, Cycle, DailyEntry, Prediction
from django.db.models import Avg

@shared_task
def get_dashboard_metrics(user_id):
    user = User.objects.get(id=user_id)
    profile = Profile.objects.get(user=user)
    cycles = Cycle.objects.filter(user=user)
    daily_entries = DailyEntry.objects.filter(profile=profile)
    predictions = Prediction.objects.filter(user=user).order_by('-prediction_date')[:5]

    avg_cycle_length = cycles.aggregate(Avg('cycle_length'))['cycle_length__avg'] or profile.cycle_length or 28
    symptom_frequency = daily_entries.filter(cramps__gt=0).count()
    accuracies = [p.accuracy() for p in predictions if p.accuracy() is not None]
    prediction_accuracy = sum(accuracies) / len(accuracies) if accuracies else None
    hormone_stability = "N/A"

    return {
        "average_cycle_length": round(avg_cycle_length, 1),
        "symptom_frequency": symptom_frequency,
        "prediction_accuracy": round(prediction_accuracy, 1) if prediction_accuracy else None,
        "hormone_stability": hormone_stability,
    }