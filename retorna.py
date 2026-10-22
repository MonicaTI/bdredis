import redis
r = redis.Redis(host='127.0.0.1', port=6379, db=3)
r.hmset("pessoa1":"name": "Paul Zamir","email": "paul.zamir@example.com","age": 35,"city": "Tel Aviv")
r.hgetall
