from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import UpdateView
from django.contrib import messages

# from botsite.forms import ChatConversationForm, ChatSettingForm
from botsite.models import UserProfile
# from vk.models import ChatConversation, ChatSetting
from vk.models import Chat, RandomPostSetting


def home(request):
    return render(request, "botsite/home.html")


@login_required
def profile(request):
    current_user = User.objects.get(username=request.user)
    idVK = UserProfile.objects.get(user_id=current_user.id).vk_id
    conversations = Chat.objects.filter(owner_id=idVK)
    context = {'conversations': conversations}
#TODO: делать запрос в контакт и получать имя чата
    # имя чата?
    return render(request, "botsite/profile.html", context)


def account_creation_info(request):
    return render(request, "botsite/account_creation_info.html")


def test(request):
    return render(request, "botsite/test.html")


# class ChatSettingUpdate(UpdateView):
#     model = ChatSetting
#     fields = ['random_post_group']
#     template_name = "botsite/random_post.html"

# def get_context_data(self, **kwargs):
#         context = super(TaffyUpdateView, self).get_context_data(**kwargs)
#         context['second_model'] = SecondModel.objects.get(id=1) #whatever you would like
#         return context

# def get_context_data(self, **kwargs):
#     context = super(ChatSettingUpdate, self).get_context_data(**kwargs)
#     # {'object': <ChatSetting: 2000000005>, 'chatsetting': <ChatSetting: 2000000005>,
#     # 'form': <ChatSettingForm bound=False, valid=Unknown, fields=(random_post_group)>, 'view': <botsite.views.ChatSettingUpdate object at 0x000002078FC7AE48>}
#     # print(self.kwargs['pk'])
#     chat_conversation_object = ChatConversation.objects.get(peer_id=self.kwargs['pk'])
#     context['chat_conversation'] = {'object': chat_conversation_object, 'form': ChatConversationForm}
#     print(context)
#     return context

# def get_success_url(self):
#     messages.add_message(self.request, messages.INFO, 'form submission success')
#     return self.request.path


# @login_required
# def random_post(request, conversation):
#     chat_setting_instance = get_object_or_404(RandomPostSetting, peer_id=conversation)
#     chat_conversation_instance = get_object_or_404(Chat, peer_id=conversation)
#
#     if request.method == 'POST':
#         chat_setting_form = ChatSettingForm(request.POST, instance=chat_setting_instance)
#         chat_conversation_form = ChatConversationForm(request.POST, instance=chat_conversation_instance)
#
#         if chat_setting_form.is_valid() and chat_conversation_form.is_valid():
#             print("in view:", chat_setting_form['random_post_group'].value())
#
#             chat_setting_form.save()
#             chat_conversation_form.save()
#
#             return redirect(request.path)
#         else:
#             context = {
#                 'chat_setting_form': chat_setting_form,
#                 'chat_conversation_form': chat_conversation_form,
#             }
#             return render(request, "botsite/random_post.html", context)
#
#
#
#     else:
#         chat_setting_instance = get_object_or_404(ChatSetting, peer_id=conversation)
#         chat_conversation_instance = get_object_or_404(ChatConversation, peer_id=conversation)
#
#         chat_setting_form = ChatSettingForm(instance=chat_setting_instance)
#         chat_conversation_form = ChatConversationForm(instance=chat_conversation_instance)
#
#         context = {
#             'chat_setting_form': chat_setting_form,
#             'chat_conversation_form': chat_conversation_form,
#         }
#
#         return render(request, "botsite/random_post.html", context)



@login_required
def conversation_settings(request, conversation):
    # check for user and conversation
    return render(request, "botsite/bot_settings.html")


def error_500(request, *args):
    return render(request, 'botsite/500.html', status=500)


def error_404(request, exception):
    return render(request, 'botsite/404.html', status=404)


