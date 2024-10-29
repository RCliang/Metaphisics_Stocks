from pydantic import BaseModel
from datetime import date as date_, datetime
from typing import Optional




class Plate(BaseModel):
    plate_code: str
    plate_name: str
