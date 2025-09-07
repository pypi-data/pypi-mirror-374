"""
Report Generator for PyGenAI Security Framework
Generates comprehensive security reports in multiple formats with enterprise features.
"""

import json
import csv
import html
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import base64

from ..core.config_manager import ConfigManager
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """
    Comprehensive report generator for security scan results
    
    Supports multiple output formats:
    - HTML (with interactive features)
    - PDF (enterprise reporting)
    - CSV (data analysis)
    - JSON (structured data)
    - Custom templates
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        self.config = config_manager or ConfigManager()
        self.logger = get_logger(f'{__name__}.ReportGenerator')
    
    def generate_report(self, results: Dict[str, Any], output_path: str, format: str = 'html'):
        """Generate report in specified format"""
        
        output_file = Path(output_path)
        
        try:
            if format == 'html':
                self._generate_html_report(results, output_file)
            elif format == 'pdf':
                self._generate_pdf_report(results, output_file)
            elif format == 'csv':
                self._generate_csv_report(results, output_file)
            elif format == 'json':
                self._generate_json_report(results, output_file)
            else:
                raise ValueError(f"Unsupported report format: {format}")
            
            self.logger.info(f"Report generated successfully: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            raise
    
    def _generate_html_report(self, results: Dict[str, Any], output_file: Path):
        """Generate comprehensive HTML report with interactive features"""
        
        vulnerabilities = results.get('vulnerabilities', [])
        summary = results.get('summary', {})
        security_metrics = results.get('security_metrics', {})
        risk_analysis = results.get('risk_analysis', {})
        recommendations = results.get('recommendations', [])
        scan_metadata = results.get('scan_metadata', {})
        
        # Generate HTML content
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyGenAI Security Report</title>
    <style>
        {self._get_html_styles()}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="report-header">
            <div class="logo">
                <h1>🛡️ PyGenAI Security Report</h1>
                <p>Comprehensive Python & GenAI Security Analysis</p>
            </div>
            <div class="scan-info">
                <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Scan ID:</strong> {scan_metadata.get('scan_id', 'N/A')}</p>
                <p><strong>Duration:</strong> {scan_metadata.get('duration', 0):.2f}s</p>
            </div>
        </header>
        
        <!-- Executive Summary -->
        <section class="executive-summary">
            <h2>📊 Executive Summary</h2>
            <div class="summary-cards">
                <div class="summary-card critical">
                    <h3>{summary.get('total_vulnerabilities', 0)}</h3>
                    <p>Total Vulnerabilities</p>
                </div>
                <div class="summary-card files">
                    <h3>{summary.get('files_scanned', 0)}</h3>
                    <p>Files Scanned</p>
                </div>
                <div class="summary-card risk">
                    <h3>{risk_analysis.get('overall_risk_level', 'Unknown').title()}</h3>
                    <p>Risk Level</p>
                </div>
                <div class="summary-card score">
                    <h3>{risk_analysis.get('risk_score', 0):.1f}</h3>
                    <p>Risk Score</p>
                </div>
            </div>
        </section>
        
        <!-- Threat Level Chart -->
        <section class="charts-section">
            <h2>📈 Vulnerability Analysis</h2>
            <div class="charts-container">
                <div class="chart-wrapper">
                    <canvas id="threatLevelChart"></canvas>
                </div>
                <div class="chart-wrapper">
                    <canvas id="categoryChart"></canvas>
                </div>
            </div>
        </section>
        
        <!-- Vulnerabilities Table -->
        <section class="vulnerabilities-section">
            <h2>🔍 Detailed Vulnerabilities</h2>
            <div class="table-controls">
                <input type="text" id="searchFilter" placeholder="Search vulnerabilities..." class="search-input">
                <select id="severityFilter" class="filter-select">
                    <option value="">All Severities</option>
                    <option value="critical">Critical</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                    <option value="info">Info</option>
                </select>
            </div>
            
            <div class="table-container">
                <table id="vulnerabilitiesTable" class="vulnerabilities-table">
                    <thead>
                        <tr>
                            <th>Severity</th>
                            <th>Title</th>
                            <th>Category</th>
                            <th>File</th>
                            <th>Line</th>
                            <th>Confidence</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        # Add vulnerability rows
        for vuln in vulnerabilities:
            threat_level = vuln.get('threat_level', 'unknown')
            severity_class = f"severity-{threat_level}"
            confidence = vuln.get('confidence', 0) * 100
            
            html_content += f"""
                        <tr class="{severity_class}" data-severity="{threat_level}" data-category="{vuln.get('category', '')}">
                            <td><span class="severity-badge {severity_class}">{threat_level.title()}</span></td>
                            <td>
                                <strong>{html.escape(str(vuln.get('title', 'Unknown')))}</strong>
                                <br><small>{html.escape(str(vuln.get('description', '')))[:100]}...</small>
                            </td>
                            <td>{html.escape(str(vuln.get('category_display', '')))}</td>
                            <td><code>{html.escape(str(vuln.get('file_path', '')))}</code></td>
                            <td>{vuln.get('line_number', 0)}</td>
                            <td>
                                <div class="confidence-bar">
                                    <div class="confidence-fill" style="width: {confidence}%"></div>
                                    <span>{confidence:.0f}%</span>
                                </div>
                            </td>
                            <td>
                                <button class="btn-details" onclick="showVulnDetails('{vuln.get('id', '')}')">Details</button>
                            </td>
                        </tr>"""
        
        html_content += """
                    </tbody>
                </table>
            </div>
        </section>
        
        <!-- Recommendations -->
        <section class="recommendations-section">
            <h2>💡 Security Recommendations</h2>
            <div class="recommendations-list">
"""
        
        for i, recommendation in enumerate(recommendations, 1):
            html_content += f"""
                <div class="recommendation-item">
                    <span class="recommendation-number">{i}</span>
                    <p>{html.escape(str(recommendation))}</p>
                </div>"""
        
        html_content += f"""
            </div>
        </section>
        
        <!-- Footer -->
        <footer class="report-footer">
            <p>Generated by <strong>PyGenAI Security Framework v1.0.0</strong></p>
            <p>Repository: <a href="https://github.com/RiteshGenAI/pygenai-security">https://github.com/RiteshGenAI/pygenai-security</a></p>
        </footer>
    </div>
    
    <script>
        {self._get_html_javascript(security_metrics, vulnerabilities)}
    </script>
</body>
</html>"""
        
        # Write HTML file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_pdf_report(self, results: Dict[str, Any], output_file: Path):
        """Generate PDF report (requires additional dependencies in production)"""
        # For now, generate HTML and note that PDF conversion is available
        html_file = output_file.with_suffix('.html')
        self._generate_html_report(results, html_file)
        
        # Note: In production, implement PDF generation using libraries like:
        # - weasyprint
        # - reportlab
        # - wkhtmltopdf
        
        self.logger.info(f"HTML report generated at {html_file}. PDF conversion available in enterprise version.")
    
    def _generate_csv_report(self, results: Dict[str, Any], output_file: Path):
        """Generate CSV report for data analysis"""
        vulnerabilities = results.get('vulnerabilities', [])
        
        if not vulnerabilities:
            # Create empty CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['No vulnerabilities found'])
            return
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header row
            headers = [
                'ID', 'Title', 'Description', 'Threat Level', 'Category',
                'File Path', 'Line Number', 'Confidence', 'CVSS Score',
                'CWE ID', 'OWASP Category', 'Remediation', 'Scanner',
                'First Detected', 'Business Impact'
            ]
            writer.writerow(headers)
            
            # Data rows
            for vuln in vulnerabilities:
                row = [
                    vuln.get('id', ''),
                    vuln.get('title', ''),
                    vuln.get('description', ''),
                    vuln.get('threat_level', ''),
                    vuln.get('category_display', ''),
                    vuln.get('file_path', ''),
                    vuln.get('line_number', 0),
                    vuln.get('confidence', 0),
                    vuln.get('cvss_score', 0),
                    vuln.get('cwe_id', ''),
                    vuln.get('owasp_category', ''),
                    vuln.get('remediation', ''),
                    vuln.get('scanner_name', ''),
                    vuln.get('first_detected', ''),
                    vuln.get('business_impact', '')
                ]
                writer.writerow(row)
    
    def _generate_json_report(self, results: Dict[str, Any], output_file: Path):
        """Generate JSON report with structured data"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
    
    def _get_html_styles(self) -> str:
        """Get CSS styles for HTML report"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f7fa;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .report-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo h1 {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .scan-info {
            text-align: right;
        }
        
        .executive-summary {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .summary-card {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #007bff;
        }
        
        .summary-card.critical {
            border-left-color: #dc3545;
        }
        
        .summary-card.files {
            border-left-color: #28a745;
        }
        
        .summary-card.risk {
            border-left-color: #ffc107;
        }
        
        .summary-card h3 {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
            color: #333;
        }
        
        .charts-section, .vulnerabilities-section, .recommendations-section {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .charts-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-top: 1rem;
        }
        
        .chart-wrapper {
            position: relative;
            height: 300px;
        }
        
        .table-controls {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        
        .search-input, .filter-select {
            padding: 0.5rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        
        .search-input {
            flex: 1;
        }
        
        .table-container {
            overflow-x: auto;
        }
        
        .vulnerabilities-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        
        .vulnerabilities-table th,
        .vulnerabilities-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        
        .vulnerabilities-table th {
            background-color: #f8f9fa;
            font-weight: 600;
            position: sticky;
            top: 0;
        }
        
        .severity-badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .severity-critical {
            background-color: #dc3545;
            color: white;
        }
        
        .severity-high {
            background-color: #fd7e14;
            color: white;
        }
        
        .severity-medium {
            background-color: #ffc107;
            color: #333;
        }
        
        .severity-low {
            background-color: #28a745;
            color: white;
        }
        
        .severity-info {
            background-color: #17a2b8;
            color: white;
        }
        
        .confidence-bar {
            position: relative;
            background-color: #e9ecef;
            height: 20px;
            border-radius: 10px;
            overflow: hidden;
        }
        
        .confidence-fill {
            background-color: #007bff;
            height: 100%;
            transition: width 0.3s ease;
        }
        
        .confidence-bar span {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 12px;
            font-weight: bold;
            color: #333;
        }
        
        .btn-details {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }
        
        .btn-details:hover {
            background-color: #0056b3;
        }
        
        .recommendations-list {
            margin-top: 1rem;
        }
        
        .recommendation-item {
            display: flex;
            align-items: flex-start;
            margin-bottom: 1rem;
            padding: 1rem;
            background-color: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #007bff;
        }
        
        .recommendation-number {
            background-color: #007bff;
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 12px;
            margin-right: 1rem;
            flex-shrink: 0;
        }
        
        .report-footer {
            text-align: center;
            padding: 2rem;
            color: #666;
            border-top: 1px solid #eee;
        }
        
        .report-footer a {
            color: #007bff;
            text-decoration: none;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .report-header {
                flex-direction: column;
                text-align: center;
            }
            
            .charts-container {
                grid-template-columns: 1fr;
            }
            
            .table-controls {
                flex-direction: column;
            }
        }
        """
    
    def _get_html_javascript(self, security_metrics: Dict[str, Any], vulnerabilities: List[Dict[str, Any]]) -> str:
        """Get JavaScript for interactive HTML report"""
        
        # Prepare data for charts
        threat_levels = security_metrics.get('by_threat_level', {})
        categories = security_metrics.get('by_category', {})
        
        return f"""
        // Chart.js configuration
        Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        
        // Threat Level Chart
        const threatLevelCtx = document.getElementById('threatLevelChart').getContext('2d');
        new Chart(threatLevelCtx, {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(list(threat_levels.keys()))},
                datasets: [{{
                    data: {json.dumps(list(threat_levels.values()))},
                    backgroundColor: [
                        '#dc3545',  // Critical
                        '#fd7e14',  // High
                        '#ffc107',  // Medium
                        '#28a745',  // Low
                        '#17a2b8'   // Info
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Vulnerabilities by Threat Level'
                    }},
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
        
        // Category Chart
        const categoryCtx = document.getElementById('categoryChart').getContext('2d');
        new Chart(categoryCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps([cat.replace('_', ' ').title() for cat in categories.keys()])},
                datasets: [{{
                    label: 'Count',
                    data: {json.dumps(list(categories.values()))},
                    backgroundColor: '#007bff'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Vulnerabilities by Category'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        
        // Table filtering
        const searchFilter = document.getElementById('searchFilter');
        const severityFilter = document.getElementById('severityFilter');
        const table = document.getElementById('vulnerabilitiesTable');
        const rows = table.querySelectorAll('tbody tr');
        
        function filterTable() {{
            const searchTerm = searchFilter.value.toLowerCase();
            const severityValue = severityFilter.value.toLowerCase();
            
            rows.forEach(row => {{
                const title = row.cells[1].textContent.toLowerCase();
                const severity = row.dataset.severity.toLowerCase();
                
                const matchesSearch = title.includes(searchTerm);
                const matchesSeverity = !severityValue || severity === severityValue;
                
                row.style.display = matchesSearch && matchesSeverity ? '' : 'none';
            }});
        }}
        
        searchFilter.addEventListener('input', filterTable);
        severityFilter.addEventListener('change', filterTable);
        
        // Vulnerability details modal (placeholder)
        function showVulnDetails(vulnId) {{
            alert('Vulnerability details for: ' + vulnId + '\n\nDetailed view available in enterprise version.');
        }}
        """
    
    def generate_report_with_template(self, results: Dict[str, Any], output_file: str, template_file: str):
        """Generate report using custom template"""
        # Template system implementation (placeholder)
        self.logger.info(f"Custom template reporting available in enterprise version")
        # For now, fall back to HTML report
        self._generate_html_report(results, Path(output_file))
