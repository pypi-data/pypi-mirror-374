from typing import Optional
from pydantic import BaseModel


class ImpostoMiro(BaseModel):
    sem_retencao: Optional[bool] = False
