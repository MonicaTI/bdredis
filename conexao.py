import socket
import psycopg2

def get_windows_ip():
    """Obtém o IP do host Windows a partir do ambiente WSL2"""
    try:
        # Resolve o hostname padrão da WSL2
        return socket.gethostbyname('host.docker.internal')
    except socket.gaierror:
        # Fallback: le o IP do gateway padrão do arquivo /etc/resolv.conf
        with open('/etc/resolv.conf', 'r') as f:
            for line in f:
                if line.startswith('nameserver'):
                    return line.split()[1]

# Uso na conexao do PostgreSQL
windows_ip = 127.0.0.1
print(f"Conectando ao PostgreSQL no IP: {windows_ip}")

pg_conn = psycopg2.connect(
    host=windows_ip,
    port=5432,
    database="bdgeo",
    user="postgres",
    password="postgres"
)
