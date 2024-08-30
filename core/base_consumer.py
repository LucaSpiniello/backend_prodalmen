
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
import jwt
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
import asyncio

User = get_user_model()

class JWTConsumerBase(AsyncWebsocketConsumer):
    async def connect(self):
        query_string = self.scope['query_string'].decode()
        token = self.get_token_from_query_string(query_string)
        try:
            self.user = await self.get_user_from_token(token)
            if self.user:
                await self.accept()
                await self.send(text_data="Connected")
            else:
                raise TokenError("El token es inválido o ha expirado")
        except (TokenError, InvalidToken) as e:
            await self.accept()
            #await self.send(text_data="Token expirado o invalido")
            await asyncio.sleep(1)
            await self.close(code=4001)

    async def disconnect(self, close_code):
        print(f"Desconectado del ws: {close_code}")

    async def receive(self, text_data):
        await self.send(text_data=f"Message received: {text_data}")

    def get_token_from_query_string(self, query_string):
        token = query_string.split('=')[1]
        #print(f"Token: {token}")  # Debug
        return token

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            UntypedToken(token)
            decoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_data.get('user_id')
            user = User.objects.get(id=user_id)
            return user
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist, IndexError) as e:
            #print(f"Token error: {e}")  # Debug
            return None