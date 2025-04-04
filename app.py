from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from blueprints.auth import auth_bp
from blueprints.api import api_bp
from blueprints.profile import profile_bp
from blueprints.email_api import email_api_bp
from config import port, debug, flask_secret_key, email_api_url, current_year

def create_app():
    app = Flask(__name__)
    
    # Configure app settings here
    app.config['SECRET_KEY'] = flask_secret_key
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(email_api_bp)
    
    return app

app = create_app()

@app.route('/')
def home():
    return render_template('landing.html', email_api_url=email_api_url)

@app.route('/dashboard')
@app.route('/dashboard/<path:page>')
def dashboard(page='dashboard'):
    if not session.get('user_id'):
        return redirect(url_for('auth'))
    return render_template('user_dashboard.html', page=page, email_api_url=email_api_url)

@app.route('/auth')
@app.route('/auth/<path:page>')
def auth(page='login'):
    uid = session.get('user_id')
    if uid:
        return redirect(url_for('dashboard'))
    return render_template('auth.html', page=page, email_api_url=email_api_url)

@app.route('/logout')
def logout():
    return redirect(url_for('auth.logout'))

@app.route('/user_docs')
def user_docs():
    return render_template('dashboard_user/user_docs.html')

@app.route('/template/<path:page>', methods=['GET'])
def templates(page):
    return render_template(f'{page}.html', current_year = current_year)


if __name__ == '__main__':
    app.run(port=port, host='0.0.0.0', debug=debug)