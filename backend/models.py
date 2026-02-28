from sqlalchemy import Column, Integer, String, Boolean, Float
from database import Base

class Train(Base):
    __tablename__ = "trains"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    fitness_valid = Column(Boolean)
    open_job_card = Column(Boolean)
    cleaning_completed = Column(Boolean)
    sensor_alert=Column(Boolean,default=False)
    # parking_slot = Column(Integer, nullable=True)
    mileage = Column(Float)
    branding_priority = Column(Integer)
    override_status=Column(String,nullable=True)