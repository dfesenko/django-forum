from django.urls import path
from django.urls import reverse_lazy

from . import views
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView, \
    PasswordResetDoneView, PasswordResetCompleteView

app_name = 'discussions'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='detail'),
    path('signup/', views.UserSignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password_reset/', PasswordResetView.as_view(
                                    success_url=reverse_lazy('discussions:password_reset_done')),
         name='password_reset'),
    path('password_reset_done/', views.UserPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
                                                    success_url=reverse_lazy('discussions:password_reset_complete')),
         name='password_reset_confirm'),
    path('password_reset_complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('users/edit_profile/', views.UserPageEditView.as_view(), name='edit_profile'),
    path('userpage/', views.UserPageView.as_view(), name='userpage'),
]
