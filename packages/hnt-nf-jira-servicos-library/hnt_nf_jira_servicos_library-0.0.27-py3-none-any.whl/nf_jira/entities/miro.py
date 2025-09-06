from typing import Optional
from pydantic import BaseModel

from nf_jira.entities.imposto_miro import ImpostoMiro

from .dados_basicos_miro import DadosBasicosMiro
from .referencia_pedido import ReferenciaPedido
from .detalhe import Detalhe

class Miro(BaseModel):
    dados_basicos: DadosBasicosMiro
    referencia_pedido: Optional[ReferenciaPedido] = None
    detalhe: Detalhe
    imposto: Optional[ImpostoMiro] = None
