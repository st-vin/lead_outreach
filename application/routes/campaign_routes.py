from flask import Blueprint, render_template, request, redirect, url_for, Response, stream_with_context, jsonify
from application.database import get_db_session
from application.models import User, Campaign, Business, OutreachStatus
from application.services.pitch import PitchGenerator
from application.utils.crypto import decrypt_api_key
import json
from datetime import datetime
import config

bp = Blueprint('campaign', __name__)

def get_or_create_user(db):
    """Get or create default user using provided session."""
    user = db.query(User).first()
    if not user:
        user = User(name='User', email='user@example.com')
        db.add(user)
    return user

@bp.route('/campaign/<int:campaign_id>')
def campaign_detail(campaign_id):
    """Campaign detail view with businesses"""
    with get_db_session() as db:
        user = get_or_create_user(db)
        campaign = db.query(Campaign).filter_by(id=campaign_id, user_id=user.id).first()
        
        if not campaign:
            return redirect(url_for('main.dashboard'))
        
        # Get businesses with filters
        status_filter = request.args.get('status', 'all')
        sort_by = request.args.get('sort', 'score_desc')
        
        query = db.query(Business).filter_by(campaign_id=campaign_id)
        
        # Apply status filter
        if status_filter != 'all':
            if status_filter == 'pitch_ready':
                query = query.filter_by(outreach_status=OutreachStatus.PITCH_READY)
            elif status_filter == 'contacted':
                query = query.filter_by(outreach_status=OutreachStatus.SENT)
            elif status_filter == 'replied':
                query = query.filter_by(outreach_status=OutreachStatus.REPLIED)
        
        # Apply sorting
        if sort_by == 'score_desc':
            query = query.order_by(Business.opportunity_score.desc())
        elif sort_by == 'score_asc':
            query = query.order_by(Business.opportunity_score.asc())
        elif sort_by == 'recent':
            query = query.order_by(Business.created_at.desc())
        
        businesses = query.all()
    
    return render_template(
        'campaign_detail.html', 
        campaign=campaign, 
        businesses=businesses,
        user=user
    )

@bp.route('/api/campaigns/<int:campaign_id>/generate-batch', methods=['GET'])
def generate_batch_sse(campaign_id):
    """Generate AI pitches with Server-Sent Events for progress"""
    
    def generate():
        batch_size = int(request.args.get('size', config.DEFAULT_BATCH_SIZE))
        
        with get_db_session() as db:
            user = get_or_create_user(db)
            campaign = db.query(Campaign).filter_by(id=campaign_id, user_id=user.id).first()
            
            if not campaign:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Campaign not found'})}\n\n"
                return
            
            # Get pending businesses
            businesses = db.query(Business).filter(
                Business.campaign_id == campaign_id,
                Business.outreach_status == OutreachStatus.NOT_GENERATED,
                Business.opportunity_score >= config.MIN_OPPORTUNITY_SCORE
            ).order_by(
                Business.opportunity_score.desc()
            ).limit(batch_size).all()
            
            total = len(businesses)
            
            if total == 0:
                yield f"data: {json.dumps({'type': 'complete', 'message': 'No businesses to generate pitches for'})}\n\n"
                return
            
            # Yield start message
            yield f"data: {json.dumps({'type': 'started', 'total': total, 'message': f'Generating pitches for {total} businesses...'})}\n\n"
            
            # Get API key and user preferences
            settings = user.settings or {}
            api_key = decrypt_api_key(settings.get('cerebras_api_key', ''))
            
            # Initialize pitch generator
            pitch_gen = PitchGenerator(
                api_key=api_key,
                user_skill=settings.get('skill', 'Web Development'),
                user_name=user.name,
                tone=settings.get('pitch_tone', 'professional')
            )
            
            current_batch = campaign.batch_config.get('current_batch', 0) + 1
            success_count = 0
            
            for idx, business in enumerate(businesses):
                try:
                    # Prepare business data
                    business_data = {
                        'id': business.id,
                        'name': business.name,
                        'category': business.category,
                        'address': business.address,
                        'rating': business.rating,
                        'review_count': business.review_count,
                        'review_snippet': business.review_snippet,
                        'discovery_analysis': business.discovery_analysis,
                        'website_status': business.website_status.value if business.website_status else 'unknown'
                    }
                    
                    # Generate pitch (with AI or template fallback)
                    pitch, source = pitch_gen.generate_pitch(business_data)
                    
                    # Update business
                    business.ai_pitch = pitch
                    business.pitch_source = source
                    business.batch_number = current_batch
                    business.pitch_generated_at = datetime.utcnow()
                    business.outreach_status = OutreachStatus.PITCH_READY
                    
                    db.commit()
                    success_count += 1
                    
                    # Yield progress
                    yield f"data: {json.dumps({'type': 'progress', 'current': idx + 1, 'total': total, 'business_name': business.name, 'pitch_source': source, 'status': 'success'})}\n\n"
                    
                except Exception as e:
                    # Yield error but continue
                    yield f"data: {json.dumps({'type': 'progress', 'current': idx + 1, 'total': total, 'business_name': business.name, 'status': 'error', 'error_message': str(e)})}\n\n"
            
            # Update campaign stats
            batch_config = campaign.batch_config
            batch_config['current_batch'] = current_batch
            batch_config['total_generated'] = batch_config.get('total_generated', 0) + success_count
            batch_config['last_generated_at'] = datetime.utcnow().isoformat()
            campaign.batch_config = batch_config
            
            db.commit()
            
            # Yield complete
            yield f"data: {json.dumps({'type': 'complete', 'total': total, 'success': success_count, 'message': f'Generated {success_count} pitches!'})}\n\n"
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )
