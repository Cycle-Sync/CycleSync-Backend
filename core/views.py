# core/views.py
from datetime import date, timedelta
import math
from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Profile, DailyEntry, Cycle, Prediction, Condition, DemoRequest
from .serializers import ConditionSerializer
from calendar import monthrange
from datetime import date, timedelta
from .serializers import (
    UserSerializer,
    ProfileSerializer,
    DailyEntrySerializer,
    CycleSerializer,
    PredictionSerializer,
    DemoRequestSerializer
)
from django.core.cache import cache
from django.db.models import Avg

from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends SimpleJWT to include user info in the token response.
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        return {
            "tokens": {
                "refresh": data["refresh"],
                "access": data["access"],
            },
            "user": {
                "id": self.user.id,
                "username": self.user.username,
            },
        }

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["user_id"] = user.id
        return token


class MyTokenObtainPairView(TokenObtainPairView):
    """
    POST /api/auth/token/  -> { tokens: { refresh, access }, user: {...} }
    """
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(APIView):
    """
    POST /api/auth/register/
    {
      "username": "...",
      "password": "...",
      "date_of_birth": "YYYY-MM-DD",
      "country": "US",
      "last_ovulation": "YYYY-MM-DD",
      "cycle_type": "regular",
      "cycle_length": 28,
      "period_length": 5,
      "preferences": ["cycle", "symptoms"],
      "medical_conditions": [1,2,3]
    }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        username = data.get("username")
        password = data.get("password")

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already taken"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(username=username, password=password)
        profile = Profile.objects.create(
            user=user,
            date_of_birth=data.get("date_of_birth"),
            country=data.get("country"),
            last_ovulation=data.get("last_ovulation"),
            cycle_type=data.get("cycle_type", "unknown"),
            cycle_length=data.get("cycle_length"),
            period_length=data.get("period_length"),
            preferences=data.get("preferences", []),
        )
        if "medical_conditions" in data:
            profile.medical_conditions.set(data["medical_conditions"])

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class ProfileViewSet(viewsets.ModelViewSet):
    """
    /api/profiles/       [GET, POST]
    /api/profiles/{pk}/  [GET, PUT, PATCH, DELETE]
    /api/profiles/me/    [GET]  — current user's profile
    """
    queryset = Profile.objects.select_related("user").all()
    serializer_class = ProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        serializer = self.get_serializer(request.user.profile)
        return Response(serializer.data)


class DailyEntryViewSet(viewsets.ModelViewSet):
    """
    /api/daily-entries/       [GET, POST]
    /api/daily-entries/{pk}/  [GET, PUT, PATCH, DELETE]
    """
    serializer_class = DailyEntrySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DailyEntry.objects.filter(profile=self.request.user.profile)

    def perform_create(self, serializer):
        date = serializer.validated_data['date']
        cycle = Cycle.objects.filter(user=self.request.user, start_date__lte=date, end_date__gte=date).first()
        serializer.save(profile=self.request.user.profile, cycle=cycle)


class CycleViewSet(viewsets.ModelViewSet):
    """
    /api/cycles/       [GET, POST]
    /api/cycles/{pk}/  [GET, PUT, PATCH, DELETE]
    """
    serializer_class = CycleSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    #pagination_class = StandardResultsSetPagination  

    def get_queryset(self):
        return Cycle.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PredictionViewSet(viewsets.ModelViewSet):
    """
    /api/predictions/       [GET, POST]
    /api/predictions/{pk}/  [GET, PUT, PATCH, DELETE]
    """
    serializer_class = PredictionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Prediction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CalendarView(APIView):
    """
    GET /api/calendar/
    Returns a list of days in the current cycle with phases, angles, and flags.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        last_end = profile.last_ovulation
        cycle_len = profile.cycle_length
        period_len = profile.period_length
        today = date.today()

        days_since = (today - last_end).days
        cycle_index = max(0, days_since // cycle_len)
        cycle_start = last_end + timedelta(days=cycle_index * cycle_len)

        days_list = []
        ov_offset = cycle_len // 2
        prev_month = None

        for offset in range(cycle_len):
            d = cycle_start + timedelta(days=offset)
            is_new_month = (d.month != prev_month)
            prev_month = d.month
            angle = (360.0 / cycle_len) * offset

            if offset < period_len:
                phase = "menstrual"
            elif offset < ov_offset - 5:
                phase = "follicular"
            elif offset < ov_offset:
                phase = "fertile"
            elif offset == ov_offset:
                phase = "ovulation"
            else:
                phase = "luteal"

            days_list.append({
                "date": d.isoformat(),
                "day_num": offset + 1,
                "phase": phase,
                "is_past": d < today,
                "is_today": d == today,
                "new_month": is_new_month,
                "angle": angle,
            })

        return Response({"days_list": days_list})


class DashboardView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cycle_length = request.user.profile.cycle_length or 28
        days = list(range(1, cycle_length + 1))
        fsh = [5 + 2 * math.exp(-((d - 1) / 5) ** 2) for d in days]
        lh = [1 + 10 * math.exp(-((d - cycle_length // 2) / 1.5) ** 2) for d in days]
        estradiol = [5 + 8 * math.exp(-((d - cycle_length // 2 - 2) / 3) ** 2) for d in days]
        progesterone = [1 + 5 * math.exp(-((d - cycle_length // 2 + 7) / 3) ** 2) for d in days]
        return Response({"days": days, "fsh": fsh, "lh": lh, "estradiol": estradiol, "progesterone": progesterone})
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /api/users/       [GET]
    /api/users/{pk}/  [GET]
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return User.objects.all().order_by('username')

#for fetching conditions registered in the Condition model
class ConditionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /api/conditions/       [GET]
    /api/conditions/{pk}/  [GET]
    """
    queryset = Condition.objects.all()
    serializer_class = ConditionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Condition.objects.all().order_by('name')


class DashboardMetricsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        metrics = self.get_dashboard_metrics(user_id)
        return Response(metrics)

    def get_dashboard_metrics(self, user_id):
        cache_key = f"dashboard_metrics_{user_id}"
        metrics = cache.get(cache_key)  # Check cache first
        if metrics is None:
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

            metrics = {
                "average_cycle_length": round(avg_cycle_length, 1),
                "symptom_frequency": symptom_frequency,
                "prediction_accuracy": round(prediction_accuracy, 1) if prediction_accuracy else None,
                "hormone_stability": hormone_stability,
            }
            cache.set(cache_key, metrics, timeout=60 * 15)  # Cache for 15 minutes
        return metrics
# from .tasks import get_dashboard_metrics

# class DashboardMetricsView(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request):
#         user_id = request.user.id
#         result = get_dashboard_metrics.delay(user_id)  # Run task asynchronously
#         metrics = result.get(timeout=10)  # Wait up to 10 seconds for result
#         return Response(metrics)
        
# class DashboardMetricsView(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request):
#         profile = request.user.profile
#         cycles = Cycle.objects.filter(user=request.user)
#         daily_entries = DailyEntry.objects.filter(profile=profile)
#         predictions = Prediction.objects.filter(user=request.user).order_by('-prediction_date')[:5]

#         # Average cycle length
#         avg_cycle_length = cycles.aggregate(models.Avg('cycle_length'))['cycle_length__avg'] or profile.cycle_length or 28

#         # Symptom frequency (e.g., days with cramps)
#         symptom_frequency = daily_entries.filter(cramps__gt=0).count()

#         # Prediction accuracy (average days off)
#         accuracies = [p.accuracy() for p in predictions if p.accuracy() is not None]
#         prediction_accuracy = sum(accuracies) / len(accuracies) if accuracies else None

#         # Hormone stability (placeholder until real data exists)
#         hormone_stability = "N/A"

#         return Response({
#             "average_cycle_length": round(avg_cycle_length, 1),
#             "symptom_frequency": symptom_frequency,
#             "prediction_accuracy": round(prediction_accuracy, 1) if prediction_accuracy else None,
#             "hormone_stability": hormone_stability,
#         })


class CycleCalendarDataView(APIView):
    """
    GET /api/cycle-calendar/<year>/<month>/
    Returns a list of days in the specified month with cycle phases and flags.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, year, month):
        profile = request.user.profile
        cycle_len = profile.cycle_length or 28
        period_len = profile.period_length or 5

        # Get the number of days in the specified month
        _, num_days = monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, num_days)

        # Fetch cycles overlapping with this month
        cycles = Cycle.objects.filter(
            user=request.user,
            start_date__lte=end_date,
            end_date__gte=start_date
        ).order_by('start_date')

        days_list = []
        for d in (start_date + timedelta(n) for n in range(num_days)):
            # Check if the day is in a recorded cycle
            cycle = next((c for c in cycles if c.start_date <= d <= c.end_date), None)
            if cycle:
                offset = (d - cycle.start_date).days
                if offset < period_len:
                    phase = "menstrual"
                elif offset < cycle.cycle_length // 2 - 5:
                    phase = "follicular"
                elif offset < cycle.cycle_length // 2:
                    phase = "fertile"
                elif offset == cycle.cycle_length // 2:
                    phase = "ovulation"
                else:
                    phase = "luteal"
            else:
                # Fallback to profile-based calculation
                last_ovulation = profile.last_ovulation
                if last_ovulation:
                    days_since_last_ov = (d - last_ovulation).days
                    cycle_index = days_since_last_ov // cycle_len
                    cycle_start = last_ovulation + timedelta(days=cycle_index * cycle_len)
                    offset = (d - cycle_start).days
                    if 0 <= offset < cycle_len:
                        if offset < period_len:
                            phase = "menstrual"
                        elif offset < cycle_len // 2 - 5:
                            phase = "follicular"
                        elif offset < cycle_len // 2:
                            phase = "fertile"
                        elif offset == cycle_len // 2:
                            phase = "ovulation"
                        else:
                            phase = "luteal"
                    else:
                        phase = "unknown"
                else:
                    phase = "unknown"

            days_list.append({
                "date": d.isoformat(),
                "phase": phase,
                "is_today": d == date.today(),
                "is_past": d < date.today(),
            })

        return Response({"days_list": days_list})

#demo
class DemoRequestCreateAPIView(generics.CreateAPIView):
    queryset         = DemoRequest.objects.all()
    serializer_class = DemoRequestSerializer
    permission_classes = [permissions.AllowAny]