from django.urls import path
from . import views

app_name = 'FeedApp'

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/', views.profile, name='profile'), # path for profile information
    path('myfeed',views.myfeed, name='myfeed'), # path for users/my feed
    ]

    