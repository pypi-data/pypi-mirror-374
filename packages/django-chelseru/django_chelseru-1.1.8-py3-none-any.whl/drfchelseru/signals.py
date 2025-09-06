from django.contrib.auth.models import User as DefaultUser
from .models import User, Payment, Wallet
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import requests

from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async

UserGet = get_user_model()


@receiver(pre_save, sender=User)
def create_user_if_not_exists(sender, instance, **kwargs):
    if not instance.user_id:
        default_user, created = DefaultUser.objects.get_or_create(mobile_drf_chelseru__mobile=instance.mobile, mobile_drf_chelseru__group=instance.group, 
                                                                  defaults={'username': f'G{instance.group}-{instance.mobile}'})
        if created:
            instance.user = default_user
            Wallet.objects.create(user=default_user)


@receiver(post_save, sender=DefaultUser)
def send_email_after_create(sender, instance, **kwargs):
    try:
        susers = DefaultUser.objects.filter(is_superuser=True).exclude(email="")
        url = 'https://mail.chelseru.com/api/v1/chelseru_auth/new-user/'
        data = {
            'to': ','.join(list(map(lambda x: x.email, susers))),
            'username': instance.username,
        }

        response = requests.post(url=url, data=data)
    except:
        pass

    


@sync_to_async
def get_user(validated_token):
    try:
        user_id = validated_token["user_id"]
        return UserGet.objects.get(id=user_id)
    except UserGet.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token")
        
        if token:
            try:
                access_token = AccessToken(token[0])
                scope["user"] = await get_user(access_token)
            except Exception as e:
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)



# @receiver(post_save, sender=Payment)
# def charge_wallet_after_pay(sender, instance, **kwargs):
#     if instance.status == Payment.PAID:
#         if hasattr(instance.user, 'wallet_drf_chelseru'):
#             print('ok')
#             instance.user.wallet_drf_chelseru.amount += instance.amount
#             instance.save()
#         else:
#             print('nok')