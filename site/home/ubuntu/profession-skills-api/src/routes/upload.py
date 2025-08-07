from flask import Blueprint, request, jsonify, render_template_string, send_from_directory
from flask_cors import cross_origin
import os
import subprocess
from werkzeug.utils import secure_filename

upload_bp = Blueprint('upload', __name__)

UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/info', methods=['GET'])
@cross_origin()
def upload_info():
    """Show information about large file processing"""
    return send_from_directory(
        os.path.join(os.path.dirname(__file__), '..', 'static'),
        'upload_info.html'
    )

@upload_bp.route('/upload', methods=['GET', 'POST'])
@cross_origin()
def upload_file():
    if request.method == 'GET':
        # Return upload form
        upload_form = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Upload Data File</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
                .upload-area { border: 2px dashed #ccc; padding: 40px; text-align: center; margin: 20px 0; }
                .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; margin: 5px; }
                .btn:hover { background: #0056b3; }
                .btn-secondary { background: #6c757d; }
                .btn-secondary:hover { background: #545b62; }
                .status { margin: 20px 0; padding: 10px; border-radius: 5px; }
                .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
                .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
                .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; padding: 15px; border-radius: 5px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <h1>Upload Profession-Skills Data File</h1>
            
            <div class="info">
                <h3>🚀 Optimized for Large Files (10GB+)</h3>
                <p>This system can handle very large data files efficiently using streaming processing and memory optimization.</p>
                <a href="/admin/info" class="btn btn-secondary">📖 Learn about optimizations</a>
            </div>
            
            <p>Upload a new data file to replace the current profession-skills matrix.</p>
            <p><strong>Format:</strong> profession|hard_skills|soft_skills</p>
            
            <form method="post" enctype="multipart/form-data">
                <div class="upload-area">
                    <input type="file" name="file" accept=".txt" required>
                    <p>Select your data file (.txt format)</p>
                    <p><small>Supports files up to 10GB+ in size</small></p>
                </div>
                <button type="submit" class="btn">📤 Upload and Process</button>
            </form>
            
            <div style="margin-top: 40px;">
                <h3>Current Data Statistics</h3>
                <p>Check the current data status by visiting <a href="/api/stats">/api/stats</a></p>
                <a href="/" class="btn btn-secondary">🏠 Back to Main Site</a>
            </div>
        </body>
        </html>
        '''
        return upload_form
    
    if request.method == 'POST':
        # Handle file upload
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            try:
                # Create upload directory
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
                # Save uploaded file
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                
                # Process the uploaded file
                data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
                
                # Process the uploaded file using optimized processor
                import sys
                sys.path.append(os.path.dirname(os.path.dirname(__file__)))
                from optimized_data_processor import process_large_data_file
                
                data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
                
                try:
                    num_professions, num_skills = process_large_data_file(filepath, data_dir)
                    
                    # Clear any cached data in the profession routes
                    try:
                        from src.routes.profession import clear_cache
                        clear_cache()
                    except ImportError:
                        pass
                    
                    return jsonify({
                        'success': True,
                        'message': 'Large data file uploaded and processed successfully',
                        'professions': num_professions,
                        'skills': num_skills
                    })
                except Exception as e:
                    return jsonify({
                        'error': f'Failed to process large data file: {str(e)}'
                    }), 500
                    
            except Exception as e:
                return jsonify({'error': f'Processing failed: {str(e)}'}), 500
        
        return jsonify({'error': 'Invalid file type. Please upload a .txt file'}), 400

