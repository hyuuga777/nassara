import os
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Float
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv

# Load configurations from .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///y:/CLIENTE/nassara/buscador/database.db")

# In Windows, ensure the directory exists before engine creation
db_path = DATABASE_URL.replace("sqlite:///", "")
db_dir = os.path.dirname(db_path)
if db_dir and not os.path.exists(db_dir):
    os.makedirs(db_dir, exist_ok=True)

# Create engine and session local
# connect_args={"check_same_thread": False} is required only for SQLite to allow multiple threads
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ── ORM Models ─────────────────────────────────────────────────────────────

class Countries(Base):
    __tablename__ = "countries"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(10), nullable=False)

class States(Base):
    __tablename__ = "states"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(10), nullable=False)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    
    country = relationship("Countries")

class Cities(Base):
    __tablename__ = "cities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=False)
    
    state = relationship("States")

class Institutions(Base):
    __tablename__ = "institutions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    acronym = Column(String(50), nullable=True)
    type = Column(String(100), nullable=False) # 'university', 'faculty', 'council', 'congress', 'company', 'clinic', 'hospital', 'association'

class Universities(Base):
    __tablename__ = "universities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    acronym = Column(String(50), nullable=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)
    
    institution = relationship("Institutions")
    city = relationship("Cities")

class Congresses(Base):
    __tablename__ = "congresses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    edition = Column(String(50), nullable=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)
    
    city = relationship("Cities")

class Certifications(Base):
    __tablename__ = "certifications"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=True)
    date = Column(String(50), nullable=True)
    url = Column(String(500), nullable=True)
    credential_id = Column(String(100), nullable=True)
    
    institution = relationship("Institutions")

class Publications(Base):
    __tablename__ = "publications"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    journal = Column(String(200), nullable=True)
    doi = Column(String(100), nullable=True)
    url = Column(String(500), nullable=True)
    date = Column(String(50), nullable=True)

class People(Base):
    __tablename__ = "people"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    bio = Column(Text, nullable=True)
    birth_date = Column(String(50), nullable=True)
    registry_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="active")
    metadata_json = Column(Text, nullable=True) # JSON stored as text

class Sources(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    url = Column(String(500), unique=True, nullable=False)
    type = Column(String(50), nullable=False) # 'instagram', 'website', 'news', 'sympla', etc.
    capture_date = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(Text, nullable=True)

class Events(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    date = Column(String(50), nullable=True) # ISO format or readable string
    location = Column(String(200), nullable=True) # 'Goiânia/GO', 'Online', etc.
    description = Column(Text, nullable=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    metadata_json = Column(Text, nullable=True)
    
    source = relationship("Sources")

class Awards(Base):
    __tablename__ = "awards"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    date = Column(String(50), nullable=True)
    institution = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    metadata_json = Column(Text, nullable=True)
    
    source = relationship("Sources")

class Courses(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    date = Column(String(50), nullable=True)
    role = Column(String(50), default="instructor") # 'instructor' (ministrado) or 'student' (realizado)
    location = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    metadata_json = Column(Text, nullable=True)
    
    source = relationship("Sources")

class Videos(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    url = Column(String(500), nullable=False)
    date = Column(String(50), nullable=True)
    duration = Column(String(50), nullable=True)
    summary = Column(Text, nullable=True)
    transcription = Column(Text, nullable=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    metadata_json = Column(Text, nullable=True)
    
    source = relationship("Sources")

class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    date = Column(String(50), nullable=True)
    publisher = Column(String(100), nullable=True) # CRF-GO, Delta Proto, etc.
    url = Column(String(500), nullable=True)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    metadata_json = Column(Text, nullable=True)
    
    source = relationship("Sources")

class SocialPosts(Base):
    __tablename__ = "social_posts"
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False) # 'instagram', 'linkedin', 'facebook', 'tiktok'
    post_id = Column(String(100), nullable=True)
    url = Column(String(500), nullable=False)
    date = Column(String(50), nullable=True)
    content = Column(Text, nullable=True)
    likes = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    metadata_json = Column(Text, nullable=True)
    
    source = relationship("Sources")

class Students(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    testimonial = Column(Text, nullable=True)
    date = Column(String(50), nullable=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    metadata_json = Column(Text, nullable=True)
    
    source = relationship("Sources")
    course = relationship("Courses")

class Testimonials(Base):
    __tablename__ = "testimonials"
    id = Column(Integer, primary_key=True, index=True)
    author = Column(String(100), nullable=False)
    relation = Column(String(100), nullable=True) # 'student', 'patient', 'partner'
    content = Column(Text, nullable=False)
    date = Column(String(50), nullable=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    metadata_json = Column(Text, nullable=True)
    
    source = relationship("Sources")

class MediaMentions(Base):
    __tablename__ = "media_mentions"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    date = Column(String(50), nullable=True)
    publisher = Column(String(100), nullable=True)
    url = Column(String(500), nullable=False)
    summary = Column(Text, nullable=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    metadata_json = Column(Text, nullable=True)
    
    source = relationship("Sources")

class Timeline(Base):
    __tablename__ = "timeline"
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=True)
    type = Column(String(50), nullable=False) # 'course', 'event', 'award', 'video', 'news', 'social'
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    date = Column(String(50), nullable=True) # Full readable date
    image_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    source_table = Column(String(50), nullable=True) # 'courses', 'events', etc.
    source_row_id = Column(Integer, nullable=True) # FK to the original table
    
    # V2 Relational Geolocation and Academic / Institutional Fields
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=True)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=True)
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=True)
    participation_type = Column(String(100), nullable=True) # Palestrante, Professora, etc.
    category = Column(String(100), nullable=True) # Formação, Atuação, etc.
    
    source = relationship("Sources")
    attachments = relationship("Attachments", back_populates="timeline", cascade="all, delete-orphan")
    country = relationship("Countries")
    state = relationship("States")
    city = relationship("Cities")
    institution = relationship("Institutions")
    university = relationship("Universities")
    evidences = relationship("Evidences", back_populates="timeline", cascade="all, delete-orphan")

class Evidences(Base):
    __tablename__ = "evidences"
    id = Column(Integer, primary_key=True, index=True)
    timeline_id = Column(Integer, ForeignKey("timeline.id"), nullable=False)
    url = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)
    pdf_path = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    doc_path = Column(String(500), nullable=True)
    print_path = Column(String(500), nullable=True)
    
    timeline = relationship("Timeline", back_populates="evidences")

class Attachments(Base):
    __tablename__ = "attachments"
    id = Column(Integer, primary_key=True, index=True)
    timeline_id = Column(Integer, ForeignKey("timeline.id"), nullable=False)
    filename = Column(String(200), nullable=False)
    file_path = Column(String(500), nullable=False)
    type = Column(String(50), nullable=True) # 'image', 'document', 'certificate'
    metadata_json = Column(Text, nullable=True)
    
    timeline = relationship("Timeline", back_populates="attachments")

class SearchParameters(Base):
    """Stores search configuration: keywords, target sites, and search engines used for biography research."""
    __tablename__ = "search_parameters"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False)  # 'keyword', 'site', 'engine', 'social'
    value = Column(String(500), nullable=False)
    label = Column(String(200), nullable=True)  # human-readable label
    active = Column(Integer, default=1)  # 1=active, 0=inactive
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)

class SectionSummaries(Base):
    """Stores AI-generated and editable summaries for key bio sections."""
    __tablename__ = "section_summaries"
    id = Column(Integer, primary_key=True, index=True)
    section_name = Column(String(100), unique=True, nullable=False)  # 'courses', 'events', 'videos', 'news', 'testimonials'
    content = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ── Database Initialization ───────────────────────────────────────────────

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Banco de dados e tabelas inicializados com sucesso!")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
