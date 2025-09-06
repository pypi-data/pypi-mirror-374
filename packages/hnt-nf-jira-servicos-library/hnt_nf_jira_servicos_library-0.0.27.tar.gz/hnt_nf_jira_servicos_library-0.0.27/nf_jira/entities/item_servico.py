from typing import Optional
from pydantic import BaseModel

class ItemServico(BaseModel):
    nro_servico: str
    centro_custo: Optional[str] = None
    ord_interna: Optional[str] = None
    valor_bruto: float=0.0
    quantidade: str="1"

    # def handle_montante(self):
    #     self.valor_bruto = self.montante
    #     if self.valor_liquido:
    #         self.montante = self.valor_liquido