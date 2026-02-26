from pydantic import BaseModel

class TrainBase(BaseModel):
    name: str
    fitness_valid: bool
    open_job_card: bool
    cleaning_available: bool
    mileage: float
    branding_priority: int

class TrainResponse(TrainBase):
    id: int

    class Config:
        orm_mode = True