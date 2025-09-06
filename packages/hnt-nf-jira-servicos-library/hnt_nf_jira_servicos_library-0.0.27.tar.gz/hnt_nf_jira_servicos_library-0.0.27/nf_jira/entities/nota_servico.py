from pydantic import BaseModel

from typing import List, Optional

from nf_jira.entities.constants import ZAIM, ZCOR

from .sintese_servico import SinteseServico
from .anexo import Anexo

class NotaServico(BaseModel):
    empresa: str="HFNT"
    tipo: str=ZCOR
    org_compras: Optional[str] = None
    grp_compradores: str
    cod_fornecedor: str
    # valor_bruto: float=0.0
    sintese_itens: List[SinteseServico] = []
    anexo: List[Anexo]

    def __init__(self, **data):
        super().__init__(**data)
        self.handle_tipo()

    def handle_tipo(self):
        for sintese_item in self.sintese_itens:
            for item in sintese_item.item:
                if item.ord_interna is not None and item.ord_interna.startswith("6"):
                    self.tipo = ZAIM