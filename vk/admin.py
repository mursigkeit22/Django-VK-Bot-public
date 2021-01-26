from django.contrib import admin

from .models import *


class ChatAdmin(admin.ModelAdmin):
    list_display = ("chat_id", 'title',)


class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("chat_id", 'text',)
    list_filter = ("chat_id",)


class UserMessageAdmin(admin.ModelAdmin):
    list_display = ("from_id", 'text',)
    list_filter = ("from_id",)


class IntervalPhraseAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat_id', 'phrase',)
    list_filter = ("chat_id",)  # TODO: добавить в ридонли chat_id?
    readonly_fields = ['id']

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        fields = fields[-1:] + fields[:-1]
        return fields

    def display_id(self, obj):
        return obj.id


class NewPostSettingAdmin(admin.ModelAdmin):
    list_display = ("chat_id", 'newpost_mode', 'newpost_group_link',)


class KickNonMembersSettingAdmin(admin.ModelAdmin):
    list_display = ("chat_id", 'kick_nonmembers_mode', 'kick_nonmembers_group_link',)


class RandomPostSettingAdmin(admin.ModelAdmin):
    list_display = ("chat_id", 'random_post_mode', 'random_post_group_link',)


admin.site.register(IntervalPhrase, IntervalPhraseAdmin)
admin.site.register(Chat, ChatAdmin)
admin.site.register(RandomPostSetting, RandomPostSettingAdmin)
admin.site.register(KickNonMembersSetting, KickNonMembersSettingAdmin)
admin.site.register(NewPostSetting, NewPostSettingAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)
admin.site.register(UserMessage, UserMessageAdmin)
