import json


class RedisStreamProducer():
    def __init__(self, redis_client):
        self.redis_client = redis_client

    def publish_message(self, room_id: str, message: dict):
        self.redis_client.publish(room_id, json.dumps(message))

class RedisStreamSubscriber():
    def __init__(self, redis_client, websocket):
        self.redis_client = redis_client
        self.pub_sub = redis_client.pubsub()
        self.websocket = websocket

    async def subscribe(self, room_id: str):
        await self.pub_sub.subscribe(room_id)

        async for message in self.pub_sub.listen():
            if message['type'] == 'message':
                data = message['data']
                if not isinstance(data, str):
                    data = str(data)
                await self.websocket.send_text(data)