import redis
from PIL import Image

def establish_redis_connection():

  # Configuration parameters for Redis connection in file redis_settings.py
  from redis_settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD

  print("Establishing connection to Redis server at", REDIS_HOST, "on port", REDIS_PORT)
  
  # Create a Redis client instance
  redis_client = redis.StrictRedis(
      host=REDIS_HOST,
      port=REDIS_PORT,
      password=REDIS_PASSWORD,
      decode_responses=False  # Decode responses to UTF-8
  )

  # Test the connection
  try:
      redis_client.ping()
      print("Connected to Redis!")
      return redis_client
  except redis.ConnectionError as e:
      print(f"Error connecting to Redis: {e}")
      return None


def push_image_to_redis(redis_client, image_path, redis_key):
    with open(image_path, 'rb') as f:
        image_data = f.read()
    redis_client.set(redis_key, image_data)


def push_to_redis(redis_client):
  push_image_to_redis(redis_client, './plots/daq_weekly_livetime_light.png', 'cumulative_pot:daq_uptime:image')
  push_image_to_redis(redis_client, './plots/pot_weekly_collection_efficiency_light.png', 'cumulative_pot:pot_collection_weekly:image')
  push_image_to_redis(redis_client, './plots/livetime_pot_cumulative_run2_light.png', 'cumulative_pot:livetime_pot_cumulative_run2:image')
  push_image_to_redis(redis_client, './plots/livetime_pot_cumulative_run1+2_light.png', 'cumulative_pot:livetime_pot_cumulative_run1-2:image')
