from flask import Blueprint, render_template
from application.database import get_db_session
from application.models import User, Campaign

bp = Blueprint('main', __name__)

def get_or_create_user(db):
    """Get or create default user (MVP: single user) using provided session."""
    user = db.query(User).first()
    
    if not user:
        user = User(
            name='User',
            email='user@example.com',
            settings={
                'skill': 'Web Development',
                'pitch_tone': 'professional',
                'cerebras_api_key': '',
                'country_code': '+254'
            }
        )
        db.add(user)
    
    return user

@bp.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@bp.route('/dashboard')
def dashboard():
    """Main dashboard - show all campaigns"""
    with get_db_session() as db:
        user = get_or_create_user(db)
        campaigns = db.query(Campaign).filter_by(
            user_id=user.id
        ).order_by(Campaign.uploaded_at.desc()).all()
    
    return render_template('dashboard.html', campaigns=campaigns, user=user)
