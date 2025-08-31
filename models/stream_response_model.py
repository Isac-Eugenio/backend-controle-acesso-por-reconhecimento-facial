from fastapi.responses import StreamingResponse
from core.commands.stream_command import StreamCommand


class StreamResponse:
    """
    Estrutura de resposta para streams usando FastAPI.
    - Recebe um StreamCommand e transforma em StreamingResponse.
    """

    def __init__(self, stream_command: StreamCommand):
        self.stream = stream_command  # Comando de stream que será executado

    async def _def_generator(self):
        """
        Gera dados do stream.
        - Itera pelos resultados do StreamCommand.
        - Converte cada resultado para dict e adiciona quebra de linha.
        """
        async for task in self.stream.execute_stream():
            yield f"{task.to_map()}\n\n"

    async def response(self) -> StreamingResponse:
        """
        Retorna a resposta como StreamingResponse do FastAPI.
        - Define media_type como text/event-stream.
        - Usa o generator _def_generator para enviar os dados em tempo real.
        """
        return StreamingResponse(self._def_generator(), media_type="text/event-stream")
