from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
import pandas as pd
from application.database import get_db_session
from application.models import User, Campaign, Business, CampaignStatus
from application.services.cleaner import DataCleaner
from application.services.analyzer import BusinessAnalyzer
from application.utils.file_handler import save_uploaded_file
import config
import os

bp = Blueprint('upload', __name__)

def get_or_create_user(db):
    """Get or create default user using provided session."""
    user = db.query(User).first()
    if not user:
        user = User(name='User', email='user@example.com')
        db.add(user)
    return user

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

@bp.route('/upload', methods=['GET'])
def upload_step1():
    """Step 1: Upload CSV file"""
    return render_template('upload/step1_upload.html')

@bp.route('/upload/process', methods=['POST'])
def upload_process():
    """Process uploaded CSV and show preview"""
    
    if 'file' not in request.files:
        flash('No file provided', 'error')
        return redirect(url_for('upload.upload_step1'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('upload.upload_step1'))
    
    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload a CSV file', 'error')
        return redirect(url_for('upload.upload_step1'))
    
    try:
        # Save file with unique filename
        filepath, original_filename = save_uploaded_file(file)
        
        # Read CSV
        df = pd.read_csv(filepath)
        
        # Check size limit
        if len(df) > config.MAX_CSV_ROWS:
            flash(f'CSV too large. Maximum {config.MAX_CSV_ROWS} rows allowed. Found {len(df)} rows.', 'error')
            os.remove(filepath)
            return redirect(url_for('upload.upload_step1'))
        
        # Get form data and user settings
        campaign_name = request.form.get('campaign_name', original_filename.replace('.csv', ''))
        location = request.form.get('location', 'Kenya')
        
        with get_db_session() as db:
            user = get_or_create_user(db)
            country_code = (user.settings or {}).get('country_code', '+254')
        
        # Detect columns with confidence
        cleaner = DataCleaner(country_code=country_code)
        detected_mappings = cleaner.detect_columns_with_confidence(df)
        
        # Store in session for next step
        session['upload_data'] = {
            'filepath': str(filepath),
            'original_filename': original_filename,
            'campaign_name': campaign_name,
            'location': location,
            'detected_mappings': detected_mappings,
            'total_rows': len(df)
        }
        
        # Get preview data (first 5 rows)
        preview_data = []
        for idx, row in df.head(5).iterrows():
            row_data = {}
            for field, mapping in detected_mappings.items():
                col = mapping['csv_column']
                row_data[field] = str(row.get(col, ''))
            preview_data.append(row_data)
        
        return render_template(
            'upload/step2_preview.html',
            detected_mappings=detected_mappings,
            preview_data=preview_data,
            campaign_name=campaign_name,
            location=location,
            total_rows=len(df)
        )
        
    except Exception as e:
        flash(f'Error processing CSV: {str(e)}', 'error')
        return redirect(url_for('upload.upload_step1'))

@bp.route('/upload/confirm', methods=['POST'])
def upload_confirm():
    """Step 3: Confirm mappings and import data"""
    
    upload_data = session.get('upload_data')
    if not upload_data:
        flash('Session expired. Please upload again.', 'error')
        return redirect(url_for('upload.upload_step1'))
    
    try:
        # Get user-confirmed mappings (or use detected ones)
        # For MVP, we'll use detected mappings directly
        detected_mappings = upload_data['detected_mappings']
        
        # Read CSV
        filepath = upload_data['filepath']
        df = pd.read_csv(filepath)
        
        # Clean and validate data
        with get_db_session() as db:
            user = get_or_create_user(db)
            country_code = (user.settings or {}).get('country_code', '+254')
            cleaner = DataCleaner(country_code=country_code)
            result = cleaner.clean_and_validate_dataframe(df, detected_mappings)
        
        # Create campaign
        with get_db_session() as db:
            user = get_or_create_user(db)
            campaign = Campaign(
                user_id=user.id,
                name=upload_data['campaign_name'],
                location=upload_data['location'],
                csv_filename=upload_data['original_filename'],
                csv_filepath=upload_data['filepath'],
                status=CampaignStatus.PROCESSING,
                column_mapping=detected_mappings,
                skipped_businesses=result['skipped_businesses']
            )
            db.add(campaign)
            db.flush()
            
            # Analyze and save businesses
            analyzer = BusinessAnalyzer(user_skill=(user.settings or {}).get('skill', 'Web Development'))
            opportunities_count = 0
            
            for business_data in result['valid_businesses']:
                # Analyze business
                analysis = analyzer.analyze_business(business_data)
                
                # Only save if opportunity score is reasonable
                if analysis['opportunity_score'] >= config.MIN_OPPORTUNITY_SCORE:
                    opportunities_count += 1
                    
                    business = Business(
                        campaign_id=campaign.id,
                        name=business_data['name'],
                        category=business_data.get('category', ''),
                        address=business_data.get('address', ''),
                        phone_raw=business_data.get('phone_raw', ''),
                        phone_normalized=business_data.get('phone_normalized'),
                        rating=business_data.get('rating'),
                        review_count=business_data.get('review_count', 0),
                        review_snippet=business_data.get('review_snippet'),
                        google_maps_url=business_data.get('google_maps_url'),
                        website_url=business_data.get('website_url'),
                        website_status=analysis['website_status'],
                        opportunity_score=analysis['opportunity_score'],
                        discovery_analysis=analysis['discovery_analysis']
                    )
                    db.add(business)
            
            # Update campaign stats
            campaign.stats = {
                'total_rows': result['stats']['total_rows'],
                'total_businesses': result['stats']['valid_count'],
                'opportunities_found': opportunities_count,
                'contacted': 0,
                'replied': 0,
                'converted': 0,
                'skipped_count': result['stats']['skipped_count']
            }
            campaign.status = CampaignStatus.READY
            
            campaign_id = campaign.id
        
        # Clear session
        session.pop('upload_data', None)
        
        # Show results
        return render_template(
            'upload/step3_confirm.html',
            campaign_id=campaign_id,
            stats=result['stats'],
            skipped_businesses=result['skipped_businesses'],
            opportunities_count=opportunities_count
        )
        
    except Exception as e:
        flash(f'Error importing data: {str(e)}', 'error')
        return redirect(url_for('upload.upload_step1'))
