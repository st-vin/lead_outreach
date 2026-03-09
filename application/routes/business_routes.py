from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from application.database import get_db_session
from application.models import Business, Campaign, OutreachStatus
from application.utils.phone import create_whatsapp_link
from datetime import datetime

bp = Blueprint('business', __name__)

@bp.route('/business/<int:business_id>')
def business_detail(business_id):
    """Individual business detail view"""
    
    with get_db_session() as db:
        business = db.query(Business).filter_by(id=business_id).first()
        
        if not business:
            return redirect(url_for('main.dashboard'))
        
        campaign = db.query(Campaign).filter_by(id=business.campaign_id).first()
        
        # Create WhatsApp link
        whatsapp_link = None
        if business.phone_normalized and (business.ai_pitch or business.ai_pitch_edited):
            pitch_text = business.ai_pitch_edited or business.ai_pitch
            whatsapp_link = create_whatsapp_link(business.phone_normalized, pitch_text)
    
    return render_template(
        'business_detail.html', 
        business=business,
        campaign=campaign,
        whatsapp_link=whatsapp_link
    )

@bp.route('/api/business/<int:business_id>/status', methods=['POST'])
def update_business_status(business_id):
    """Update business outreach status"""
    
    try:
        with get_db_session() as db:
            business = db.query(Business).filter_by(id=business_id).first()
            
            if not business:
                return jsonify({'error': 'Business not found'}), 404
            
            new_status = request.json.get('status')
            
            try:
                business.outreach_status = OutreachStatus[new_status.upper()]
                
                # Update contacted_at if status is SENT
                if new_status.upper() == 'SENT' and not business.contacted_at:
                    business.contacted_at = datetime.utcnow()
                    
                    # Update campaign stats
                    campaign = db.query(Campaign).filter_by(id=business.campaign_id).first()
                    stats = campaign.stats
                    stats['contacted'] = stats.get('contacted', 0) + 1
                    campaign.stats = stats
            
            except KeyError:
                return jsonify({'error': 'Invalid status'}), 400
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/business/<int:business_id>/pitch', methods=['PUT'])
def update_pitch(business_id):
    """Update edited pitch"""
    
    try:
        with get_db_session() as db:
            business = db.query(Business).filter_by(id=business_id).first()
            
            if not business:
                return jsonify({'error': 'Business not found'}), 404
            
            edited_pitch = request.json.get('pitch', '').strip()
            business.ai_pitch_edited = edited_pitch
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
