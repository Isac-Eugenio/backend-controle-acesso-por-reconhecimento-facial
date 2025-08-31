from services.ping_service import PingService
from core.config.app_config import CameraConfig
from core.utils.api_utils import ApiUtils


class CameraModel:
    """
    Representa uma câmera no sistema, incluindo configuração, status e
    identificação única. Estrutura pensada para o módulo ESP32-CAM 
    modelo Ai Thinker:

        - Host/IP e porta de acesso à câmera
        - Resolução suportada (ex.: 800x600, 1024x768, 1280x720)
        - Formato de imagem (BMP, JPG, MJPEG)
        - ID único da câmera gerado automaticamente
        - URL completa para requisições HTTP
        - Status online da câmera (usando Ping)
    
    Este modelo facilita integração de múltiplas câmeras ESP32-CAM
    em aplicações de monitoramento, captura de imagens ou vídeo.
    """
    
    def __init__(self, config: CameraConfig):
        """
        Inicializa o modelo da câmera com a configuração fornecida.

        Args:
            config (CameraConfig): Configuração da câmera contendo host, porta,
                                   resolução e formato.
        """
        self.config = config  # Configuração principal da câmera
        self.host = config.host
        self.port = config.port
        self.resolution = config.resolution
        self.format = config.format

        # Resoluções e formatos suportados (pode ser usado para validação ou UI)
        self.available_resolutions = ["800x600", "1024x768", "1280x720"]
        self.available_formats = ["BMP", "JPG", "MJPEG"]

        # ID único da câmera gerado automaticamente
        self.camera_id = ApiUtils()._generate_id()

        # URL completa para acessar a câmera
        self.full_host = f"http://{self.host}:{self.port}/{self.resolution}.{self.format}"

        # Status online da câmera
        self.status_online = self.status()

    def status(self) -> bool:
        """
        Verifica se a câmera está online usando o serviço de ping.

        Returns:
            bool: True se a câmera responder ao ping, False caso contrário.
        """
        ping = PingService(self.host)  # Cria serviço de ping para o host
        self.status_online = ping.ping()  # Atualiza status da câmera
        return self.status_online
