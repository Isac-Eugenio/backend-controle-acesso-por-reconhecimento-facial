import asyncio
from typing import Any
import cv2
from numpy import dtype, floating, integer, ndarray
from core.commands.command import Command
from core.commands.result import *
from core.config.app_config import CameraConfig
from models.camera_model import CameraModel


class CameraRepository(CameraModel):
    """
    Repositório para interação com a câmera Ai Thinker ESP32-CAM.
    Extende CameraModel, permitindo:
      - Captura de frames
      - Execução síncrona e assíncrona
      - Validação do status da câmera
    """

    def __init__(self, config: CameraConfig):
        super().__init__(config)
        self.command = Command()  # Wrapper para executar funções com tratamento de erro

    def __str__(self):
        return (
            f"Camera(host={self.host}, port={self.port}, status={self.status_online})"
        )

    def release(self):
        """Libera a câmera caso esteja aberta"""
        if self.cap.isOpened():
            self.cap.release()

    def _get_frame(
        self,
    ) -> Result[cv2.Mat | ndarray[Any, dtype[integer[Any] | floating[Any]]], str]:
        """Captura um frame da câmera de forma síncrona"""
        self.status_online = self.status()

        if not self.status_online:
            return Failure(f"Camera no host {self.full_host} está offline")

        cap = cv2.VideoCapture(self.full_host)

        if not cap.isOpened():
            return Failure(f"Não foi possível abrir a câmera em {self.host}.")

        ret, frame = cap.read()
        cap.release()

        if not ret:
            return Failure(
                f"Não foi possível capturar o frame da câmera em {self.host}."
            )

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Success(frame)

    def get_frame(self) -> Result[cv2.Mat | ndarray[Any, dtype[integer[Any] | floating[Any]]], str]:
        """Executa _get_frame usando o wrapper Command"""
        result = self.command.execute(self._get_frame)
        return result

    async def get_frame_async(
        self,
    ) -> Result[cv2.Mat | ndarray[Any, dtype[integer[Any] | floating[Any]]], str]:
        """Executa get_frame de forma assíncrona usando loop executor"""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.get_frame)
