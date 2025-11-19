"""Strategic reports output directory for AI-generated strategic analyses"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class StrategicReportManager:
    """Manager for strategic report output files"""
    
    def __init__(self, base_path: str = "outputs/strategic_reports"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def save_strategic_report(self, report_data: Dict[str, Any], report_name: str):
        """Save strategic report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"strategic_report_{report_name}_{timestamp}.json"
        file_path = self.base_path / filename
        
        # Add metadata
        report_data['metadata'] = {
            'generated_at': datetime.now().isoformat(),
            'report_name': report_name,
            'report_type': report_data.get('report_type', 'strategic_analysis'),
            'ai_system_version': '1.0.0'
        }
        
        # Save report
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        return str(file_path)
    
    def load_strategic_report(self, filename: str) -> Dict[str, Any]:
        """Load strategic report from file"""
        file_path = self.base_path / filename
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_strategic_reports(self) -> List[Dict[str, Any]]:
        """List all strategic reports with basic info"""
        reports = []
        for file_path in self.base_path.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                    reports.append({
                        'filename': file_path.name,
                        'report_name': report_data.get('metadata', {}).get('report_name', 'Unknown'),
                        'report_type': report_data.get('metadata', {}).get('report_type', 'Unknown'),
                        'generated_at': report_data.get('metadata', {}).get('generated_at', 'Unknown'),
                        'file_size': file_path.stat().st_size
                    })
            except:
                continue
        
        return sorted(reports, key=lambda x: x['generated_at'], reverse=True)
    
    def generate_executive_summary(self, report_data: Dict[str, Any]) -> str:
        """Generate executive summary from strategic report"""
        analysis = report_data.get('strategic_analysis', {})
        recommendations = report_data.get('strategic_recommendations', {})
        
        executive_summary = f"""
STRATEGIC REPORT EXECUTIVE SUMMARY
==================================

Report: {report_data.get('metadata', {}).get('report_name', 'Unknown')}
Date: {report_data.get('metadata', {}).get('generated_at', 'Unknown')}

KEY FINDINGS:
{analysis.get('key_findings', 'No key findings provided')}

STRATEGIC ASSESSMENT:
- Current Position: {analysis.get('current_position', 'Not assessed')}
- Competitive Landscape: {analysis.get('competitive_landscape', 'Not assessed')}
- Market Opportunities: {analysis.get('market_opportunities', 'Not identified')}

CRITICAL RECOMMENDATIONS:
{chr(10).join(f"- {rec}" for rec in recommendations.get('critical_recommendations', []))}

EXPECTED IMPACT:
{recommendations.get('expected_impact', 'Impact not quantified')}

RISK ASSESSMENT:
{analysis.get('risk_assessment', 'Risks not assessed')}
"""
        return executive_summary
    
    def generate_implementation_roadmap(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate implementation roadmap from strategic recommendations"""
        recommendations = report_data.get('strategic_recommendations', {})
        
        roadmap = {
            'immediate_actions': recommendations.get('immediate_actions', []),
            'short_term_initiatives': recommendations.get('short_term_initiatives', []),
            'medium_term_strategies': recommendations.get('medium_term_strategies', []),
            'long_term_vision': recommendations.get('long_term_vision', []),
            'success_metrics': recommendations.get('success_metrics', {})
        }
        
        return roadmap
