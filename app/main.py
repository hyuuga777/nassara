import os
import sys
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import (
    get_db, People, Sources, Events, Awards, Courses,
    Videos, News, SocialPosts, Students, Testimonials, MediaMentions,
    Timeline, Attachments
)
from app.schemas import RelevanceMap, TimelineItem, Student, Testimonial, Source, Course, Event, News as NewsSchema, Video

app = FastAPI(
    title="Buscador Biográfico Inteligente - API",
    description="Backend API de alta performance para o memorial digital e linha do tempo profissional da Dra. Nássara Mesquita.",
    version="1.0.0"
)

# Configure CORS to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for local/development use
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Endpoints ─────────────────────────────────────────────────────────

@app.get("/api/profile")
def get_profile(db: Session = Depends(get_db)):
    profile = db.query(People).filter(People.name == "Dra. Nassara Mesquita").first()
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil profissional não localizado.")
    return {
        "name": profile.name,
        "bio": profile.bio,
        "birth_date": profile.birth_date,
        "status": profile.status,
        "registry_date": profile.registry_date,
        "metadata_json": profile.metadata_json
    }

@app.get("/api/timeline", response_model=List[TimelineItem])
def get_timeline(
    year: Optional[int] = None,
    month: Optional[int] = None,
    country_id: Optional[int] = None,
    state_id: Optional[int] = None,
    city_id: Optional[int] = None,
    institution_id: Optional[int] = None,
    university_id: Optional[int] = None,
    type: Optional[str] = None,
    category: Optional[str] = None,
    source_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Timeline)
    if year is not None:
        query = query.filter(Timeline.year == year)
    if month is not None:
        query = query.filter(Timeline.month == month)
    if country_id is not None:
        query = query.filter(Timeline.country_id == country_id)
    if state_id is not None:
        query = query.filter(Timeline.state_id == state_id)
    if city_id is not None:
        query = query.filter(Timeline.city_id == city_id)
    if institution_id is not None:
        query = query.filter(Timeline.institution_id == institution_id)
    if university_id is not None:
        query = query.filter(Timeline.university_id == university_id)
    if type is not None:
        query = query.filter(Timeline.type == type)
    if category is not None:
        query = query.filter(Timeline.category == category)
    if source_id is not None:
        query = query.filter(Timeline.source_id == source_id)
    
    # Sort chronologically by year (descending) and month (descending)
    return query.order_by(Timeline.year.desc(), Timeline.month.desc()).all()

@app.get("/api/relevance", response_model=RelevanceMap)
def get_relevance(db: Session = Depends(get_db)):
    """
    Calculate dynamic relevance mapping and metrics based on actual database counts.
    """
    # Count occurrences across all relational tables
    courses_count = db.query(Courses).count()
    events_count = db.query(Events).count()
    news_count = db.query(News).count()
    videos_count = db.query(Videos).count()
    students_count = db.query(Students).count()
    testimonials_count = db.query(Testimonials).count()
    mentions_count = db.query(MediaMentions).count()
    posts_count = db.query(SocialPosts).count()
    timeline_count = db.query(Timeline).count()
    
    # Calculate a weighted score representing public presence index
    appearances_score = (
        (courses_count * 15) + 
        (events_count * 10) + 
        (news_count * 8) + 
        (videos_count * 8) + 
        (posts_count * 4) + 
        (mentions_count * 12)
    )
    
    return RelevanceMap(
        total_courses=courses_count,
        total_events=events_count,
        total_news=news_count,
        total_videos=videos_count,
        total_students=students_count,
        total_testimonials=testimonials_count,
        total_media_mentions=mentions_count,
        total_social_posts=posts_count,
        total_timeline_items=timeline_count,
        total_appearances=appearances_score
    )

@app.get("/api/testimonials", response_model=List[Testimonial])
def get_testimonials(db: Session = Depends(get_db)):
    return db.query(Testimonials).all()

@app.get("/api/students", response_model=List[Student])
def get_students(db: Session = Depends(get_db)):
    return db.query(Students).all()

@app.get("/api/sources", response_model=List[Source])
def get_sources(db: Session = Depends(get_db)):
    return db.query(Sources).all()

@app.get("/api/courses", response_model=List[Course])
def get_courses(db: Session = Depends(get_db)):
    return db.query(Courses).all()

@app.get("/api/events", response_model=List[Event])
def get_events(db: Session = Depends(get_db)):
    return db.query(Events).all()

@app.get("/api/news", response_model=List[NewsSchema])
def get_news(db: Session = Depends(get_db)):
    return db.query(News).all()

@app.get("/api/videos", response_model=List[Video])
def get_videos(db: Session = Depends(get_db)):
    return db.query(Videos).all()

@app.get("/api/lattes")
def get_lattes_curriculum(db: Session = Depends(get_db)):
    """
    Generate grouped Lattes curriculum structures from enriched timeline records.
    """
    items = db.query(Timeline).order_by(Timeline.year.desc(), Timeline.month.desc()).all()
    
    curriculum = {
        "formacao": [],
        "atuacao": [],
        "producoes": [],
        "eventos": [],
        "cursos": [],
        "orientacoes": [],
        "certificacoes": []
    }
    
    for item in items:
        cat = (item.category or "").lower().strip()
        
        # Group chronologically into the 7 standard Lattes sections
        if "formacao" in cat or "graduação" in cat or "pós-graduação" in cat or "formação" in cat:
            section = "formacao"
        elif "atuacao" in cat or "atuação" in cat:
            section = "atuacao"
        elif "producoes" in cat or "produção" in cat or "produções" in cat or item.type == "video":
            section = "producoes"
        elif "eventos" in cat or "evento" in cat:
            section = "eventos"
        elif "cursos" in cat or "curso" in cat:
            section = "cursos"
        elif "orientacoes" in cat or "orientações" in cat or "mentoria" in cat:
            section = "orientacoes"
        elif "certificacoes" in cat or "certificações" in cat or item.type == "award":
            section = "certificacoes"
        else:
            # Fallback based on item type
            type_map = {
                "course": "cursos",
                "event": "eventos",
                "award": "certificacoes",
                "video": "producoes",
                "news": "producoes",
                "social": "producoes"
            }
            section = type_map.get(item.type, "atuacao")
            
        curriculum[section].append({
            "id": item.id,
            "year": item.year,
            "month": item.month,
            "type": item.type,
            "title": item.title,
            "description": item.description,
            "date": item.date,
            "participation_type": item.participation_type,
            "institution": item.institution.name if item.institution else None,
            "university": item.university.name if item.university else None,
            "location": f"{item.city.name}/{item.state.code}" if (item.city and item.state) else None
        })
        
    return curriculum

# Root landing check
@app.get("/")
def read_root():
    return {
        "status": "online",
        "app": "Buscador Biográfico Inteligente - Dra. Nássara Mesquita",
        "version": "1.0.0",
        "endpoints": {
            "profile": "/api/profile",
            "timeline": "/api/timeline",
            "relevance": "/api/relevance",
            "testimonials": "/api/testimonials",
            "students": "/api/students",
            "sources": "/api/sources",
            "courses": "/api/courses",
            "events": "/api/events",
            "news": "/api/news",
            "videos": "/api/videos"
        }
    }
