import redis
import json
from datetime import datetime

globals()

r = redis.Redis(host='127.0.0.1', port=6379, db=0)
"""
for key in r.scan_iter():
    print(key)
    
for x in range(0, 4):
    nome = input('Nome da pessoa:')
    datan = input('Data de nascimento:')
    cidade = input('Cidade de nascimento:')
    uf = input('Estado:')
    var = {"nome":nome, "datan":datan, "cidade": cidade, "uf": uf}
    r.json().set(str('pessoa' + str(x)), '$', var)
"""
for x in range(0, 4):
  a = str(x)
  chave = str('pessoa' + a)
  print(r.json().get(chave))
  #p1 = r.json().get(chave, '$')
  datanasc = r.json().get(chave, '$.datan')
  data = datetime.strptime(datanasc[0], '%Y-%m-%d')
  datat = datetime.now()
  anoatual = datetime.now().year
  print(anoatual)
  dias = (abs((datat - data).days))/365
  print(dias)