import redis
import psycopg2
from psycopg2.extras import execute_values
import json

r = redis.Redis(host='localhost', port=6379, db=0)
pg_conn = psycopg2.connect("dbname=bdgeo user=postgres password=postgres host=127.0.0.1")

def receber_coordenada_gps(veiculo_id: int, lon: float, lat: float, velocidade: float):
    member_id = f"veiculo:{veiculo_id}"
    r.geoadd("frotas:posicoes", (lon, lat, member_id))
    dado_ponto = json.dumps({"veiculo_id": veiculo_id, "lon": lon, "lat": lat, "velocidade": velocidade})
    r.rpush("fila:persistir_postgis", dado_ponto)

def worker_persistir_postgis():
    pontos = []
    while len(pontos) < 100 and r.llen("fila:persistir_postgis") > 0:
        item = r.lpop("fila:persistir_postgis")
        if item:
            pontos.append(json.loads(item))
    if not pontos:
        return
    query = """
        INSERT INTO historico_posicoes (veiculo_id, posicao, velocidade)
        VALUES %s
    """
    valores = [
        (p["veiculo_id"], f'ST_SetSRID(ST_MakePoint({p["lon"]}, {p["lat"]}), 4326)', p["velocidade"])
        for p in pontos
    ]
    with pg_conn.cursor() as cur:
        execute_values(cur, query, valores, template="(%s, %s, %s)")
        pg_conn.commit()
worker_persistir_postgis()

