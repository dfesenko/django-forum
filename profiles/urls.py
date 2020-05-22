from django.urls import path

from . import views


app_name = 'profiles'
urlpatterns = [
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_details'),
    path('users/<int:pk>/forum-activity/', views.UserActivityView.as_view(), name='user_forum_activity'),
    path('users/profile/edit', views.UserPageEditView.as_view(), name='edit_profile'),
    path('userpage/', views.UserPageView.as_view(), name='userpage'),
]