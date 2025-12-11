from django.urls import path
from . import views

app_name = 'FeedApp'

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/', views.profile, name='profile'), # path for profile information
    path('myfeed', views.myfeed, name='myfeed'), # path for users/my feed
    path('new_post/', views.new_post, name='new_post'), # path for creating a new post
    path('friendsfeed/', views.friendsfeed, name='friendsfeed'), # path for friends feed
    path('comments/<int:post_id>/',views.comments, name='comments'), # path for comments on a post
    path('friends/', views.friends, name='friends'), # path for friends list
    ]

    