from enum import Enum
from typing import Union


class TipoDado(Enum):
    NOTA = 1
    CARTAO = 2
    CREDENCIAL = 3
    IDENTIDADE = 4

    @staticmethod
    def get_icon(tipo_dado: Union['TipoDado', None]) -> str:
        """Retorna o ícone correspondente ao tipo de dado."""
        return {
            TipoDado.CREDENCIAL: "images/credencial.png",
            TipoDado.CARTAO: "images/cartao.png",
            TipoDado.IDENTIDADE: "images/identidade.png",
            TipoDado.NOTA: "images/nota.png",
        }.get(tipo_dado, "images/default.png")
