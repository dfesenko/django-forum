from django.urls import path

from . import views


app_name = 'discussions'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('users/<int:pk>/', views.DetailView.as_view(), name='detail'),
]