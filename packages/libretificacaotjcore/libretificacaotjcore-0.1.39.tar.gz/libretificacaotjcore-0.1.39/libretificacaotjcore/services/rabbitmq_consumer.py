import aio_pika
import json

class RabbitMQConsumer:
    def __init__(
        self,
        *,
        host: str,
        queue: str,
        username: str,
        password: str,
        vhost: str = "/",
    ):
        self.host = host
        self.queue = queue
        self.username = username
        self.password = password
        self.vhost = vhost
        self.connection = None
        self.channel = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust(
            host=self.host,
            login=self.username,
            password=self.password,
            virtualhost=self.vhost,
            heartbeat=600,
        )
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=1)
        await self.channel.declare_queue(self.queue, durable=True)

    async def start_consuming(self, *, callback):
        if not self.channel:
            raise RuntimeError("❌ Canal RabbitMQ não conectado. Chame connect() antes.")

        queue = await self.channel.get_queue(self.queue)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        mensagem = json.loads(message.body.decode())
                        await callback(mensagem)
                    except Exception as e:
                        print(f"Erro ao processar mensagem: {e}")\
                    
                    await self.close()

    async def close(self):
        if self.connection:
            await self.connection.close()
