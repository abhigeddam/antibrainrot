from django.contrib import admin
from .models import UserProfile, PollResponse

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'chat_id')
    search_fields = ('user__username', 'chat_id')

@admin.register(PollResponse)
class PollResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'response', 'timestamp')
    search_fields = ('user__username', 'response')
