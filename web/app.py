import os
import asyncio
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
import json
import logging

from ..core.search_client import EpsteinSearchClient, ContactMatch
from ..core.linkedin_parser import LinkedInParser, LinkedInContact
from ..ai.analyzer import AIAnalyzer
from ..database.models import Database, Contact, Match, SearchResult
from ..utils.report_generator import ReportGenerator
from ..utils.network_graph import NetworkGraphGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'data/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

CORS(app)

db = Database()
db.create_tables()
ai_analyzer = AIAnalyzer()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'File must be a CSV'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(filepath)
        
        contacts = LinkedInParser.parse_csv(filepath)
        
        session['contacts_file'] = filepath
        session['contacts_count'] = len(contacts)
        
        return jsonify({
            'success': True,
            'contacts_count': len(contacts),
            'contacts': [
                {
                    'full_name': c.full_name,
                    'company': c.company,
                    'position': c.position
                }
                for c in contacts[:10]
            ]
        })
        
    except Exception as e:
        logger.error(f"Error uploading CSV: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    
    if 'contacts_file' not in session:
        return jsonify({'error': 'No contacts file uploaded'}), 400
    
    try:
        contacts = LinkedInParser.parse_csv(session['contacts_file'])
        
        filter_common = data.get('filter_common_names', True)
        if filter_common:
            contacts = LinkedInParser.filter_common_names(contacts)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(run_search(contacts, data))
        loop.close()
        
        return jsonify({
            'success': True,
            'results': results,
            'total_contacts': len(contacts),
            'contacts_with_matches': len([r for r in results if r['total_mentions'] > 0])
        })
        
    except Exception as e:
        logger.error(f"Error performing search: {e}")
        return jsonify({'error': str(e)}), 500


async def run_search(contacts: list, options: dict):
    results = []
    use_ai = options.get('use_ai_analysis', False)
    
    async with EpsteinSearchClient() as client:
        names = [c.full_name for c in contacts]
        
        search_results = await client.batch_search(names, batch_size=10)
        
        for contact in contacts:
            contact_results = search_results.get(contact.full_name, [])
            
            if not contact_results:
                continue
            
            excerpts = [r.get('excerpt', '') for r in contact_results]
            
            ai_analysis = None
            false_positive_score = 0.0
            
            if use_ai and excerpts:
                ai_analysis = ai_analyzer.analyze_mentions(
                    contact.full_name,
                    excerpts,
                    contact.position,
                    contact.company
                )
                false_positive_score = ai_analyzer.calculate_false_positive_score(
                    contact.full_name,
                    excerpts,
                    contact.position,
                    contact.company
                )
            
            result = {
                'name': contact.full_name,
                'company': contact.company,
                'position': contact.position,
                'email': contact.email,
                'total_mentions': len(contact_results),
                'false_positive_score': false_positive_score,
                'results': [
                    {
                        'document_path': r.get('file_path', ''),
                        'excerpt': r.get('excerpt', ''),
                        'pdf_url': client.get_pdf_url(r.get('file_path', ''))
                    }
                    for r in contact_results
                ]
            }
            
            if ai_analysis:
                result['ai_analysis'] = {
                    'category': ai_analysis.category,
                    'sentiment': ai_analysis.sentiment,
                    'summary': ai_analysis.summary,
                    'confidence': ai_analysis.confidence,
                    'key_facts': ai_analysis.key_facts
                }
            
            results.append(result)
    
    results.sort(key=lambda x: x['total_mentions'], reverse=True)
    
    return results


@app.route('/api/export/html', methods=['POST'])
def export_html():
    data = request.json
    results = data.get('results', [])
    
    try:
        generator = ReportGenerator()
        html_path = generator.generate_html_report(results)
        
        return send_file(html_path, as_attachment=True, download_name='epstein_report.html')
        
    except Exception as e:
        logger.error(f"Error exporting HTML: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/json', methods=['POST'])
def export_json():
    data = request.json
    results = data.get('results', [])
    
    try:
        json_path = 'data/exports/results.json'
        os.makedirs('data/exports', exist_ok=True)
        
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        return send_file(json_path, as_attachment=True, download_name='epstein_results.json')
        
    except Exception as e:
        logger.error(f"Error exporting JSON: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/network-graph', methods=['POST'])
def network_graph():
    data = request.json
    results = data.get('results', [])
    
    try:
        generator = NetworkGraphGenerator()
        graph_html = generator.generate_interactive_graph(results)
        
        return jsonify({
            'success': True,
            'html': graph_html
        })
        
    except Exception as e:
        logger.error(f"Error generating network graph: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        db_session = db.get_session()
        
        stats = {
            'total_contacts': db_session.query(Contact).count(),
            'total_matches': db_session.query(Match).count(),
            'total_results': db_session.query(SearchResult).count(),
        }
        
        db_session.close()
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500


def main():
    app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == '__main__':
    main()
