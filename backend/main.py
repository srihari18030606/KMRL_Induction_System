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

@app.get("/generate-induction")
def generate_induction(
    traffic_level: int = 3,
    db: Session = Depends(get_db)
):
    trains = crud.get_trains(db)

    result = induction.evaluate_trains(
        trains,
        traffic_level=traffic_level
    )

    return result

@app.post("/upload-trains")
async def upload_trains(file: UploadFile = File(...), db: Session = Depends(get_db)):
    
    contents = await file.read()
    decoded = contents.decode("utf-8")
    csv_reader = csv.DictReader(StringIO(decoded))

    count = 0

    for row in csv_reader:
        train_data = {
            "name": row["name"],
            "fitness_valid": row["fitness_valid"].lower() == "true",
            "open_job_card": row["open_job_card"].lower() == "true",
            "cleaning_completed": row["cleaning_completed"].lower() == "true",
            "mileage": float(row["mileage"]),
            "branding_priority": int(row["branding_priority"])
        }

        crud.create_train(db, schemas.TrainBase(**train_data))
        count += 1

    return {"message": f"{count} trains uploaded successfully"}

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

class IoTUpdate(BaseModel):
    train_name: str
    sensor_alert: bool | None = None
    mileage: float | None = None


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