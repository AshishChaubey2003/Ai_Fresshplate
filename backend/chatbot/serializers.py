from django.conf import settings
from rest_framework import serializers


class ChatRequestSerializer(serializers.Serializer):
    """Validates a chat message before it costs us a Gemini call.

    max_length stops someone burning the API quota with a huge message.
    trim_whitespace turns "   " into "" so a blank message is rejected.
    """

    message = serializers.CharField(
        max_length=settings.CHATBOT_MAX_MESSAGE_LENGTH,
        trim_whitespace=True,
    )
    session_id = serializers.IntegerField(required=False, allow_null=True, min_value=1)