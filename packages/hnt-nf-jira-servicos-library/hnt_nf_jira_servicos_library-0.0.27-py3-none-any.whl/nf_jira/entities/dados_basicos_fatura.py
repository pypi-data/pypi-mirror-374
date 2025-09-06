from pydantic import BaseModel
from typing import List, Optional

from .itens_fatura import ItensFatura

class DadosBasicosFatura(BaseModel):
    cod_fornecedor: str
    data_fatura: str
    referencia: Optional[str] = None
    montante: float
    valor_bruto: Optional[float] = 0.0
    bus_pl_sec_cd: str
    texto: str
    itens: List[ItensFatura]

    def handle_montante(self):
        self.valor_bruto = self.montante
        if self.valor_liquido:
            self.montante = self.valor_liquido