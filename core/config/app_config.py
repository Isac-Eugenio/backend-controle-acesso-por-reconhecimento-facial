from dataclasses import dataclass, field
from typing import List, Literal
import yaml

# Função para carregar as configurações do arquivo YAML
def load_config(path="core/config/config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)  # Retorna o YAML como dicionário Python

# Carrega as configurações globais para serem usadas nas classes
config = load_config()

# Tipos fixos para os formatos de câmera (substitui Enum)
CameraFormat = Literal["jpg", "bmp", "mjpeg"]

# Tipos fixos para resoluções suportadas pela câmera
CameraResolution = Literal[
    "96x96",
    "160x120",
    "176x144",
    "240x176",
    "240x240",
    "320x240",
    "400x296",
    "480x320",
    "640x480",
    "800x600",
    "1024x768",
    "1280x720",
    "1280x1024",
    "1600x1200",
]

# Classe que representa a configuração de uma câmera
@dataclass
class CameraConfig:
    host: str = config["hosts"]["camera"]        # IP da câmera
    port: int = config["ports"]["camera"]        # Porta da câmera
    resolution: CameraResolution = "800x600"    # Resolução padrão
    format: CameraFormat = "jpg"                 # Formato padrão

    @property
    def custom_host(self) -> str:
        # Retorna uma URL completa para acessar a câmera com host, porta, resolução e formato
        return f"http://{self.host}:{self.port}/{self.resolution}.{self.format}"

# Classe que representa a configuração de conexão com o banco de dados
@dataclass
class DatabaseConfig:
    host: str = config["hosts"]["database"]                # IP ou hostname do banco
    port: int = config["ports"]["database"]                # Porta do banco (padrão MySQL)
    user: str = config["credentials"]["database"]["user"]  # Usuário do banco
    password: str = config["credentials"]["database"]["password"]  # Senha do banco
    name: str = config["credentials"]["database"]["name"]  # Nome do banco

# Classe que mantém os nomes das tabelas do banco de dados
@dataclass
class DatabaseTables:
    perfis: str = config["details"]["database"]["tables"]["perfis"]         # Tabela de perfis
    dispositivos: str = config["details"]["database"]["tables"]["dispositivos"] # Tabela de dispositivos
    historico: str = config["details"]["database"]["tables"]["historico"]   # Tabela de histórico

