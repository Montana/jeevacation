import json
import csv
import logging
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ReportGenerator:
    
    def generate_html_report(
        self,
        results: List[Dict[str, Any]],
        output_path: str = "epstein_report.html"
    ) -> str:
        total_contacts = len(results)
        total_mentions = sum(r['total_mentions'] for r in results)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Epstein Document Search Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background:
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid
        }}
        
        h1 {{
            color:
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .report-date {{
            color:
            font-size: 0.9em;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .summary-card {{
            background: linear-gradient(135deg,
            color: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
        }}
        
        .summary-value {{
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .summary-label {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .contact-card {{
            background: white;
            border: 2px solid
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            transition: all 0.3s;
        }}
        
        .contact-card:hover {{
            border-color:
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
        }}
        
        .contact-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 15px;
        }}
        
        .contact-name {{
            font-size: 1.8em;
            font-weight: bold;
            color:
        }}
        
        .contact-meta {{
            color:
            margin-top: 5px;
        }}
        
        .badge {{
            display: inline-block;
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: bold;
            background:
            color: white;
        }}
        
        .ai-section {{
            background:
            padding: 20px;
            border-radius: 8px;
            margin: 15px 0;
        }}
        
        .ai-section h4 {{
            color:
            margin-bottom: 10px;
        }}
        
        .key-facts {{
            list-style: none;
            margin-top: 10px;
        }}
        
        .key-facts li {{
            padding: 5px 0;
            padding-left: 20px;
            position: relative;
        }}
        
        .key-facts li:before {{
            content: "→";
            position: absolute;
            left: 0;
            color:
            font-weight: bold;
        }}
        
        .excerpts {{
            margin-top: 20px;
        }}
        
        .excerpt {{
            background:
            border-left: 4px solid
            padding: 15px;
            margin: 10px 0;
            font-size: 0.95em;
            line-height: 1.6;
        }}
        
        .pdf-link {{
            display: inline-block;
            margin-top: 10px;
            color:
            text-decoration: none;
            font-weight: bold;
        }}
        
        .pdf-link:hover {{
            text-decoration: underline;
        }}
        
        .disclaimer {{
            background:
            border: 2px solid
            padding: 20px;
            border-radius: 10px;
            margin-top: 40px;
        }}
        
        .disclaimer strong {{
            color:
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Epstein Document Search Report</h1>
            <p class="report-date">Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <div class="summary-value">{total_contacts}</div>
                <div class="summary-label">Contacts with Matches</div>
            </div>
            <div class="summary-card">
                <div class="summary-value">{total_mentions}</div>
                <div class="summary-label">Total Mentions</div>
            </div>
        </div>
            
            excerpts_html = ""
            for excerpt_result in result['results'][:5]:
                excerpts_html += f"""
                <div class="excerpt">
                    {excerpt_result['excerpt']}
                    <a href="{excerpt_result['pdf_url']}" target="_blank" class="pdf-link">
                        📄 View PDF Document
                    </a>
                </div>
        
        html += """
        <div class="disclaimer">
            <strong>⚠️ Important Disclaimer:</strong>
            <p>A mention in these documents does not imply wrongdoing. Many individuals appear as witnesses, 
            employees, legal professionals, or in other neutral contexts. This report is for informational 
            purposes only. Please review the full document context before drawing any conclusions.</p>
        </div>
    </div>
</body>
</html>
        Generate JSON report.
        
        Args:
            results: List of search results
            output_path: Path to save the report
            
        Returns:
            Path to the generated report
        Generate CSV report.
        
        Args:
            results: List of search results
            output_path: Path to save the report
            
        Returns:
            Path to the generated report
