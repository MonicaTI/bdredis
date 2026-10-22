
from datetime import datetime, timedelta, timezone
import random
from pymongo import MongoClient
from pymongo.errors import PyMongoError

URI_MONGODB = "mongodb://localhost:27017/"
BANCO = "QualidadeAr"

DATA_INICIAL = datetime(2026, 10, 22, 0, 0, tzinfo=timezone.utc)
HORAS_SIMULACAO = 24
INTERVALO_MINUTOS = 5


def gerar_medicao(sensor_id, instante):
    pm25 = round(random.uniform(5, 85), 1)
    pm10 = round(random.uniform(pm25, 130), 1)

    return {
        "sensor_id": sensor_id,
        "timestamp": instante,
        "pm25": pm25,
        "pm10": pm10,
        "co2": random.randint(400, 1100),
        "temperatura": round(random.uniform(15, 35), 1),
        "umidade": random.randint(30, 90)
    }


def main():
    cliente = MongoClient(
        URI_MONGODB, serverSelectionTimeoutMS=5000
    )

    try:
        cliente.admin.command("ping")
        banco = cliente[BANCO]

        sensores = list(
            banco["Sensores"].find(
                {"ativo": True}, {"_id": 1}
            )
        )

        ids_sensores = [s["_id"] for s in sensores]

        if not ids_sensores:
            print("Nenhum sensor ativo encontrado.")
            return

        medicoes = banco["Medicoes"]

        medicoes.create_index([
            ("sensor_id", 1),
            ("timestamp", -1)
        ])

        total_instantes = (
            HORAS_SIMULACAO * 60 // INTERVALO_MINUTOS
        )

        documentos = [
            gerar_medicao(
                sensor_id,
                DATA_INICIAL + timedelta(
                    minutes=i * INTERVALO_MINUTOS
                )
            )
            for i in range(total_instantes)
            for sensor_id in ids_sensores
        ]

        resultado = medicoes.insert_many(documentos)

        print(f"Sensores ativos: {len(ids_sensores)}")
        print(f"Medições inseridas: {len(resultado.inserted_ids)}")
        print("Primeira medição:", documentos[0])

    except PyMongoError as erro:
        print(f"Erro de acesso ao MongoDB: {erro}")

    finally:
        cliente.close()


if __name__ == "__main__":
    main()
