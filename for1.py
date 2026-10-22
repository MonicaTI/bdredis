import redis
for i in range(5):
    globals()[f'pessoa{i}'] = f'pessoa{i}'
    
pessoa0 = {"nome":"Juliana","idade":22,"cidade": "Chapeco"}
pessoa1 = {"nome":"Antonio","datanasc":{"dia":10, "mes":10, "ano":2000},"cidade": "Chapeco"}
pessoa2 = {"nome":"Pedro","idade":24,"cidade": "Chapeco"}
pessoa3 = {"nome":"Maria","idade":31,"cidade": "Nonoai"}
r = redis.Redis(host='127.0.0.1', port=6379, db=2)
for x in range(0, 4):
  a = str(x)
  chave = str('pessoa' + a)
  r.json().set(f'pessoa{i}', '$', chave)

for x in range(0, 4):
  a = str(x)
  chave = str('pessoa' + a)
  #p1 = r.json().get(chave, '$')
  pd1 = r.json().get(chave, '$.nome')
  ano = r.json().get(chave, '$.datanasc.ano')
  #print(p1)
  print(pd1)
  print(ano)