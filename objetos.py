import redis
pessoa0 = {"nome":"Juliana","idade":22,"cidade": "Chapeco"}
pessoa1 = {"nome":"Leonardo","idade":22,"cidade": "Chapeco"}
pessoa2 = {"nome":"Pedro","idade":24,"cidade": "Chapeco"}
pessoa3 = {"nome":"Maria","idade":31,"cidade": "Nonoai"}
r = redis.Redis(host='127.0.0.1', port=6379, db=2)
r.json().set('pessoa0', '$', pessoa0)
r.json().set('pessoa1', '$', pessoa1)
r.json().set('pessoa2', '$', pessoa2)
r.json().set('pessoa3', '$', pessoa3)

for x in range(0, 4):
  a = str(x)
  chave = str('pessoa' + a)
  print(chave)
  print(r.json().get(chave, '$'))
  objeto = r.json().get('chave', '$.nome')
  print(objeto)
