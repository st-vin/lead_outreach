from flask import Flask, render_template, redirect, url_for
import config
from application.database import init_db
import os

# Create Flask app
app = Flask(__name__)
app.config.from_object(config)

# Ensure required directories exist
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(config.BASE_DIR / 'data', exist_ok=True)

# Initialize database
init_db()

# Import routes (after app creation to avoid circular imports)
from application.routes import main_routes, upload_routes, campaign_routes, business_routes, settings_routes

# Register blueprints
app.register_blueprint(main_routes.bp)
app.register_blueprint(upload_routes.bp)
app.register_blueprint(campaign_routes.bp)
app.register_blueprint(business_routes.bp)
app.register_blueprint(settings_routes.bp)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('error.html', error='Server error occurred'), 500

@app.route('/favicon.ico')
def favicon():
    # Avoid unnecessary errors/noise for automatic browser favicon requests
    return '', 204

if __name__ == '__main__':
    app.run(debug=config.DEBUG, host='0.0.0.0', port=5008)
