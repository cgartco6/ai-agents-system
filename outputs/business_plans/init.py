"""Business plans output directory for AI-generated business strategies"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class BusinessPlanManager:
    """Manager for business plan output files"""
    
    def __init__(self, base_path: str = "outputs/business_plans"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def save_business_plan(self, plan_data: Dict[str, Any], plan_name: str):
        """Save business plan to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"business_plan_{plan_name}_{timestamp}.json"
        file_path = self.base_path / filename
        
        # Add metadata
        plan_data['metadata'] = {
            'generated_at': datetime.now().isoformat(),
            'plan_name': plan_name,
            'ai_system_version': '1.0.0'
        }
        
        # Save plan
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(plan_data, f, indent=2, ensure_ascii=False)
        
        return str(file_path)
    
    def load_business_plan(self, filename: str) -> Dict[str, Any]:
        """Load business plan from file"""
        file_path = self.base_path / filename
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_business_plans(self) -> List[Dict[str, Any]]:
        """List all business plans with basic info"""
        plans = []
        for file_path in self.base_path.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    plan_data = json.load(f)
                    plans.append({
                        'filename': file_path.name,
                        'plan_name': plan_data.get('metadata', {}).get('plan_name', 'Unknown'),
                        'generated_at': plan_data.get('metadata', {}).get('generated_at', 'Unknown'),
                        'file_size': file_path.stat().st_size
                    })
            except:
                continue
        
        return sorted(plans, key=lambda x: x['generated_at'], reverse=True)
    
    def generate_executive_summary(self, plan_data: Dict[str, Any]) -> str:
        """Generate executive summary from business plan"""
        executive_summary = f"""
EXECUTIVE SUMMARY: {plan_data.get('business_name', 'Business Plan')}

Overview:
{plan_data.get('executive_summary', {}).get('overview', 'No overview provided')}

Key Objectives:
{chr(10).join(f"- {obj}" for obj in plan_data.get('executive_summary', {}).get('key_objectives', []))}

Expected Outcomes:
{chr(10).join(f"- {outcome}" for outcome in plan_data.get('executive_summary', {}).get('expected_outcomes', []))}

Financial Highlights:
- Initial Investment: {plan_data.get('financial_projections', {}).get('initial_investment', 'Not specified')}
- Projected Revenue Year 1: {plan_data.get('financial_projections', {}).get('year1_revenue', 'Not specified')}
- Break-even Point: {plan_data.get('financial_projections', {}).get('break_even_point', 'Not specified')}
"""
        return executive_summary
