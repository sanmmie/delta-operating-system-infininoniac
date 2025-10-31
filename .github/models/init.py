from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

Base = declarative_base()

class DeltaNode(Base):
    __tablename__ = "delta_nodes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    node_id = Column(String(50), unique=True, nullable=False)
    domain = Column(String(50), nullable=False)
    status = Column(String(20), default="active")
    last_heartbeat = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TransformationPlan(Base):
    __tablename__ = "transformation_plans"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    node_id = Column(String(50), nullable=False)
    domain = Column(String(50), nullable=False)
    plan_data = Column(JSON, nullable=False)
    confidence_score = Column(Float, nullable=False)
    status = Column(String(20), default="pending")
    impact_metrics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class EthicalEvaluation(Base):
    __tablename__ = "ethical_evaluations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_id = Column(String(36), nullable=False)
    principles_evaluation = Column(JSON, nullable=False)
    overall_score = Column(Float, nullable=False)
    recommendations = Column(JSON)
    evaluated_at = Column(DateTime, default=datetime.utcnow)

class Database:
    def __init__(self, config):
        self.config = config
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def _create_engine(self):
        db_config = self.config.get('database.postgres')
        connection_string = (
            f"postgresql://{db_config['username']}:{db_config['password']}"
            f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )
        return create_engine(connection_string, pool_size=db_config['pool_size'])
    
    def get_session(self):
        return self.SessionLocal()
    
    def create_tables(self):
        Base.metadata.create_all(bind=self.engine)
