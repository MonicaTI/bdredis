import redis
pessoa1 = {"nome":"Antonio","datanasc":{"dia":10, "mes":10, "ano":2000},"cidade": "Chapeco"}
pessoa2 = {"nome":"Pedro","idade":24,"cidade": "Chapeco"}
pessoa3 = {"nome":"Maria","idade":31,"cidade": "Nonoai"}

r = redis.Redis()
r.json().set('pessoa1', '$', pessoa1)
r.json().set('pessoa2', '$', pessoa2)
r.json().set('pessoa3', '$', pessoa3)
p1 = r.json().get('pessoa1', '$')
pd1 = r.json().get('pessoa1', '$.datanasc')
ano = r.json().get('pessoa1', '$..ano')
print(p1)
print(pd1)
print(ano)