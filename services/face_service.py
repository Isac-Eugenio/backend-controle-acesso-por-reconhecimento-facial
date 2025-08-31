import asyncio
from typing import Any
import face_recognition as fr
from face_recognition import face_encodings, face_locations

from core.commands.result import Failure, Result, Success
from repository.camera_repository import CameraRepository
from models.face_model import FaceModel


class FaceService:
    """
    Serviço responsável por processar rostos usando a câmera e a biblioteca face_recognition.
    - Permite capturar frames síncronos e assíncronos da câmera.
    - Detecta localização de rostos em frames.
    - Gera encodings faciais para identificação.
    - Cria instâncias de FaceModel a partir dos dados capturados.
    """

    def __init__(self, camera_repository: CameraRepository):
        self.camera_repository = camera_repository
        self._frame = camera_repository.get_frame()  # Result síncrono para debug / sync
        self.fr = fr

    # ---------------------------
    # Sync versions
    # ---------------------------
    def get_face_locations(self) -> Result[list[tuple[int, Any, Any, int]], str]:
        # get_face_locations: Detecta rostos em um frame síncrono, retorna lista de coordenadas ou falha.
        if self._frame.is_failure:
            return Failure("Erro ao obter o frame da câmera", details=self._frame.value)
        try:
            locations = face_locations(self._frame.value)
            if not locations:
                return Failure("Nenhum rosto encontrado")
            return Success(locations, log="Rostos encontrados com sucesso")
        except Exception as e:
            return Failure("Erro inesperado ao detectar rostos", details=str(e))

    def get_face_encodings(self) -> Result[list[Any], str]:
        # get_face_encodings: Gera encodings para todos os rostos detectados em um frame síncrono.
        if self._frame.is_failure:
            return Failure("Erro ao obter o frame da câmera", details=self._frame.value)

        locations_result = self.get_face_locations()
        if locations_result.is_failure:
            return Failure("Erro ao encontrar rostos", details=locations_result.value)

        try:
            encodings = face_encodings(self._frame.value, locations_result.value)
            if not encodings:
                return Failure("Nenhum encoding gerado")
            return Success(encodings, log="Encodings gerados com sucesso")
        except Exception as e:
            return Failure("Erro inesperado ao gerar encodings", details=str(e))

    def get_first_face_encoding(self) -> Result[Any, str]:
        # get_first_face_encoding: Retorna o primeiro encoding de rosto encontrado no frame.
        encodings_result = self.get_face_encodings()
        if encodings_result.is_failure:
            return Failure("Erro ao obter encodings", details=encodings_result.value)
        return Success(
            encodings_result.value[0], log="Primeiro encoding obtido com sucesso"
        )

    def create_face_model(self) -> Result[FaceModel, str]:
        # create_face_model: Cria FaceModel a partir do primeiro rosto detectado e seu encoding.

        locations_result = self.get_face_locations()
        if locations_result.is_failure:
            return Failure(
                "Erro ao obter localização do rosto", details=locations_result.value
            )

        encodings_result = self.get_first_face_encoding()
        if encodings_result.is_failure:
            return Failure(
                "Erro ao obter encoding do rosto", details=encodings_result.value
            )

        try:
            face_model = FaceModel(
                location=locations_result.value[0],
                encodings=encodings_result.value,
                frame=self._frame.value,
            )
            return Success(face_model, log="FaceModel criado com sucesso")
        except Exception as e:
            return Failure("Erro ao validar FaceModel", details=str(e))

    # ---------------------------
    # Async frame capture
    # ---------------------------
    async def frame_async(self) -> Result[Any, str]:
        # frame_async: Captura um frame de forma assíncrona usando CameraRepository.

        frame_result = await self.camera_repository.get_frame_async()
        if frame_result.is_failure:
            return Failure(
                "Erro ao capturar frame da câmera", details=frame_result.value
            )
        return frame_result

    # ---------------------------
    # Async versions (usando frame_async)
    # ---------------------------
    async def get_face_locations_async(
        self,
    ) -> Result[list[tuple[int, Any, Any, int]], str]:
        # get_face_locations_async: Versão assíncrona de detecção de rostos.

        frame_result = await self.frame_async()
        if frame_result.is_failure:
            return frame_result
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, lambda: face_locations(frame_result.value)
        )

    async def get_face_encodings_async(self) -> Result[list[Any], str]:
        # get_face_encodings_async: Versão assíncrona de geração de encodings.
        frame_result = await self.frame_async()
        if frame_result.is_failure:
            return frame_result
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, lambda: self.get_face_encodings_sync(frame_result.value)
        )

    async def get_first_face_encoding_async(self) -> Result[Any, str]:
        # get_first_face_encoding_async: Retorna primeiro encoding de forma assíncrona.

        frame_result = await self.frame_async()
        if frame_result.is_failure:
            return frame_result
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, lambda: self.get_first_face_encoding_sync(frame_result.value)
        )

    async def create_face_model_async(self) -> Result[FaceModel, str]:
        # create_face_model_async: Cria FaceModel de forma assíncrona a partir de um frame capturado.

        frame_result = await self.frame_async()
        if frame_result.is_failure:
            return frame_result
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, lambda: self.create_face_model_sync(frame_result.value)
        )

    # ---------------------------
    # Sync helpers para async executor
    # ---------------------------
    def get_face_encodings_sync(self, frame) -> Result[list[Any], str]:
        # get_face_encodings_sync: Helper síncrono usado pelo executor assíncrono.

        locations_result = self.get_face_locations_sync(frame)
        if locations_result.is_failure:
            return Failure("Erro ao encontrar rostos", details=locations_result.value)
        try:
            encodings = face_encodings(frame, locations_result.value)
            if not encodings:
                return Failure("Nenhum encoding gerado")
            return Success(encodings, log="Encodings gerados com sucesso")
        except Exception as e:
            return Failure("Erro inesperado ao gerar encodings", details=str(e))

    def get_first_face_encoding_sync(self, frame) -> Result[Any, str]:
        # get_first_face_encoding_sync: Helper síncrono para obter o primeiro encoding.

        encodings_result = self.get_face_encodings_sync(frame)
        if encodings_result.is_failure:
            return Failure("Erro ao obter encodings", details=encodings_result.value)
        return Success(
            encodings_result.value[0], log="Primeiro encoding obtido com sucesso"
        )

    def create_face_model_sync(self, frame) -> Result[FaceModel, str]:
        # create_face_model_sync: Helper síncrono para criar FaceModel.

        locations_result = self.get_face_locations_sync(frame)
        if locations_result.is_failure:
            return Failure(
                "Erro ao obter localização do rosto", details=locations_result.value
            )
        encodings_result = self.get_first_face_encoding_sync(frame)
        if encodings_result.is_failure:
            return Failure(
                "Erro ao obter encoding do rosto", details=encodings_result.value
            )
        try:
            face_model = FaceModel(
                location=locations_result.value[0],
                encodings=encodings_result.value,
                frame=frame,
            )
            return Success(face_model, log="FaceModel criado com sucesso")
        except Exception as e:
            return Failure("Erro ao validar FaceModel", details=str(e))

    def get_face_locations_sync(
        self, frame
    ) -> Result[list[tuple[int, Any, Any, int]], str]:
        # get_face_locations_sync: Helper síncrono para detectar rostos em frame fornecido.

        try:
            locations = face_locations(frame)
            if not locations:
                return Failure("Nenhum rosto encontrado")
            return Success(locations, log="Rostos encontrados com sucesso")
        except Exception as e:
            return Failure("Erro inesperado ao detectar rostos", details=str(e))
