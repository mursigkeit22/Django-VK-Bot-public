from django.contrib import admin


# Register your models here.
from .models import *


class IntervalPhraseAdmin(admin.ModelAdmin):
    readonly_fields = ['id']

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        fields = fields[-1:] + fields[:-1] # or something more robust
        return fields

    def display_id(self, obj):
        return obj.id


admin.site.register(IntervalPhrase, IntervalPhraseAdmin)
# admin.site.register(IntervalPhrase)
admin.site.register(ChatConversation)
admin.site.register(UserConversation)
admin.site.register(ChatMessage)
admin.site.register(UserMessage)
admin.site.register(ChatSetting)

