from django.contrib import admin
from .models import TelegramUser, PollResponse

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'chat_id', 'created_at')
    search_fields = ('user__username', 'chat_id')

@admin.register(PollResponse)
class PollResponseAdmin(admin.ModelAdmin):
    list_display = ('telegram_user', 'activity', 'timestamp')
    list_filter = ('activity', 'timestamp')
    search_fields = ('telegram_user__user__username',)
