import argparse
import json
import os
from datetime import datetime, timedelta, timezone

from pymongo import MongoClient
from pymongo.errors import PyMongoError
import redis
from redis.exceptions import RedisError

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
NOME_BANCO = "QualidadeAr"


def interpretar_inicio(valor):
    instante = datetime.fromisoformat(valor.replace("Z", "+00:00"))
    if instante.tzinfo is None:
        raise argparse.ArgumentTypeError("Informe o fuso (ex.: Z ou +00:00).")
    instante = instante.astimezone(timezone.utc)
    if instante.minute or instante.second or instante.microsecond:
        raise argparse.ArgumentTypeError("O início deve ser uma hora cheia (ex.: 10:00:00Z).")
    return instante


def agregar(medicoes, inicio, fim, por_cidade=False):
    etapas = [{"$match": {"timestamp": {"$gte": inicio, "$lt": fim}}}]
    if por_cidade:
        etapas += [
            {"$lookup": {
                "from": "Sensores", "localField": "sensor_id",
                "foreignField": "_id", "as": "sensor"
            }},
            {"$unwind": "$sensor"},
            {"$match": {"sensor.localizacao.cidade": {"$type": "string"},
                        "sensor.localizacao.uf": {"$type": "string"}}},
        ]
        grupo = {"uf": "$sensor.localizacao.uf", "cidade": "$sensor.localizacao.cidade"}
    else:
        grupo = "$sensor_id"

    etapas += [{"$group": {
        "_id": grupo,
        "qt_medicoes": {"$sum": 1},
        "pm25_media": {"$avg": "$pm25"},
        "pm10_media": {"$avg": "$pm10"},
        "co2_media": {"$avg": "$co2"},
        "temperatura_media": {"$avg": "$temperatura"},
        "umidade_media": {"$avg": "$umidade"},
        "pm25_max": {"$max": "$pm25"},
        "pm10_max": {"$max": "$pm10"},
    }}]
    return list(medicoes.aggregate(etapas))


def montar_resumo(registro, inicio, fim, por_cidade):
    resumo = {
        "inicio_periodo": inicio.isoformat().replace("+00:00", "Z"),
        "fim_periodo": fim.isoformat().replace("+00:00", "Z"),
        "qt_medicoes": registro["qt_medicoes"],
    }
    if por_cidade:
        resumo.update(uf=registro["_id"]["uf"], cidade=registro["_id"]["cidade"])
    else:
        resumo["sensor_id"] = str(registro["_id"])
    for campo in ("pm25_media", "pm10_media", "co2_media", "temperatura_media",
                  "umidade_media", "pm25_max", "pm10_max"):
        valor = registro.get(campo)
        resumo[campo] = round(float(valor), 2) if valor is not None else None
    return resumo


def slug_cidade(valor):
    import unicodedata
    texto = unicodedata.normalize("NFKD", valor)
    return "".join(c for c in texto if not unicodedata.combining(c)).lower().replace(" ", "_")


def gravar_e_publicar(r, resumo, por_cidade):
    if por_cidade:
        destino = f"{resumo['uf']}:{slug_cidade(resumo['cidade'])}"
        chave = f"qualidadear:cidade:{destino}"
        canais = [f"qualidadear:resumo:{destino}", "qualidadear:resumo:geral"]
    else:
        destino = resumo["sensor_id"]
        chave = f"qualidadear:sensor:{destino}"
        canais = [f"qualidadear:sensor:{destino}"]

    # Hash persistente para leitores que não estavam conectados durante o Pub/Sub.
    campos = {campo: str(valor) for campo, valor in resumo.items() if valor is not None}
    r.hset(chave, mapping=campos)
    mensagem = json.dumps(resumo, ensure_ascii=False)
    for canal in canais:
        r.publish(canal, mensagem)
    print(f"Gravado {chave}; publicado em: {', '.join(canais)}")


def main():
    parser = argparse.ArgumentParser(description="MongoDB → Redis: resumos horários de qualidade do ar")
    parser.add_argument("--inicio", type=interpretar_inicio,
                        help="Início UTC do período (ex.: 2026-10-20T10:00:00Z)")
    args = parser.parse_args()

    agora = datetime.today()
    fim_padrao = agora.replace(minute=0, second=0, microsecond=0)
    inicio = args.inicio or (fim_padrao - timedelta(hours=1))
    fim = inicio + timedelta(hours=1)

    mongo = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    r = redis.Redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=5)
    try:
        mongo.admin.command("ping")
        r.ping()
        medicoes = mongo[NOME_BANCO]["Medicoes"]
        print(f"Período UTC: {inicio.isoformat()} até {fim.isoformat()}")

        por_sensor = agregar(medicoes, inicio, fim, por_cidade=False)
        por_cidade = agregar(medicoes, inicio, fim, por_cidade=True)
        for reg in por_sensor:
            gravar_e_publicar(r, montar_resumo(reg, inicio, fim, False), False)
        for reg in por_cidade:
            gravar_e_publicar(r, montar_resumo(reg, inicio, fim, True), True)
        print(f"Concluído: {len(por_sensor)} sensores e {len(por_cidade)} cidades.")
        if not por_sensor:
            print("Nenhuma medição encontrada no período.")
    except (PyMongoError, RedisError, ValueError) as exc:
        print(f"Erro durante a integração: {exc}")
    finally:
        mongo.close()
        r.close()


if __name__ == "__main__":
    main()
