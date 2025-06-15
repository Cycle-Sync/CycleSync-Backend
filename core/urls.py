from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *
router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'daily-entries', DailyEntryViewSet, basename='dailyentry')
router.register(r'cycles', CycleViewSet, basename='cycle')
router.register(r'predictions', PredictionViewSet, basename='prediction')
router.register(r'users', UserViewSet)
#condition viewset
router.register(r'conditions', ConditionViewSet, basename='condition')
urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/token/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('dashboard-metrics/', DashboardMetricsView.as_view(), name='dashboard-metrics'),
    path('cycle-calendar/<int:year>/<int:month>/', CycleCalendarDataView.as_view(), name='cycle-calendar'),

    # custom endpoints
    path("book-demo/", DemoRequestCreateAPIView.as_view(), name="book-demo"),
    path('calendar/', CalendarView.as_view(), name='calendar'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
