import redis
pessoa10 = {"nome":"Leonardo","idade":22,"cidade": "Chapeco"}
pessoa20 = {"nome":"Pedro","idade":24,"cidade": "Chapeco"}
pessoa30 = {"nome":"Maria","idade":31,"cidade": "Nonoai"}

data = {
    'doguinho': {
        'scientific-name' : 'Canis familiaris'
    }
}

r = redis.Redis(host='127.0.0.1', port=6379, db=2)

r.json().set('doc', '$', pessoa20)
doc = r.json().get('doc', '$')
dog = r.json().get('doc', '$.pessoa1')
scientific_name = r.json().get('doc', '$..scientific-name')
print(dog)