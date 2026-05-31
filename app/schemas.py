from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

# ── Base Schemas ──────────────────────────────────────────────────────────

class SourceBase(BaseModel):
    title: str
    url: str
    type: str
    metadata_json: Optional[str] = None

class SourceCreate(SourceBase):
    pass

class Source(SourceBase):
    id: int
    capture_date: datetime
    model_config = ConfigDict(from_attributes=True)

# ── Biographic Entities ───────────────────────────────────────────────────

class EventBase(BaseModel):
    name: str
    date: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    source_id: Optional[int] = None
    metadata_json: Optional[str] = None

class Event(EventBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class AwardBase(BaseModel):
    title: str
    date: Optional[str] = None
    institution: Optional[str] = None
    description: Optional[str] = None
    source_id: Optional[int] = None
    metadata_json: Optional[str] = None

class Award(AwardBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class CourseBase(BaseModel):
    title: str
    date: Optional[str] = None
    role: str = "instructor"
    location: Optional[str] = None
    description: Optional[str] = None
    source_id: Optional[int] = None
    metadata_json: Optional[str] = None

class Course(CourseBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class VideoBase(BaseModel):
    title: str
    url: str
    date: Optional[str] = None
    duration: Optional[str] = None
    summary: Optional[str] = None
    transcription: Optional[str] = None
    source_id: Optional[int] = None
    metadata_json: Optional[str] = None

class Video(VideoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class NewsBase(BaseModel):
    title: str
    date: Optional[str] = None
    publisher: Optional[str] = None
    url: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    source_id: Optional[int] = None
    metadata_json: Optional[str] = None

class News(NewsBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class SocialPostBase(BaseModel):
    platform: str
    post_id: Optional[str] = None
    url: str
    date: Optional[str] = None
    content: Optional[str] = None
    likes: int = 0
    comments_count: int = 0
    source_id: Optional[int] = None
    metadata_json: Optional[str] = None

class SocialPost(SocialPostBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class StudentBase(BaseModel):
    name: str
    course_id: Optional[int] = None
    testimonial: Optional[str] = None
    date: Optional[str] = None
    source_id: Optional[int] = None
    metadata_json: Optional[str] = None

class Student(StudentBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class TestimonialBase(BaseModel):
    author: str
    relation: Optional[str] = None
    content: str
    date: Optional[str] = None
    source_id: Optional[int] = None
    metadata_json: Optional[str] = None

class Testimonial(TestimonialBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class MediaMentionBase(BaseModel):
    title: str
    date: Optional[str] = None
    publisher: Optional[str] = None
    url: str
    summary: Optional[str] = None
    source_id: Optional[int] = None
    metadata_json: Optional[str] = None

class MediaMention(MediaMentionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ── New Relational Entities (V2) ──────────────────────────────────────────

class CountryBase(BaseModel):
    name: str
    code: str

class Country(CountryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class StateBase(BaseModel):
    name: str
    code: str
    country_id: int

class State(StateBase):
    id: int
    country: Optional[Country] = None
    model_config = ConfigDict(from_attributes=True)

class CityBase(BaseModel):
    name: str
    state_id: int

class City(CityBase):
    id: int
    state: Optional[State] = None
    model_config = ConfigDict(from_attributes=True)

class InstitutionBase(BaseModel):
    name: str
    acronym: Optional[str] = None
    type: str

class Institution(InstitutionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class UniversityBase(BaseModel):
    name: str
    acronym: Optional[str] = None
    institution_id: Optional[int] = None
    city_id: Optional[int] = None

class University(UniversityBase):
    id: int
    institution: Optional[Institution] = None
    city: Optional[City] = None
    model_config = ConfigDict(from_attributes=True)

class CongressBase(BaseModel):
    name: str
    edition: Optional[str] = None
    city_id: Optional[int] = None

class Congress(CongressBase):
    id: int
    city: Optional[City] = None
    model_config = ConfigDict(from_attributes=True)

class CertificationBase(BaseModel):
    title: str
    institution_id: Optional[int] = None
    date: Optional[str] = None
    url: Optional[str] = None
    credential_id: Optional[str] = None

class Certification(CertificationBase):
    id: int
    institution: Optional[Institution] = None
    model_config = ConfigDict(from_attributes=True)

class PublicationBase(BaseModel):
    title: str
    journal: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    date: Optional[str] = None

class Publication(PublicationBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class EvidenceBase(BaseModel):
    url: Optional[str] = None
    image_url: Optional[str] = None
    pdf_path: Optional[str] = None
    video_url: Optional[str] = None
    doc_path: Optional[str] = None
    print_path: Optional[str] = None

class Evidence(EvidenceBase):
    id: int
    timeline_id: int
    model_config = ConfigDict(from_attributes=True)

# ── Timeline & Attachments ────────────────────────────────────────────────

class AttachmentBase(BaseModel):
    filename: str
    file_path: str
    type: Optional[str] = None
    metadata_json: Optional[str] = None

class Attachment(AttachmentBase):
    id: int
    timeline_id: int
    model_config = ConfigDict(from_attributes=True)

class TimelineItemBase(BaseModel):
    year: int
    month: Optional[int] = None
    type: str
    title: str
    description: Optional[str] = None
    date: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    source_id: Optional[int] = None
    source_table: Optional[str] = None
    source_row_id: Optional[int] = None
    
    # V2 augmented fields
    country_id: Optional[int] = None
    state_id: Optional[int] = None
    city_id: Optional[int] = None
    institution_id: Optional[int] = None
    university_id: Optional[int] = None
    participation_type: Optional[str] = None
    category: Optional[str] = None

class TimelineItemCreate(TimelineItemBase):
    pass

class TimelineItem(TimelineItemBase):
    id: int
    attachments: List[Attachment] = []
    
    # V2 detailed objects
    country: Optional[Country] = None
    state: Optional[State] = None
    city: Optional[City] = None
    institution: Optional[Institution] = None
    university: Optional[University] = None
    evidences: List[Evidence] = []
    
    model_config = ConfigDict(from_attributes=True)

# ── Dashboard & Metrics ───────────────────────────────────────────────────

class RelevanceMap(BaseModel):
    total_courses: int = 0
    total_events: int = 0
    total_news: int = 0
    total_videos: int = 0
    total_students: int = 0
    total_testimonials: int = 0
    total_media_mentions: int = 0
    total_social_posts: int = 0
    total_timeline_items: int = 0
    total_appearances: int = 0
