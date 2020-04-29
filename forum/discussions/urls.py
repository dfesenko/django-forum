from django.urls import path
from django.urls import reverse_lazy

from . import views
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView, \
    PasswordResetCompleteView, PasswordChangeView

app_name = 'discussions'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_details'),
    path('users/<int:pk>/forum-activity/', views.UserActivityView.as_view(), name='user_forum_activity'),
    path('signup/', views.UserSignupView.as_view(), name='signup'),
    path('email-confirm/', views.EmailConfirmView.as_view(), name='email_confirm'),
    path('account-activation/<uidb64>/<token>/', views.UserActivationView.as_view(), name='activation'),

    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-reset/', PasswordResetView.as_view(
                                    success_url=reverse_lazy('discussions:password_reset_done')),
         name='password_reset'),
    path('password-reset-done/', views.UserPasswordResetDoneView.as_view(), name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
                                                    success_url=reverse_lazy('discussions:password_reset_complete')),
         name='password_reset_confirm'),
    path('password-reset-complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('password-change/', PasswordChangeView.as_view(
                                    success_url=reverse_lazy('discussions:password_change_done')),
         name='password_change'),
    path('password-change-done/', views.UserPasswordChangeDoneView.as_view(), name='password_change_done'),

    path('users/profile/edit', views.UserPageEditView.as_view(), name='edit_profile'),
    path('userpage/', views.UserPageView.as_view(), name='userpage'),
    path('forums/', views.ForumView.as_view(), name='forum'),
    path('forums/topics/new/', views.CreateTopicView.as_view(), name='new_topic'),
    path('forums/<int:category_id>/', views.CategoryView.as_view(), name='category'),
    path('forums/topics/<int:topic_id>/', views.TopicView.as_view(), name='topic'),
    path('post/vote/<int:post_id>/<slug:direction>/', views.VotePostView.as_view(), name='vote_post'),
]
