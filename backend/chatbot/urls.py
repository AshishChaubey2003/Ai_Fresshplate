from django.urls import path

from . import views

urlpatterns = [
    # GET lists sessions or one session's messages, POST sends a message
    path("", views.ChatView.as_view(), name="chat"),
    path("session/<int:pk>/delete/", views.DeleteChatSessionView.as_view(), name="delete-session"),
]