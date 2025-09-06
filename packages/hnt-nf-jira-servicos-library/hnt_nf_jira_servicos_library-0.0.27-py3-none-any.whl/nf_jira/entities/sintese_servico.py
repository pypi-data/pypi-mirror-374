from typing import List, Optional
from pydantic import BaseModel

from nf_jira.entities.fatura_servico import FaturaServico

from .item_servico import ItemServico

class SinteseServico(BaseModel):
    categoria_cc: str
    categoria_item: str="D"
    quantidade: str="1"
    texto_breve: str
    centro: Optional[str] = None
    grp_mercadorias: str
    fatura: FaturaServico
    item: List[ItemServico]