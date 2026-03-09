from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from application.database import get_db_session
from application.models import User
from application.utils.crypto import encrypt_api_key, decrypt_api_key
from sqlalchemy.orm.attributes import flag_modified

bp = Blueprint('settings', __name__)

def get_or_create_user(db):
    """Get or create default user using provided session."""
    user = db.query(User).first()
    if not user:
        user = User(name='User', email='user@example.com')
        db.add(user)
    return user

@bp.route('/settings', methods=['GET', 'POST'])
def settings():
    """User settings page with verification"""
    
    if request.method == 'POST':
        try:
            with get_db_session() as db:
                user = get_or_create_user(db)
                
                # Update user fields
                user.name = request.form.get('name', 'User').strip()
                
                # Update settings JSON
                settings = user.settings or {}
                settings['skill'] = request.form.get('skill', 'Web Development')
                settings['pitch_tone'] = request.form.get('pitch_tone', 'professional')
                settings['country_code'] = request.form.get('country_code', '+254')
                
                # Handle API key encryption
                api_key_raw = request.form.get('cerebras_api_key', '').strip()
                if api_key_raw:
                    encrypted = encrypt_api_key(api_key_raw)
                    if encrypted:
                        settings['cerebras_api_key'] = encrypted
                
                # Mark JSON field as modified (required for SQLAlchemy)
                flag_modified(user, 'settings')
                user.settings = settings
                
                # Flush and refresh to verify
                db.flush()
                db.refresh(user)
                
                # Verification: Read back and confirm
                verification_user = db.query(User).filter_by(id=user.id).first()
                
                if verification_user.name != request.form.get('name').strip():
                    raise Exception("Verification failed: name mismatch")
                
                if verification_user.settings.get('skill') != request.form.get('skill'):
                    raise Exception("Verification failed: skill mismatch")
            
            # Success
            flash('✅ Settings saved successfully!', 'success')
            return redirect(url_for('settings.settings'))
            
        except Exception as e:
            flash(f'❌ Error saving settings: {str(e)}', 'error')
            return redirect(url_for('settings.settings'))
    
    with get_db_session() as db:
        # GET request - show current settings
        user = get_or_create_user(db)
        
        # Decrypt API key for display (masked)
        encrypted_key = (user.settings or {}).get('cerebras_api_key', '')
        if encrypted_key:
            decrypted = decrypt_api_key(encrypted_key)
            if decrypted and len(decrypted) > 6:
                masked_key = f"sk-***{decrypted[-6:]}"
                api_key_status = 'valid'
            else:
                masked_key = "Error: Unable to decrypt"
                api_key_status = 'invalid'
        else:
            masked_key = ""
            api_key_status = 'none'
    
        return render_template(
            'settings.html', 
            user=user, 
            masked_key=masked_key,
            api_key_status=api_key_status
        )
