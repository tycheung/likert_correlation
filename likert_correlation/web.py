"""Web interface for Likert scale correlation analysis."""
import tempfile
from pathlib import Path

from flask import Flask, jsonify, render_template, request, Response
from werkzeug.utils import secure_filename

from .analyzer import Analyzer

def create_app(base_dir: Path = None) -> Flask:
    """Create and configure the Flask application."""
    if base_dir is None:
        base_dir = Path(__file__).parent

    app = Flask(__name__,
                template_folder=str(base_dir / 'templates'),
                static_folder=str(base_dir / 'static'))
    
    # Use system temp directory for uploads
    app.config['UPLOAD_FOLDER'] = Path(tempfile.gettempdir()) / 'likert_correlation'
    app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1GB max file size

    # Ensure upload folder exists
    app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)

    # Global analyzer instance
    analyzer = Analyzer()

    @app.route('/')
    def index():
        """Render the main page."""
        return render_template('index.html')

    @app.route('/upload', methods=['POST'])
    def upload_file():
        """Handle file upload and return column names."""
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if file:
            filename = secure_filename(file.filename)
            filepath = app.config['UPLOAD_FOLDER'] / filename
            
            try:
                file.save(filepath)
                columns = analyzer.load_data(filepath)
                filepath.unlink()  # Clean up the file after reading
                return jsonify({'columns': columns})
            except Exception as e:
                if filepath.exists():
                    filepath.unlink()
                return jsonify({'error': str(e)}), 400

    @app.route('/analyze', methods=['POST'])
    def analyze():
        """Perform correlation analysis and return results."""
        data = request.get_json()
        col1 = data.get('col1')
        col2 = data.get('col2')
        
        if not (col1 and col2):
            return jsonify({'error': 'Please select both columns'}), 400
            
        try:
            # Get analysis results
            results = analyzer.analyze(col1, col2)
            fig = analyzer.create_visualizations(col1, col2)
            
            # Convert results to dictionary
            response = {
                'kendall': {
                    'correlation': results.kendall_tau,
                    'p_value': results.kendall_p,
                    'interpretation': results.kendall_interpretation
                },
                'spearman': {
                    'correlation': results.spearman_rho,
                    'p_value': results.spearman_p,
                    'interpretation': results.spearman_interpretation
                },
                'recommendation': {
                    'method': results.recommended_method,
                    'reason': results.recommendation_reason
                },
                'metadata': {
                    'sample_size': results.sample_size,
                    'total_ties': results.total_ties
                },
                'visualizations': fig.to_json()
            }
            
            return jsonify(response)
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @app.route('/shutdown', methods=['GET'])
    def shutdown():
        """Shutdown the Flask server cleanly."""
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        return 'Server shutting down...'

    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint for the frontend."""
        return Response(status=200)

    return app