import logging
import time

import orjson
from aiokafka import AIOKafkaProducer
from backoff import backoff
from kafka.admin import KafkaAdminClient, NewTopic
from pydantic import BaseModel

from config import settings as SET

logging.basicConfig(format='%(asctime)s[%(name)s]: %(message)s', level='ERROR')
logger = logging.getLogger(__name__)

kafka_list_urls = [SET.kafka_url]
kafka_kwargs = {'bootstrap_servers': kafka_list_urls, 'client_id': SET.kafka_client}
logger.error('INFO -- kafka_kwargs -- %s', kafka_kwargs)


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class OrJsonModel(BaseModel):

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class RequestKafka(OrJsonModel):
    topic: str
    user_id: str
    movie_id: str
    value: int


@backoff()
def kafka_init():
    """Если нет топика в кафке, то создает."""
    def test_topics():
        admin = KafkaAdminClient(**kafka_kwargs)
        kafka_list = admin.list_topics()
        for topic in SET.topic_list:
            if topic not in kafka_list:
                new_topic = NewTopic(name=topic,
                                     num_partitions=1,
                                     replication_factor=1)
                ad_resp = admin.create_topics(new_topics=[new_topic])
                logger.error('INFO - topic %s not exist, create topic - response: %s', topic, ad_resp)
            elif topic in kafka_list:
                logger.error('INFO - topic %s exist', topic)
        admin.close()
    test_topics()


async def test():
    producer = AIOKafkaProducer(**kafka_kwargs)
    for t in SET.topic_list:
        for i in range(SET.requests_count_for_every_topic):
            data = RequestKafka(topic=t, user_id='user_id', movie_id='movie_id', value=i)
            key = data.user_id + '+' + data.movie_id
            await producer.send(data.topic, data.json().encode(), key.encode())


kafka_init()
start = time.time()
test()
logger.error('INFO - ALL ok, time - %s', time.time() - start)
#  
