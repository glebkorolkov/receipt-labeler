from django.urls import path

from . import views

app_name = 'labeler'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:receipt_id>/', views.receipt_view, name='receipt'),
]