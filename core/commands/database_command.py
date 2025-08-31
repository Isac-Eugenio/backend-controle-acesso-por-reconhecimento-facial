from typing import List, Union
from numpy import record
from core.commands.async_command import AsyncCommand
from core.commands.result import *
from models.query_model import QueryModel
from databases import Database as AsyncDatabase


class DatabaseCommand(AsyncCommand):
    """
    Classe que estende AsyncCommand para lidar com operações assíncronas em banco de dados.
    Permite conectar, desconectar e executar queries (SELECT ou comandos DML/DDL).
    """

    def __init__(self, database: AsyncDatabase):
        """
        Inicializa o DatabaseCommand com uma instância de AsyncDatabase.
        """
        self.database = database
        self.isconnected = False  # Controle de estado da conexão

    async def _connect_func(self) -> Result[str, str]:
        """
        Função interna que tenta realizar a conexão com o banco de dados.
        Retorna Success ou Failure encapsulado em Result.
        """
        try:
            self.connection = await self.database.connect()  # Conecta ao banco
            self.isconnected = True
            return Success("Conexão bem-sucedida")
        except Exception as e:
            self.isconnected = False
            return Failure(f"Erro ao se conectar ao DB", details=str(e))

    async def _connect(self) -> Result[str, str]:
        """
        Executa a conexão usando a função assíncrona _connect_func através de execute_async.
        Retorna Result encapsulado.
        """
        result = await self.execute_async(self._connect_func)
        return result

    async def close(self):
        """
        Fecha a conexão de forma segura, aguardando o encerramento da conexão.
        Marca isconnected como False.
        """
        if self.connection:
            self.connection.close()
            await self.connection.wait_closed()
            self.isconnected = False

    async def _disconnect(self) -> Result[str, str]:
        """
        Desconecta do banco de dados, se estiver conectado.
        Retorna Success se já estiver desconectado.
        Retorna Failure se ocorrer algum erro.
        """
        if not self.isconnected:
            return Success("DB já desconectado")

        try:
            await self.database.disconnect()
            self.isconnected = False
            return Success("Desconexão bem-sucedida")
        except Exception as e:
            return Failure(f"Erro ao desconectar do DB", details=str(e))

    async def execute_query(
        self, query: QueryModel, type_fetch: str = None
    ) -> Result[Union[record, List[record], int], str]:
        """
        Executa uma query no banco de dados de forma assíncrona.
        type_fetch pode ser:
            - "one": retorna um único registro (fetch_one)
            - "all": retorna todos os registros (fetch_all)
            - None: executa comando DML/DDL e retorna número de linhas afetadas

        Faz conexão antes da execução e desconecta sempre no final.
        """
        # Tenta conectar
        conn_result = await self._connect()
        if conn_result.is_failure:
            return Failure(
                f"Erro ao conectar ao banco de dados", details=conn_result.value
            )

        try:
            # Executa a query de acordo com o tipo de fetch
            if type_fetch == "one":
                data = await self.database.fetch_one(
                    query=query.query, values=query.values
                )
            elif type_fetch == "all":
                data = await self.database.fetch_all(
                    query=query.query, values=query.values
                )
            else:
                data = await self.database.execute(
                    query=query.query, values=query.values
                )

            return Success(data)

        except Exception as e:
            # Captura erros da query e encapsula em Failure
            return Failure(f"Erro ao executar a query", details=str(e))

        finally:
            # Garante que a conexão será desconectada sempre, mesmo se ocorrer erro
            await self._disconnect()
