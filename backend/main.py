from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, Enum
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from datetime import datetime
import enum
from pydantic import BaseModel, EmailStr, validator
from passlib.context import CryptContext
import re
import time
from sqlalchemy.exc import OperationalError

# Database setup with retry mechanism
DATABASE_URL = "postgresql://postgres:postgres@db:5432/lending"

def create_db_engine():
    retries = 5
    while retries > 0:
        try:
            engine = create_engine(DATABASE_URL)
            engine.connect()
            return engine
        except OperationalError:
            print(f"Database connection failed, retrying... ({retries} attempts left)")
            retries -= 1
            time.sleep(5)
    raise Exception("Failed to connect to database after multiple attempts")

engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Enums
class LoanStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    paid = "paid"

# Database models
class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True)
    password = Column(String)
    email = Column(String, unique=True)
    phone_number = Column(String(15))

class Lender(Base):
    __tablename__ = "lenders"
    lender_id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    credit_score = Column(Float)
    available_funds = Column(Float)
    registration_date = Column(Date, default=datetime.now().date())

class Loan(Base):
    __tablename__ = "loans"
    loan_id = Column(Integer, primary_key=True)
    borrower_id = Column(Integer, ForeignKey("users.user_id"))
    lender_id = Column(Integer, ForeignKey("lenders.lender_id"))
    amount = Column(Float)
    interest_rate = Column(Float)
    term_months = Column(Integer)
    purpose = Column(String)
    status = Column(Enum(LoanStatus), default=LoanStatus.pending)
    creation_date = Column(Date, default=datetime.now().date())
    approval_date = Column(Date)

# Create tables after connection established
try:
    Base.metadata.create_all(bind=engine)
except OperationalError as e:
    print(f"Error creating tables: {e}")
    raise

# Pydantic models
class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    phone_number: str

    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^\w{5,30}$', v):
            raise ValueError('Username must be 5-30 alphanumeric characters')
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 12 or not re.search(r'[A-Z]', v) or not re.search(r'[a-z]', v) or not re.search(r'\d', v) or not re.search(r'[\W_]', v):
            raise ValueError('Password must be 12+ chars with uppercase, lowercase, number, and special char')
        return v

    @validator('phone_number')
    def validate_phone(cls, v):
        if not re.match(r'^\+?[0-9]{10,15}$', v):
            raise ValueError('Invalid phone number')
        return v

class LenderCreate(BaseModel):
    name: str
    email: EmailStr
    credit_score: float
    available_funds: float

class LoanCreate(BaseModel):
    borrower_id: int
    lender_id: int
    amount: float
    interest_rate: float
    term_months: int
    purpose: str

# FastAPI app
app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        username=user.username,
        password=hashed_password,
        email=user.email,
        phone_number=user.phone_number
    )
    db.add(db_user)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "User created"}

class UserUpdate(BaseModel):
    username: str
    email: EmailStr
    phone_number: str

@app.put("/users/{user_id}")
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.username = user_update.username
    db_user.email = user_update.email
    db_user.phone_number = user_update.phone_number
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "User updated successfully"}

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "User deleted successfully"}

@app.post("/lenders/")
def create_lender(lender: LenderCreate, db: Session = Depends(get_db)):
    db_lender = Lender(**lender.dict())
    db.add(db_lender)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Lender created"}

@app.post("/loans/")
def create_loan(loan: LoanCreate, db: Session = Depends(get_db)):
    if loan.interest_rate < 1.0 or loan.interest_rate > 30.0:
        raise HTTPException(status_code=400, detail="Interest rate must be 1-30%")
    
    db_loan = Loan(**loan.dict())
    db.add(db_loan)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Loan created"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}