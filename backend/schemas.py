from pydantic import BaseModel,Field

class TrainBase(BaseModel):
    name: str
    fitness_valid: bool
    open_job_card: bool
    cleaning_completed: bool
    # sensor_alert: bool
    # override_status
    # parking_slot: int | None = None
    mileage: float=Field(...,ge=0)
    branding_priority: int = Field(...,ge=0)

class TrainResponse(TrainBase):
    id: int

    class Config:
        orm_mode = True