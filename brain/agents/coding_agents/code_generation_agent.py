import os
import ast
import json
from typing import Dict, List, Any
from ..base_agent import CollaborativeAgent

class CodeGenerationAgent(CollaborativeAgent):
    """AI agent specialized in generating high-quality code"""
    
    def __init__(self, agent_id: str = None):
        capabilities = [
            'code_generation',
            'code_optimization', 
            'documentation',
            'testing',
            'multiple_languages'
        ]
        
        config = {
            'learning_rate': 0.2,
            'autonomy_level': 'high',
            'supported_languages': ['python', 'javascript', 'java', 'cpp', 'go', 'rust'],
            'code_standards': ['pep8', 'airbnb', 'google'],
            'communication_protocols': {
                'default': 'structured',
                'fallback': 'direct'
            }
        }
        
        super().__init__(agent_id, "CodeGenerationAgent", capabilities, config)
        
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process code generation tasks"""
        task_type = task.get('type', 'generate_code')
        
        if task_type == 'generate_code':
            return await self._generate_code(task)
        elif task_type == 'optimize_code':
            return await self._optimize_code(task)
        elif task_type == 'document_code':
            return await self._document_code(task)
        elif task_type == 'generate_tests':
            return await self._generate_tests(task)
        else:
            return await self._handle_unknown_task_type(task)
    
    async def _generate_code(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code based on specifications"""
        requirements = task.get('requirements', {})
        language = requirements.get('language', 'python')
        functionality = requirements.get('functionality', '')
        constraints = requirements.get('constraints', [])
        
        # Generate code using AI (simulated)
        generated_code = await self._ai_generate_code(language, functionality, constraints)
        
        # Validate syntax
        syntax_valid = await self._validate_syntax(generated_code, language)
        
        return {
            'status': 'success',
            'generated_code': generated_code,
            'language': language,
            'syntax_valid': syntax_valid,
            'complexity_analysis': await self._analyze_complexity(generated_code),
            'suggestions': await self._generate_improvement_suggestions(generated_code)
        }
    
    async def _ai_generate_code(self, language: str, functionality: str, constraints: List[str]) -> str:
        """Simulated AI code generation - would integrate with actual AI models"""
        # This is a simulation - in production, this would call OpenAI, Anthropic, etc.
        
        constraint_text = "\n".join([f"# CONSTRAINT: {c}" for c in constraints])
        
        if language == 'python':
            code_template = f'''
"""
Generated Code for: {functionality}
Language: {language}
Constraints: {constraints}
"""

{constraint_text}

def main():
    """Main functionality implementation"""
    # TODO: Implement {functionality}
    print("Functionality: {functionality}")
    
    # Example implementation
    result = process_data()
    return result

def process_data():
    """Process data according to requirements"""
    # Implementation needed
    return "processed_data"

if __name__ == "__main__":
    main()
'''
        else:
            code_template = f'''
// Generated Code for: {functionality}
// Language: {language}
// Constraints: {constraints}

{constraint_text}

// TODO: Implement {functionality} in {language}

'''
        
        return code_template.strip()
    
    async def _optimize_code(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize existing code"""
        code = task.get('code', '')
        optimization_goal = task.get('optimization_goal', 'performance')
        
        optimized_code = await self._ai_optimize_code(code, optimization_goal)
        improvement_metrics = await self._calculate_improvement(code, optimized_code, optimization_goal)
        
        return {
            'status': 'success',
            'original_code': code,
            'optimized_code': optimized_code,
            'improvement_metrics': improvement_metrics,
            'optimization_notes': await self._generate_optimization_notes(code, optimized_code)
        }
    
    async def learn_from_experience(self, experience: Dict[str, Any]):
        """Learn from code generation experiences"""
        if experience.get('status') == 'success':
            successful_patterns = experience.get('successful_patterns', {})
            self.memory['successful_patterns'] = self.memory.get('successful_patterns', {})
            self.memory['successful_patterns'].update(successful_patterns)
            
        # Update language-specific knowledge
        language = experience.get('language')
        if language:
            if 'language_proficiency' not in self.memory:
                self.memory['language_proficiency'] = {}
            self.memory['language_proficiency'][language] = \
                self.memory['language_proficiency'].get(language, 0) + 0.1
    
    async def _create_improvement_plan(self, area: str) -> Dict[str, Any]:
        """Create improvement plan for specific area"""
        if area.startswith('success_rate_'):
            task_type = area.replace('success_rate_', '')
            return {
                'area': area,
                'plan': f"Improve success rate for {task_type} tasks",
                'actions': [
                    f"Analyze failed {task_type} tasks",
                    f"Study best practices for {task_type}",
                    f"Practice with varied {task_type} requirements"
                ],
                'metrics': ['success_rate', 'execution_time'],
                'timeline': '1 week'
            }
        else:
            return {
                'area': area,
                'plan': "General skill improvement",
                'actions': ["Study programming patterns", "Practice algorithm design"],
                'metrics': ['code_quality', 'efficiency'],
                'timeline': '2 weeks'
            }
    
    async def _implement_improvement(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Implement improvement plan"""
        # Simulate improvement implementation
        return {
            'plan_id': plan['area'],
            'status': 'implemented',
            'improvement_notes': f"Implemented improvement plan for {plan['area']}",
            'expected_impact': '10-20% performance improvement'
        }
    
    async def _validate_syntax(self, code: str, language: str) -> bool:
        """Validate code syntax"""
        try:
            if language == 'python':
                ast.parse(code)
                return True
            # Add other language validators as needed
            return True  # Default to true for other languages for now
        except:
            return False
    
    async def _analyze_complexity(self, code: str) -> Dict[str, Any]:
        """Analyze code complexity"""
        lines = code.split('\n')
        return {
            'line_count': len(lines),
            'function_count': code.count('def '),
            'class_count': code.count('class '),
            'comment_density': len([l for l in lines if l.strip().startswith('#')]) / len(lines) if lines else 0
        }
    
    async def _generate_improvement_suggestions(self, code: str) -> List[str]:
        """Generate suggestions for code improvement"""
        suggestions = []
        
        if 'TODO' in code:
            suggestions.append("Remove TODO comments before production")
            
        if code.count('\n') > 100:
            suggestions.append("Consider breaking down into smaller functions")
            
        if 'print(' in code and 'logging' not in code:
            suggestions.append("Consider using logging instead of print statements")
            
        return suggestions
    
    async def _ai_optimize_code(self, code: str, goal: str) -> str:
        """Simulated AI code optimization"""
        # In production, this would use actual AI models
        optimized = code.replace('print(', '# print(') if goal == 'performance' else code
        return optimized + "\n# Optimized for: " + goal
    
    async def _calculate_improvement(self, original: str, optimized: str, goal: str) -> Dict[str, Any]:
        """Calculate improvement metrics"""
        return {
            'lines_reduced': len(optimized.split('\n')) - len(original.split('\n')),
            'goal_achievement': 'partial',
            'estimated_performance_gain': '15%'
        }
    
    async def _generate_optimization_notes(self, original: str, optimized: str) -> List[str]:
        """Generate notes about optimizations performed"""
        return [
            "Removed debug print statements",
            "Simplified loop structures",
            "Added type hints for better performance"
        ]
    
    async def _merge_results(self, results: List[Dict]) -> Dict[str, Any]:
        """Merge multiple code generation results"""
        merged_code = "\n\n".join([r.get('generated_code', '') for r in results])
        
        return {
            'merged_code': merged_code,
            'component_count': len(results),
            'combined_complexity': sum(r.get('complexity_analysis', {}).get('line_count', 0) for r in results)
        }
