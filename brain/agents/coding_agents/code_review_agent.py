import ast
from typing import Dict, List, Any
from ..base_agent import BaseAgent

class CodeReviewAgent(BaseAgent):
    """AI agent specialized in code review and quality assurance"""
    
    def __init__(self, agent_id: str = None):
        capabilities = [
            'code_review',
            'bug_detection',
            'security_analysis',
            'performance_analysis',
            'best_practices'
        ]
        
        config = {
            'learning_rate': 0.15,
            'autonomy_level': 'medium',
            'review_standards': ['pep8', 'security', 'performance', 'maintainability'],
            'severity_levels': ['critical', 'high', 'medium', 'low']
        }
        
        super().__init__(agent_id, "CodeReviewAgent", capabilities, config)
        
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process code review tasks"""
        code = task.get('code', '')
        review_focus = task.get('review_focus', ['all'])
        
        issues = await self._analyze_code(code, review_focus)
        quality_score = await self._calculate_quality_score(issues)
        recommendations = await self._generate_recommendations(issues)
        
        return {
            'status': 'success',
            'quality_score': quality_score,
            'issues_found': len(issues),
            'issues_by_severity': self._categorize_issues_by_severity(issues),
            'detailed_issues': issues,
            'recommendations': recommendations,
            'overall_assessment': await self._generate_assessment(quality_score, issues)
        }
    
    async def _analyze_code(self, code: str, focus_areas: List[str]) -> List[Dict[str, Any]]:
        """Analyze code for issues"""
        issues = []
        
        try:
            # Parse code for structural analysis
            tree = ast.parse(code)
            
            # Check for various issue types
            if 'security' in focus_areas or 'all' in focus_areas:
                issues.extend(await self._check_security_issues(code, tree))
                
            if 'performance' in focus_areas or 'all' in focus_areas:
                issues.extend(await self._check_performance_issues(code, tree))
                
            if 'maintainability' in focus_areas or 'all' in focus_areas:
                issues.extend(await self._check_maintainability_issues(code, tree))
                
            if 'best_practices' in focus_areas or 'all' in focus_areas:
                issues.extend(await self._check_best_practices(code, tree))
                
        except SyntaxError as e:
            issues.append({
                'type': 'syntax_error',
                'severity': 'critical',
                'message': f'Syntax error: {str(e)}',
                'line': getattr(e, 'lineno', 'unknown'),
                'suggestion': 'Fix syntax error before proceeding with review'
            })
        
        return issues
    
    async def _check_security_issues(self, code: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Check for security issues"""
        issues = []
        security_patterns = [
            ('eval(', 'critical', 'Use of eval is dangerous'),
            ('exec(', 'critical', 'Use of exec is dangerous'),
            ('pickle.loads(', 'high', 'Unpickling untrusted data is dangerous'),
            ('subprocess.call(', 'medium', 'Validate all subprocess inputs'),
            ('os.system(', 'high', 'Use subprocess with validated inputs instead')
        ]
        
        for pattern, severity, message in security_patterns:
            if pattern in code:
                issues.append({
                    'type': 'security',
                    'severity': severity,
                    'message': message,
                    'pattern': pattern,
                    'suggestion': 'Use safer alternatives and validate inputs'
                })
        
        return issues
    
    async def _check_performance_issues(self, code: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Check for performance issues"""
        issues = []
        
        # Check for nested loops
        if code.count('for ') > 2 and code.count('for ') == code.count('    for '):
            issues.append({
                'type': 'performance',
                'severity': 'medium',
                'message': 'Potential nested loops detected',
                'suggestion': 'Consider using more efficient algorithms or vectorization'
            })
        
        # Check for string concatenation in loops
        if 'for ' in code and '+=' in code and 'str' in code:
            issues.append({
                'type': 'performance',
                'severity': 'low',
                'message': 'String concatenation in loop',
                'suggestion': 'Use join() for better performance with large datasets'
            })
        
        return issues
    
    async def _check_maintainability_issues(self, code: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Check for maintainability issues"""
        issues = []
        lines = code.split('\n')
        
        # Check function length
        if len(lines) > 50:
            issues.append({
                'type': 'maintainability',
                'severity': 'medium',
                'message': 'Long function detected',
                'suggestion': 'Break into smaller, focused functions'
            })
        
        # Check for magic numbers
        import re
        magic_numbers = re.findall(r'\b\d{2,}\b', code)  # Numbers with 2+ digits
        if magic_numbers:
            issues.append({
                'type': 'maintainability',
                'severity': 'low',
                'message': f'Magic numbers found: {magic_numbers}',
                'suggestion': 'Define numbers as named constants'
            })
        
        return issues
    
    async def _check_best_practices(self, code: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Check for coding best practices"""
        issues = []
        
        # Check for proper exception handling
        if 'try:' in code and 'except:' in code and 'except Exception:' not in code:
            issues.append({
                'type': 'best_practice',
                'severity': 'medium',
                'message': 'Bare except clause',
                'suggestion': 'Specify exception types to catch'
            })
        
        # Check for proper imports
        if 'from module import *' in code:
            issues.append({
                'type': 'best_practice',
                'severity': 'low',
                'message': 'Wildcard import',
                'suggestion': 'Import specific functions/classes'
            })
        
        return issues
    
    async def _calculate_quality_score(self, issues: List[Dict]) -> float:
        """Calculate overall code quality score"""
        if not issues:
            return 100.0
        
        severity_weights = {'critical': 10, 'high': 5, 'medium': 2, 'low': 1}
        total_weight = sum(severity_weights.values()) * len(issues)  # Max possible
        
        actual_weight = sum(severity_weights[issue['severity']] for issue in issues)
        
        # Convert to percentage (higher is better)
        score = max(0, 100 - (actual_weight / total_weight * 100)) if total_weight > 0 else 100
        return round(score, 2)
    
    def _categorize_issues_by_severity(self, issues: List[Dict]) -> Dict[str, int]:
        """Categorize issues by severity level"""
        categories = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for issue in issues:
            categories[issue['severity']] += 1
            
        return categories
    
    async def _generate_recommendations(self, issues: List[Dict]) -> List[str]:
        """Generate overall recommendations"""
        recommendations = []
        
        critical_count = len([i for i in issues if i['severity'] == 'critical'])
        if critical_count > 0:
            recommendations.append(f"Address {critical_count} critical issues immediately")
        
        high_count = len([i for i in issues if i['severity'] == 'high'])
        if high_count > 0:
            recommendations.append(f"Fix {high_count} high-priority issues soon")
        
        # Add specific recommendations based on issue types
        security_issues = [i for i in issues if i['type'] == 'security']
        if security_issues:
            recommendations.append("Perform security review and testing")
        
        performance_issues = [i for i in issues if i['type'] == 'performance']
        if performance_issues:
            recommendations.append("Conduct performance testing")
        
        return recommendations
    
    async def _generate_assessment(self, quality_score: float, issues: List[Dict]) -> str:
        """Generate overall assessment text"""
        if quality_score >= 90:
            return "Excellent code quality with minor improvements possible"
        elif quality_score >= 75:
            return "Good code quality with some areas for improvement"
        elif quality_score >= 60:
            return "Fair code quality, several improvements needed"
        else:
            return "Poor code quality, significant refactoring recommended"
    
    async def learn_from_experience(self, experience: Dict[str, Any]):
        """Learn from code review experiences"""
        if 'detailed_issues' in experience:
            for issue in experience['detailed_issues']:
                issue_type = issue['type']
                if issue_type not in self.memory:
                    self.memory[issue_type] = []
                self.memory[issue_type].append(issue)
    
    async def _create_improvement_plan(self, area: str) -> Dict[str, Any]:
        """Create improvement plan for code review"""
        return {
            'area': area,
            'plan': f"Improve {area} detection capabilities",
            'actions': [
                f"Study common {area} patterns",
                "Update detection algorithms",
                "Practice with diverse codebases"
            ],
            'metrics': ['detection_accuracy', 'false_positive_rate'],
            'timeline': '1 week'
        }
    
    async def _implement_improvement(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Implement improvement plan"""
        return {
            'plan_id': plan['area'],
            'status': 'implemented',
            'improvement_notes': f"Enhanced {plan['area']} detection capabilities",
            'expected_impact': 'Better issue detection accuracy'
        }
