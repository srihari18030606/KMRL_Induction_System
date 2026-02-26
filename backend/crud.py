from sqlalchemy.orm import Session
import models

def get_trains(db: Session):
    return db.query(models.Train).all()

def create_train(db: Session, train):
    db_train = models.Train(**train.dict())
    db.add(db_train)
    db.commit()
    db.refresh(db_train)
    return db_train