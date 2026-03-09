from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class OutreachStatus(enum.Enum):
    NOT_GENERATED = "not_generated"
    PITCH_READY = "pitch_ready"
    SENT = "sent"
    REPLIED = "replied"
    NOT_INTERESTED = "not_interested"
    CONVERTED = "converted"

class WebsiteStatus(enum.Enum):
    NO_WEBSITE = "no_website"
    BROKEN = "broken"
    NOT_MOBILE = "not_mobile"
    HAS_WEBSITE = "has_website"
    UNKNOWN = "unknown"
    TIMEOUT = "timeout"

class CampaignStatus(enum.Enum):
    PROCESSING = "processing"
    READY = "ready"
    ARCHIVED = "archived"


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Settings stored as JSON
    settings = Column(JSON, default=lambda: {
        'skill': 'Web Development',
        'pitch_tone': 'professional',
        'cerebras_api_key': '',
        'country_code': '+254'
    })
    
    # Relationships
    campaigns = relationship('Campaign', back_populates='user', cascade='all, delete-orphan')


class Campaign(Base):
    __tablename__ = 'campaigns'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    name = Column(String(200), nullable=False)
    location = Column(String(200))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # File tracking
    csv_filename = Column(String(200))  # Original filename for display
    csv_filepath = Column(String(500))  # Unique filepath for internal use
    
    status = Column(SQLEnum(CampaignStatus), default=CampaignStatus.PROCESSING)
    
    # Stats stored as JSON
    stats = Column(JSON, default=lambda: {
        'total_rows': 0,
        'total_businesses': 0,
        'opportunities_found': 0,
        'contacted': 0,
        'replied': 0,
        'converted': 0,
        'skipped_count': 0
    })
    
    # Batch tracking
    batch_config = Column(JSON, default=lambda: {
        'batch_size': 10,
        'current_batch': 0,
        'total_generated': 0,
        'last_generated_at': None
    })
    
    # Column mapping (stores detected mappings)
    column_mapping = Column(JSON, default=dict)
    
    # Skipped businesses (for transparency)
    skipped_businesses = Column(JSON, default=list)
    
    # Relationships
    user = relationship('User', back_populates='campaigns')
    businesses = relationship('Business', back_populates='campaign', cascade='all, delete-orphan')


class Business(Base):
    __tablename__ = 'businesses'
    
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'), nullable=False)
    
    # Original data (cleaned)
    name = Column(String(200), nullable=False)
    category = Column(String(100))
    address = Column(Text)
    phone_raw = Column(String(50))
    phone_normalized = Column(String(50))
    rating = Column(Float)
    review_count = Column(Integer)
    review_snippet = Column(Text)
    google_maps_url = Column(Text)
    
    # Analysis results
    website_url = Column(String(500))
    website_status = Column(SQLEnum(WebsiteStatus), default=WebsiteStatus.UNKNOWN)
    opportunity_score = Column(Integer, default=0)
    discovery_analysis = Column(Text)
    
    # Generated content
    ai_pitch = Column(Text)
    ai_pitch_edited = Column(Text)
    pitch_source = Column(String(20))  # 'ai' or 'template'
    
    # Batch tracking
    batch_number = Column(Integer)
    pitch_generated_at = Column(DateTime)
    
    # Outreach tracking
    outreach_status = Column(SQLEnum(OutreachStatus), default=OutreachStatus.NOT_GENERATED)
    contacted_at = Column(DateTime)
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    campaign = relationship('Campaign', back_populates='businesses')
