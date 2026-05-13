"""
Export service for generating PDF and Excel reports
"""

import io
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime


class ExportService:
    """Service for exporting analysis results to various formats"""
    
    @staticmethod
    def to_csv(data: Dict[str, Any], filename: str = "analysis_results.csv") -> Dict[str, str]:
        """
        Export analysis results to CSV format
        
        Returns:
            Dictionary with base64 encoded CSV and filename
        """
        import csv
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(["Parameter", "Value"])
        
        # Write data
        for key, value in data.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    writer.writerow([f"{key}.{sub_key}", sub_value])
            elif isinstance(value, list):
                writer.writerow([key", ".join(str(v) for v in value)])
            else:
                writer.writerow([key, value])
        
        # Encode to base64
        csv_content = output.getvalue()
        csv_base64 = base64.b64encode(csv_content.encode()).decode()
        
        return {
            "content": csv_base64,
            "filename": filename,
            "format": "csv"
        }
    
    @staticmethod
    def to_excel(data: Dict[str, Any], filename: str = "analysis_results.xlsx") -> Dict[str, str]:
        """
        Export analysis results to Excel format
        
        Returns:
            Dictionary with base64 encoded Excel and filename
        """
        try:
            import pandas as pd
            
            # Convert data to DataFrame
            rows = []
            for key, value in data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        rows.append({"Parameter": f"{key}.{sub_key}", "Value": sub_value})
                elif isinstance(value, list):
                    rows.append({"Parameter": key, "Value": str(value)})
                else:
                    rows.append({"Parameter": key, "Value": value})
            
            df = pd.DataFrame(rows)
            
            # Write to Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Results')
            
            # Encode to base64
            excel_content = output.getvalue()
            excel_base64 = base64.b64encode(excel_content).decode()
            
            return {
                "content": excel_base64,
                "filename": filename,
                "format": "xlsx"
            }
        except ImportError:
            # Fallback to CSV if pandas not available
            return ExportService.to_csv(data, filename.replace('.xlsx', '.csv'))
    
    @staticmethod
    def to_json(data: Dict[str, Any], filename: str = "analysis_results.json") -> Dict[str, str]:
        """
        Export analysis results to JSON format
        
        Returns:
            Dictionary with base64 encoded JSON and filename
        """
        import json
        
        json_content = json.dumps(data, indent=2, default=str)
        json_base64 = base64.b64encode(json_content.encode()).decode()
        
        return {
            "content": json_base64,
            "filename": filename,
            "format": "json"
        }
    
    @staticmethod
    def generate_report(
        analysis_type: str,
        parameters: Dict[str, Any],
        results: Dict[str, Any],
        interpretation: str,
        charts: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Generate a comprehensive HTML report
        
        Returns:
            Dictionary with base64 encoded HTML and filename
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Biostats Analysis Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        .header {{
            background: linear-gradient(135deg, #1a237e, #283593);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            margin: 10px 0 0;
            opacity: 0.9;
        }}
        .section {{
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #1a237e;
            border-bottom: 2px solid #1a237e;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f5f5f5;
            font-weight: 600;
        }}
        tr:hover {{
            background-color: #f9f9f9;
        }}
        .chart {{
            text-align: center;
            margin: 20px 0;
        }}
        .chart img {{
            max-width: 100%;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .interpretation {{
            background: #f8f9fa;
            border-left: 4px solid #1a237e;
            padding: 20px;
            margin: 20px 0;
            border-radius: 0 5px 5px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Biostats Analysis Report</h1>
        <p>Generated on {timestamp}</p>
    </div>
    
    <div class="section">
        <h2>Analysis Summary</h2>
        <table>
            <tr>
                <th>Analysis Type</th>
                <td>{analysis_type}</td>
            </tr>
            <tr>
                <th>Timestamp</th>
                <td>{timestamp}</td>
            </tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Parameters</h2>
        <table>
"""
        
        for key, value in parameters.items():
            html += f"""
            <tr>
                <th>{key}</th>
                <td>{value}</td>
            </tr>
"""
        
        html += """
        </table>
    </div>
    
    <div class="section">
        <h2>Results</h2>
        <table>
"""
        
        for key, value in results.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    html += f"""
            <tr>
                <th>{key}.{sub_key}</th>
                <td>{sub_value}</td>
            </tr>
"""
            else:
                html += f"""
            <tr>
                <th>{key}</th>
                <td>{value}</td>
            </tr>
"""
        
        html += """
        </table>
    </div>
"""
        
        if charts:
            html += """
    <div class="section">
        <h2>Visualizations</h2>
"""
            for i, chart in enumerate(charts):
                html += f"""
        <div class="chart">
            <img src="data:image/png;base64,{chart}" alt="Chart {i+1}">
        </div>
"""
            html += """
    </div>
"""
        
        html += f"""
    <div class="section">
        <h2>Interpretation</h2>
        <div class="interpretation">
            {interpretation}
        </div>
    </div>
    
    <div class="footer">
        <p>Generated by Biostats - AI-Powered Biostatistics Platform</p>
        <p>© 2026 MoKangMedical. All rights reserved.</p>
    </div>
</body>
</html>
"""
        
        html_base64 = base64.b64encode(html.encode()).decode()
        
        return {
            "content": html_base64,
            "filename": f"biostats_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            "format": "html"
        }
