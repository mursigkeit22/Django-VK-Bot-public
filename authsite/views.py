import os

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from oauthlib.oauth2 import AccessDeniedError
from requests_oauthlib import OAuth2Session

from authsite.utils import get_user_data
from botsite.models import UserProfile
from web_vk.constants import VK_AUTH_SECRET, VK_REDIRECT_URI, VK_AUTHORIZATION_URL, VK_ACCESS_TOKEN_URL, VK_AUTH_ID



def vk_auth(request):
    """oauth = OAuth2Session(VK_AUTH_ID, redirect_uri=VK_REDIRECT_URI, scope=['photos', 'audio', 'stories'])
    из документации:
    scope = offline
    Полученный таким образом токен перестанет действовать только при смене пользователем пароля, завершении всех сеансов или удалении приложения."""
    try:
        oauth = OAuth2Session(VK_AUTH_ID, redirect_uri=VK_REDIRECT_URI, scope=['offline', ])
        authorization_url, state = oauth.authorization_url(VK_AUTHORIZATION_URL)
        request.session['oauth_state'] = state
        return redirect(authorization_url)
    except Exception as e:
        print("vkauth exception")
        print(e)


def vk_auth_callback(request):
    try:
        oauth = OAuth2Session(client_id=VK_AUTH_ID,
                              redirect_uri=VK_REDIRECT_URI,
                              state=request.session['oauth_state'])
        token_data = oauth.fetch_token(VK_ACCESS_TOKEN_URL,
                                       client_secret=VK_AUTH_SECRET, include_client_id=True,
                                       authorization_response=request.build_absolute_uri())
        vk_user_id = token_data['user_id']
        print(token_data)
    except AccessDeniedError as e:
        return redirect('access_denied')

    try:
        profile = UserProfile.objects.get(vk_id=vk_user_id)
        user = profile.user
        profile.vk_token = token_data['access_token']
        profile.save()
        login(request, user)

    except UserProfile.DoesNotExist as e:
        user_data = get_user_data(token_data.get('access_token'))
        user = User.objects.create_user(user_data['screen_name'], first_name=user_data['first_name'],
                                        last_name=user_data['last_name'])
        profile = UserProfile(user=user, vk_id=vk_user_id, vk_token=token_data['access_token'])
        profile.save()
        login(request, user)

    return redirect('profile')



def access_denied(request):
    return render(request, "authsite/access_denied.html")
