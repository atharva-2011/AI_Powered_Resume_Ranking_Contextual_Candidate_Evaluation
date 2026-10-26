from django.urls import path
from . import views

app_name = 'ranking'

urlpatterns = [
    path('', views.home, name='home'),
    path('api/analyze/', views.analyze_candidates_api, name='analyze_candidates'),
]
