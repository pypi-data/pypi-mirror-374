from typing import AsyncIterable, Dict, List
from aiokafka import AIOKafkaProducer
from pydantic import BaseModel
from datetime import datetime
import json
import aiohttp


class AiLog(BaseModel):
    modelId: str
    confidenceScore: float
    responseTimeMs: int
    timestamp: datetime
    numericFeatures: Dict[str, float]
    categoricalFeatures: Dict[str, str]

    def to_json(self) -> str:
        # Convert to dict and format timestamp with Z suffix for UTC
        data = self.dict()
        data['timestamp'] = self.timestamp.isoformat() + 'Z'
        return json.dumps(data)

class AiLogKafkaProducer:
    def __init__(self, kafka_bootstrap_servers: str, topic: str = "ai-logs"):
        self.bootstrap_servers = kafka_bootstrap_servers
        self.topic = topic
        self._producer: AIOKafkaProducer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            key_serializer=lambda k: k.encode("utf-8"),
            value_serializer=lambda v: v.encode("utf-8")
        )

    async def start(self):
        await self._producer.start()

    async def stop(self):
        await self._producer.stop()

    async def produce_ai_logs(self, logs: List[AiLog]):
        for log in logs:
            await self._producer.send_and_wait(
                topic=self.topic,
                key=log.modelId,
                value=log.to_json()
            )

    async def produce_stream_logs(self, logs: AsyncIterable[AiLog]):
        async for log in logs:
            await self._producer.send_and_wait(
                topic=self.topic,
                key=log.modelId,
                value=log.to_json()
            )


class AiLogHttpProducer:
    def __init__(self, endpoint_url: str, timeout: int = 30):
        self.endpoint_url = endpoint_url
        self.timeout = timeout

    async def produce_ai_logs(self, logs: List[AiLog]):
        # Convert logs to JSON array
        logs_data = [json.loads(log.to_json()) for log in logs]
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as session:
            async with session.post(
                self.endpoint_url,
                json=logs_data,
                headers={'Content-Type': 'application/json'}
            ) as response:
                response.raise_for_status()
                return await response.text()
