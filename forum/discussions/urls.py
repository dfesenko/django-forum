from django.urls import path

from . import views


app_name = 'discussions'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='detail'),
    path('signup/', views.UserSignupView.as_view(), name='signup'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('userpage/', views.UserPageView.as_view(), name='userpage'),
]