import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv

load_dotenv()

# Secure DB connection for Streamlit Cloud (defaults to local SQLite for testing)
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///tax_plan.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class FamilyMember(Base):
    __tablename__ = "family_members"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    role = Column(String) # 'Spouse 1', 'Spouse 2', 'Child 1', 'Child 2'
    age = Column(Integer)
    has_dtc = Column(Boolean, default=False)
    
    incomes = relationship("Income", back_populates="member")
    accounts = relationship("RegisteredAccount", back_populates="member")

class Income(Base):
    __tablename__ = "income"
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("family_members.id"))
    employment_income = Column(Float, default=0.0)
    taxes_withheld = Column(Float, default=0.0)
    rrsp_deduction = Column(Float, default=0.0)
    medical_expenses = Column(Float, default=0.0)
    childcare_expenses = Column(Float, default=0.0)
    
    member = relationship("FamilyMember", back_populates="incomes")

class RegisteredAccount(Base):
    __tablename__ = "registered_accounts"
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("family_members.id"))
    account_type = Column(String) # 'RRSP', 'TFSA', 'RESP', 'FHSA', 'RDSP'
    balance = Column(Float, default=0.0)
    room_available = Column(Float, default=0.0)
    planned_contribution = Column(Float, default=0.0)
    
    member = relationship("FamilyMember", back_populates="accounts")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
