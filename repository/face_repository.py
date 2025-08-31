import asyncio
from core.commands.result import *
from models.face_model import FaceModel
from models.perfil_model import PerfilModel
from services.face_service import FaceService


class FaceRepository:
    """
    Repositório responsável por gerenciar operações relacionadas ao FaceModel e perfis.
    Permite comparar rostos capturados com perfis cadastrados, de forma síncrona e assíncrona.
    """

    def __init__(self, face_service: FaceService, face_model: FaceModel):
        """Inicializa o repositório com FaceService e FaceModel"""
        self.face_service = face_service
        self.face_model = face_model

    def match_face_to_profiles(
        self,
        list_profiles: list[PerfilModel],
        face_encoding: list[float],
        tolerance: int = 60,
    ) -> Result[PerfilModel, str]:
        """
        Compara um rosto com uma lista de perfis:
        - Gera percentuais de similaridade entre o rosto e cada perfil.
        - Retorna o perfil correspondente se ultrapassar o limite de tolerância.
        - Caso contrário, retorna Failure indicando acesso negado.
        """
        list_encodings = [perfil.encodings for perfil in list_profiles]

        try:
            list_distance = [
                self._distance_percent(enc)
                for enc in self.face_service.fr.face_distance(
                    list_encodings, face_encoding
                )
            ]

            for i, perfil in enumerate(list_profiles):
                if list_distance[i] >= tolerance:
                    return Success(
                        perfil,
                        log=(
                            f"Rosto reconhecido como {perfil.nome} "
                            f"com {list_distance[i]:.2f}% de similaridade"
                        ),
                    )

            return Failure(
                "Acesso negado: rosto não reconhecido",
                details="Nenhum perfil corresponde ao rosto detectado",
                log="Acesso Negado",
                error=False,
            )

        except Exception as e:
            return Failure(
                "Erro ao comparar rosto com perfis",
                details=str(e),
                log="Erro Match",
                error=True,
            )

    async def match_face_to_profiles_async(
        self,
        list_profiles: list[PerfilModel],
        face_encoding: list[float],
        tolerance: int = 60,
    ) -> Result[FaceModel, str]:
        """Versão assíncrona de match_face_to_profiles"""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.match_face_to_profiles(
                list_profiles, face_encoding, tolerance
            ),
        )

    def _distance_percent(self, distance: float) -> float:
        """Converte distância entre rostos em percentual de similaridade"""
        return ((-distance) + 1) * 100
