from redis import Redis
from rq import Queue
from .config import settings

_redis = Redis.from_url(settings.REDIS_URL)
q = Queue("eval", connection=_redis)
