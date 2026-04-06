from django.urls import path
from . import views

urlpatterns = [
    path('', views.ChatView.as_view(), name='chat'),
    path('session/<int:pk>/delete/', views.DeleteChatSessionView.as_view(), name='delete-session'),
]