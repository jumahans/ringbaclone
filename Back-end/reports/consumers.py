import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class ScamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        token = self.scope["query_string"].decode().split("token=")[-1]
        user = await self.get_user(token)

        if not user:
            await self.close()
            return

        self.group_name = "scam_reports"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        pass

    async def scam_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    @database_sync_to_async
    def get_user(self, token: str):
        try:
            from ninja_jwt.tokens import AccessToken
            from authentication.models import User
            access_token = AccessToken(token)
            user_id = access_token["user_id"]
            return User.objects.get(id=user_id)
        except Exception:
            return None