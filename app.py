from flask import Flask, request, render_template, send_file, flash, redirect, url_for
import json
import os
import tempfile
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'json'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_followers(followers_data, following_data):
    """Extract the core logic from main.py"""
    followers_list = []
    following_list = []
    
    # Extract followers
    for follower in followers_data:
        followers_list.append(follower['string_list_data'][0]['value'])
    
    # Extract following
    for following in following_data["relationships_following"]:
        following_list.append(following["string_list_data"][0]['value'])
    
    # Find people not following back
    people_not_following_back = [i for i in following_list if i not in followers_list]
    
    return people_not_following_back, len(followers_list), len(following_list)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'followers_file' not in request.files or 'following_file' not in request.files:
        flash('Please upload both files')
        return redirect(url_for('index'))
    
    followers_file = request.files['followers_file']
    following_file = request.files['following_file']
    
    if followers_file.filename == '' or following_file.filename == '':
        flash('Please select both files')
        return redirect(url_for('index'))
    
    if not (allowed_file(followers_file.filename) and allowed_file(following_file.filename)):
        flash('Only JSON files are allowed')
        return redirect(url_for('index'))
    
    try:
        # Load JSON data
        followers_data = json.load(followers_file)
        following_data = json.load(following_file)
        
        # Analyze
        not_following_back, followers_count, following_count = analyze_followers(followers_data, following_data)
        
        return render_template('results.html', 
                             not_following_back=not_following_back,
                             followers_count=followers_count,
                             following_count=following_count)
    
    except json.JSONDecodeError:
        flash('Invalid JSON files. Please check your files and try again.')
        return redirect(url_for('index'))
    except KeyError as e:
        flash(f'Invalid JSON structure. Missing key: {e}')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'An error occurred: {str(e)}')
        return redirect(url_for('index'))

@app.route('/download')
def download():
    not_following_back = request.args.getlist('users')
    
    if not not_following_back:
        flash('No data to download')
        return redirect(url_for('index'))
    
    # Create temporary file
    now = datetime.now()
    filename = f"people_not_following_back_{now.month}_{now.day}_{now.year}.txt"
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
    try:
        for i, person in enumerate(not_following_back):
            temp_file.write(f"{i+1}. {person}\n")
        temp_file.close()
        
        return send_file(temp_file.name, as_attachment=True, download_name=filename)
    finally:
        os.unlink(temp_file.name)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)