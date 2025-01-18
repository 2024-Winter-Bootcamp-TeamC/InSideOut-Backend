from sqlalchemy.orm import Session
import redis


redis_client = redis.Redis(host="teamC_redis", port=6379, decode_responses=True)

def get_emotions(user_id: int, db: Session):

    emotions_key = f"emotions_{user_id}"

    emotions = redis_client.get(emotions_key)
    


    return emotions


