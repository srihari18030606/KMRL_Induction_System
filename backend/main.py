from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import models, schemas, crud, induction
from database import engine, SessionLocal, Base

from fastapi import File,UploadFile
import csv
from io import StringIO

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/trains", response_model=list[schemas.TrainResponse])
def read_trains(db: Session = Depends(get_db)):
    return crud.get_trains(db)

@app.post("/trains")
def add_train(train: schemas.TrainBase, db: Session = Depends(get_db)):
    return crud.create_train(db, train)

from fastapi import Query

from datetime import datetime
import json

@app.get("/generate-induction")
def generate_induction(
    traffic_level: int = Query(3, ge=1, le=5),
    db: Session = Depends(get_db)
):
    trains = crud.get_trains(db)

    result = induction.evaluate_trains(
        trains,
        traffic_level=traffic_level
    )

    # Create audit log entry
    log_entry = models.InductionLog(
        traffic_level=traffic_level,
        service_trains=json.dumps([t["train"] for t in result["service"]]),
        standby_trains=json.dumps([t["train"] for t in result["standby"]]),
        maintenance_trains=json.dumps([t["train"] for t in result["maintenance"]])
    )

    db.add(log_entry)

    # Auto-clear override
    for train in trains:
        if train.override_status is not None:
            train.override_status = None

    db.commit()

    return result

@app.post("/upload-branding")
async def upload_branding(file: UploadFile = File(...), db: Session = Depends(get_db)):

    contents = await file.read()
    decoded = contents.decode("utf-8")
    csv_reader = csv.DictReader(StringIO(decoded))

    updated = 0
    unknown_trains = []
    invalid_rows = []

    for row in csv_reader:

        try:
            name = row["name"]
            branding_value = int(row["branding_priority"])

            if branding_value < 0:
                invalid_rows.append(name)
                continue

        except:
            invalid_rows.append(row)
            continue

        train = db.query(models.Train).filter(models.Train.name == name).first()

        if train:
            train.branding_priority = branding_value
            updated += 1
        else:
            unknown_trains.append(name)

    db.commit()

    return {
        "updated_trains": updated,
        "unknown_trains": unknown_trains,
        "invalid_rows": invalid_rows
    }

@app.delete("/reset-database")
def reset_database(db: Session = Depends(get_db)):
    crud.delete_all_trains(db)
    return {"message": "All trains deleted successfully"}

from pydantic import BaseModel

class MaximoUpdate(BaseModel):
    train_name: str
    open_job_card: bool | None = None
    fitness_valid: bool | None = None


@app.patch("/maximo-update")
def maximo_update(update: MaximoUpdate, db: Session = Depends(get_db)):
    train = db.query(models.Train).filter(models.Train.name == update.train_name).first()

    if not train:
        return {"error": "Train not found"}

    if update.open_job_card is not None:
        train.open_job_card = update.open_job_card

    if update.fitness_valid is not None:
        train.fitness_valid = update.fitness_valid

    db.commit()
    return {"message": "Maximo data updated"}

from pydantic import BaseModel, Field

class IoTUpdate(BaseModel):
    train_name: str
    sensor_alert: bool | None = None
    mileage: float | None = Field(default=None,ge=0)


@app.patch("/iot-update")
def iot_update(update: IoTUpdate, db: Session = Depends(get_db)):
    train = db.query(models.Train).filter(models.Train.name == update.train_name).first()

    if not train:
        return {"error": "Train not found"}

    if update.sensor_alert is not None:
        train.sensor_alert = update.sensor_alert

    if update.mileage is not None:
        train.mileage = update.mileage

    db.commit()
    return {"message": "IoT data updated"}

class CleaningUpdate(BaseModel):
    train_name: str
    cleaning_completed: bool


@app.patch("/cleaning-update")
def cleaning_update(update: CleaningUpdate, db: Session = Depends(get_db)):
    train = db.query(models.Train).filter(models.Train.name == update.train_name).first()

    if not train:
        return {"error": "Train not found"}

    train.cleaning_completed = update.cleaning_completed
    db.commit()

    return {"message": "Cleaning status updated"}


from typing import Literal
class SupervisorUpdate(BaseModel):
    train_name: str
    override_status: Literal["standby","maintenance"]# "standby" or "maintenance"


@app.patch("/supervisor-update")
def supervisor_update(update: SupervisorUpdate, db: Session = Depends(get_db)):

    train = db.query(models.Train).filter(models.Train.name == update.train_name).first()

    if not train:
        return {"error": "Train not found"}

    if update.override_status not in ["standby", "maintenance"]:
        return {"error": "Invalid override status"}

    train.override_status = update.override_status
    db.commit()

    return {"message": "Supervisor override applied"}


@app.get("/induction-logs")
def get_induction_logs(db: Session = Depends(get_db)):
    logs = db.query(models.InductionLog).all()

    return [
        {
            "id": log.id,
            "timestamp": log.timestamp,
            "traffic_level": log.traffic_level,
            "service": json.loads(log.service_trains),
            "standby": json.loads(log.standby_trains),
            "maintenance": json.loads(log.maintenance_trains),
        }
        for log in logs
    ]

import random

@app.post("/populate-database")
def populate_database(db: Session = Depends(get_db)):

    # Clear existing trains
    db.query(models.Train).delete()

    for i in range(1, 11):
        train = models.Train(
            name=f"T-{i}",
            fitness_valid=random.choice([True, True, True, False]),  # mostly valid
            open_job_card=random.choice([False, False, True]),
            cleaning_completed=random.choice([True, True, False]),
            sensor_alert=False,
            mileage=random.randint(1000, 35000),
            branding_priority=random.randint(0, 10),
            override_status=None
        )

        db.add(train)

    db.commit()

    return {"message": "10 sample trains created successfully"}