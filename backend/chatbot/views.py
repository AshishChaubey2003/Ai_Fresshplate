from google import genai
from google.genai import types
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import ChatSession, ChatMessage

client = genai.Client(api_key=settings.GEMINI_API_KEY)

class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        session_id = request.query_params.get('session_id')
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id, user=request.user)
                messages = session.messages.all().order_by('created_at')
                history = [{'role': m.role, 'content': m.content} for m in messages]
                return Response({'session_id': session.id, 'messages': history})
            except ChatSession.DoesNotExist:
                return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

        sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')
        return Response({'sessions': [{'id': s.id, 'created_at': s.created_at} for s in sessions]})

    def post(self, request):
        user_message = request.data.get('message', '').strip()
        session_id = request.data.get('session_id')

        if not user_message:
            return Response({'error': 'Message cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)

        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id, user=request.user)
            except ChatSession.DoesNotExist:
                session = ChatSession.objects.create(user=request.user)
        else:
            session = ChatSession.objects.create(user=request.user)

        ChatMessage.objects.create(session=session, role='user', content=user_message)

        history = session.messages.all().order_by('created_at')

        try:
            chat_history = []
            for m in history:
                if m.role == 'user':
                    chat_history.append(types.Content(role='user', parts=[types.Part(text=m.content)]))
                elif m.role == 'assistant':
                    chat_history.append(types.Content(role='model', parts=[types.Part(text=m.content)]))

            system_prompt = """You are FreshPlate AI Assistant — a helpful, friendly chatbot for FreshPlate,
            a Cloud Kitchen and Food Rescue Platform. You help users with:
            - Browsing food menu and placing orders
            - Tracking order status
            - Food donation process
            - Account and profile management
            - General food and nutrition queries
            Always be polite, helpful and respond in the same language the user uses."""

            response = client.models.generate_content(
                model='gemini-1.5-flash',
                config=types.GenerateContentConfig(system_instruction=system_prompt),
                contents=chat_history,
            )

            assistant_message = response.text
            ChatMessage.objects.create(session=session, role='assistant', content=assistant_message)

            return Response({
                'session_id': session.id,
                'message': assistant_message
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"CHATBOT ERROR: {str(e)}")  
            return Response({'error': f'AI service error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteChatSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            session = ChatSession.objects.get(id=pk, user=request.user)
            session.delete()
            return Response({'message': 'Chat session deleted'})
        except ChatSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)