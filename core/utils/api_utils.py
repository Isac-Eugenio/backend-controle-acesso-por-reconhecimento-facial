import hashlib
import random
from typing import AsyncGenerator, Awaitable, Callable, List, Tuple
from repository.database_repository import DatabaseRepository


class ApiUtils:
    """
    Classe utilitária com métodos estáticos para manipulação de dados, 
    geração de IDs, hashing e tratamento de listas/dicionários.
    """

    @staticmethod
    def _generate_id() -> str:
        """
        Gera um ID aleatório de 8 dígitos, preenchendo com zeros à esquerda se necessário.
        Retorno: string com 8 caracteres numéricos.
        """
        return str(random.randint(0, 99999999)).zfill(8)

    @staticmethod
    def _ensure_str_values(data: dict) -> dict:
        """
        Converte todos os valores de um dicionário para string, adicionando aspas simples.
        Útil para gerar SQL ou valores serializados.
        Exemplo: {'id': 5} -> {'id': "'5'"}
        """
        return {key: f"'{value}'" for key, value in data.items()}

    @staticmethod
    def is_empty_list(lst) -> list:
        """
        Retorna uma lista vazia se a lista fornecida for None ou vazia.
        Caso contrário, retorna a própria lista.
        """
        return [] if not lst else lst

    @staticmethod
    def _hash_sha256(s: str) -> str:
        """
        Gera o hash SHA-256 de uma string.
        Retorna o hash hexadecimal de 64 caracteres.
        """
        return hashlib.sha256(s.encode("utf-8")).hexdigest()

    @staticmethod
    def _is_sha256_hash(s: str) -> bool:
        """
        Verifica se uma string é um hash SHA-256 válido (64 caracteres hexadecimais).
        Retorna True se for, False caso contrário.
        """
        if len(s) != 64:
            return False
        try:
            int(s, 16)  # testa se todos os caracteres são hexadecimais
            return True
        except ValueError:
            return False

    @staticmethod
    def _limpar_dict(d: dict) -> dict:
        """
        Remove do dicionário todas as chaves cujo valor seja vazio, None, lista ou dicionário vazio.
        Útil para filtrar dados antes de inserção ou atualização em banco.
        """
        return {k: v for k, v in d.items() if v not in ("", None, [], {})}

    @staticmethod
    def _null_or_empty_columns(d: dict) -> list[str]:
        """
        Retorna uma lista com as chaves do dicionário que possuem valores nulos ou vazios.
        Útil para identificar colunas não preenchidas em dados de entrada.
        """
        return [k for k, v in d.items() if v in ("", None, [], {})]

    @staticmethod
    def generate_encodings(num: int) -> str:
        """
        Gera uma string simulando encodings faciais repetidos 128 vezes.
        O valor 'num' deve ser de 0 a 9.
        Exemplo: num=3 -> '0.3,0.3,0.3,...' (128 vezes)
        """
        if not (0 <= num <= 9):
            raise ValueError("O número deve ser um inteiro entre 0 e 9")
        value = f"0.{num}"
        return ",".join([value] * 128)
