from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Contact(Base):
    __tablename__ = 'contacts'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    full_name = Column(String(200), nullable=False, index=True)
    email = Column(String(200))
    company = Column(String(200))
    position = Column(String(200))
    connected_on = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    matches = relationship("Match", back_populates="contact", cascade="all, delete-orphan")
    

class Match(Base):
    __tablename__ = 'matches'
    
    id = Column(Integer, primary_key=True)
    contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=False)
    total_mentions = Column(Integer, default=0)
    confidence_score = Column(Float, default=1.0)
    false_positive_score = Column(Float, default=0.0)
    ai_category = Column(String(50))
    ai_sentiment = Column(String(50))
    ai_summary = Column(Text)
    ai_confidence = Column(Float)
    last_searched = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    contact = relationship("Contact", back_populates="matches")
    results = relationship("SearchResult", back_populates="match", cascade="all, delete-orphan")


class SearchResult(Base):
    __tablename__ = 'search_results'
    
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=False)
    document_path = Column(String(500), nullable=False)
    excerpt = Column(Text, nullable=False)
    page_number = Column(Integer)
    document_date = Column(String(50))
    pdf_url = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    match = relationship("Match", back_populates="results")


class MonitorJob(Base):
    __tablename__ = 'monitor_jobs'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    csv_path = Column(String(500), nullable=False)
    email_recipient = Column(String(200))
    check_interval_hours = Column(Integer, default=24)
    is_active = Column(Boolean, default=True)
    last_run = Column(DateTime)
    next_run = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    alerts = relationship("Alert", back_populates="job", cascade="all, delete-orphan")


class Alert(Base):
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('monitor_jobs.id'), nullable=False)
    contact_name = Column(String(200), nullable=False)
    new_mentions_count = Column(Integer, default=0)
    message = Column(Text)
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    job = relationship("MonitorJob", back_populates="alerts")


class PDFCache(Base):
    __tablename__ = 'pdf_cache'
    
    id = Column(Integer, primary_key=True)
    document_path = Column(String(500), nullable=False, unique=True, index=True)
    local_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    page_count = Column(Integer)
    downloaded_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)


class Database:
    
    def __init__(self, db_url: str = "sqlite:///data/epstein.db"):
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
    def create_tables(self):
        Base.metadata.create_all(self.engine)
    
    def get_session(self):
        return self.SessionLocal()
    
    def drop_tables(self):
        Base.metadata.drop_all(self.engine)
