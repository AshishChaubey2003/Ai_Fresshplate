from django.contrib import admin

from .models import ChatMessage, ChatSession


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    # Chat history is a record - viewing is fine, editing is not
    readonly_fields = ("role", "content", "created_at")
    can_delete = False


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "message_count", "created_at", "updated_at")
    search_fields = ("user__email", "title")
    list_select_related = ("user",)
    readonly_fields = ("user", "created_at", "updated_at")
    inlines = [ChatMessageInline]
    list_per_page = 25

    @admin.display(description="Messages")
    def message_count(self, obj):
        return obj.messages.count()