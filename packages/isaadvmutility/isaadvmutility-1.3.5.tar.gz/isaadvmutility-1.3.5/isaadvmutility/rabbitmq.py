import os
import json
from aio_pika import Message, connect, ExchangeType
from typing import Callable

class RabbitMQ:
    def __init__(self, close_on_exit=True) -> None:
        self.__connection_string = f"amqp://{os.environ.get('RABBITMQ_USER')}:{os.environ.get('RABBITMQ_PASSWD')}@{os.environ.get('RABBITMQ_HOST') or 'localhost'}:{os.environ.get('PORT') or 5672}/"
        self.__connection = None
        self.__channel = None
        self.close_on_exit = close_on_exit

    async def connect(self):
        self.__connection = await connect(self.__connection_string)
        self.__channel = await self.__connection.channel()

    async def close(self):
        if self.__channel and not self.__channel.is_closed:
            await self.__channel.close()
        if self.close_on_exit and self.__connection and not self.__connection.is_closed:
            await self.__connection.close()


    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def create(self, exchange_name, queue_name, binding_key, exchange_type=ExchangeType.DIRECT):
        """Create exchange, queue, and routing key."""
        channel = self.__channel
        # Declare an exchange
        exchange = await channel.declare_exchange(exchange_name, exchange_type)
        # Declare a queue
        queue = await channel.declare_queue(queue_name)
        # Bind the exchange and the queue with a binding key
        await queue.bind(exchange, binding_key)

    async def consume_queue(self, queue_name: str, on_message: Callable):
        """Consume messages from a queue and call the on_message callback."""
        channel = self.__channel
        # Declare the queue to consume from
        queue = await channel.declare_queue(queue_name)
        # Set up the consumer
        await queue.consume(on_message)
        print("Waiting for messages...")

    async def publish(self, exchange_name: str, routing_key: str, data: dict):
        """Publish a message to an exchange with a routing key."""
        channel = self.__channel

        # Get the exchange
        exchange = await channel.get_exchange(exchange_name)

        # Convert the dictionary to a JSON string
        json_data = json.dumps(data)

        # Create a message
        message = Message(json_data.encode())

        # Publish the JSON data to the exchange
        await exchange.publish(message, routing_key=routing_key)
