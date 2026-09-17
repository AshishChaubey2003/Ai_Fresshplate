import logging

from django.conf import settings
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ChatMessage, ChatSession
from .serializers import ChatRequestSerializer
from .services import ChatbotSafetyBlocked, ChatbotUnavailable, generate_reply

logger = logging.getLogger(__name__)


class ChatView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatRequestSerializer

    def get_throttles(self):
        # Rate-limit sending messages (each one costs money); reading history is free
        self.throttle_scope = "chatbot" if self.request.method == "POST" else None
        return super().get_throttles()

    def get(self, request):
        session_id = request.query_params.get("session_id")

        if session_id:
            if not session_id.isdigit():
                return Response({"error": "Invalid session id"}, status=status.HTTP_400_BAD_REQUEST)
            # user=request.user means you can only open your own chats
            session = get_object_or_404(ChatSession, id=session_id, user=request.user)
            history = [
                {"role": m.role, "content": m.content, "created_at": m.created_at}
                for m in session.messages.all()
            ]
            return Response({"session_id": session.id, "title": session.title, "messages": history})

        sessions = ChatSession.objects.filter(user=request.user)[:50]
        return Response({
            "sessions": [
                {"id": s.id, "title": s.title or f"Chat #{s.id}", "created_at": s.created_at}
                for s in sessions
            ]
        })

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_message = serializer.validated_data["message"]
        session_id = serializer.validated_data.get("session_id")

        if session_id:
            # 404 instead of silently starting a new chat - the user thought
            # they were continuing an old conversation
            session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        else:
            session = ChatSession.objects.create(user=request.user, title=user_message[:60])

        ChatMessage.objects.create(session=session, role="user", content=user_message)

        # Send only the last N messages. Sending the whole thread meant a long
        # chat cost more on every single reply.
        recent = list(session.messages.order_by("-created_at")[: settings.CHATBOT_HISTORY_LIMIT])[::-1]
        history = [(m.role, m.content) for m in recent]
        # Gemini requires the conversation to start with a user turn
        while history and history[0][0] != "user":
            history.pop(0)

        try:
            reply = generate_reply(request.user, history)
        except ChatbotSafetyBlocked:
            reply = "Sorry, I can't help with that. Ask me about the menu, orders or donations."
        except ChatbotUnavailable:
            # Details go to the server log; the user gets a clean message
            return Response(
                {
                    "session_id": session.id,
                    "error": "The AI assistant is temporarily unavailable. Please try again later.",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        ChatMessage.objects.create(session=session, role="assistant", content=reply)
        session.save(update_fields=["updated_at"])  # bumps this chat to the top of the sidebar

        return Response({"session_id": session.id, "message": reply}, status=status.HTTP_200_OK)


class DeleteChatSessionView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={200: None})
    def delete(self, request, pk):
        session = get_object_or_404(ChatSession, id=pk, user=request.user)
        session.delete()
        return Response({"message": "Chat session deleted"})