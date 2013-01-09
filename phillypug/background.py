from redis import Redis
from rq import Queue

# creates the Redis connection
redis_client = Redis()

# creates a default worker queue with our default Redis connection
worker_queue = Queue(connection=redis_client)
