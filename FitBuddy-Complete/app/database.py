from datetime import datetime
from sqlalchemy import create_engine, String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from .config import settings

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    age: Mapped[int] = mapped_column(Integer)
    weight: Mapped[float] = mapped_column(Float)
    goal: Mapped[str] = mapped_column(String(50))
    intensity: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    plans: Mapped[list["Plan"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Plan(Base):
    __tablename__ = "plans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    original_plan: Mapped[str] = mapped_column(Text)
    original_tip: Mapped[str] = mapped_column(Text)
    updated_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_tip: Mapped[str | None] = mapped_column(Text, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    user: Mapped[User] = relationship(back_populates="plans")

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db() -> None:
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_user(db, data):
    user = db.query(User).filter(User.user_id == data.user_id).first()
    if user:
        user.name, user.age, user.weight, user.goal, user.intensity = data.name, data.age, data.weight, data.goal, data.intensity
    else:
        user = User(user_id=data.user_id, name=data.name, age=data.age, weight=data.weight, goal=data.goal, intensity=data.intensity)
        db.add(user)
    db.commit(); db.refresh(user)
    return user

def save_plan(db, user, workout_plan, nutrition_tip):
    plan = Plan(user_id=user.id, original_plan=workout_plan, original_tip=nutrition_tip)
    db.add(plan); db.commit(); db.refresh(plan)
    return plan

def get_latest_plan(db, user_id: str):
    return db.query(Plan).join(User).filter(User.user_id == user_id).order_by(Plan.created_at.desc()).first()

def update_plan(db, plan, feedback, workout_plan, nutrition_tip):
    plan.feedback = feedback
    plan.updated_plan = workout_plan
    plan.updated_tip = nutrition_tip
    plan.updated_at = datetime.utcnow()
    db.commit(); db.refresh(plan)
    return plan

def get_all_users(db):
    return db.query(User).order_by(User.created_at.desc()).all()
