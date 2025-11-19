import traceback
from typing import Dict, List, Any
from ..base_agent import BaseAgent

class DebuggingAgent(BaseAgent):
    """AI agent specialized in debugging and error resolution"""
    
    def __init__(self, agent_id: str = None):
        capabilities = [
            'error_analysis',
            'debugging',
            'root_cause_analysis',
            'fix_generation',
            'performance_debugging'
        ]
        
        config = {
            'learning_rate': 0.25,
            'autonomy_level': 'high',
            'debugging_approaches': ['log_analysis', 'code_inspection', 'runtime_analysis'],
            'error_categories': ['syntax', 'runtime', 'logical', 'performance']
        }
        
        super().__init__(agent_id, "DebuggingAgent", capabilities, config)
        
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process debugging tasks"""
        error_info = task.get('error_info', {})
        code_context = task.get('code_context', '')
        
        error_analysis = await self._analyze_error(error_info, code_context)
        root_cause = await self._identify_root_cause(error_analysis)
        fixes = await self._generate_fixes(root_cause, code_context)
        prevention_strategy = await self._create_prevention_strategy(error_analysis)
        
        return {
            'status': 'success',
            'error_analysis': error_analysis,
            'root_cause': root_cause,
            'proposed_fixes': fixes,
            'prevention_strategy': prevention_strategy,
            'confidence_level': await self._calculate_confidence(error_analysis, fixes),
            'debugging_steps': await self._suggest_debugging_steps(error_analysis)
        }
    
    async def _analyze_error(self, error_info: Dict, code_context: str) -> Dict[str, Any]:
        """Analyze error information and code context"""
        error_type = error_info.get('type', 'unknown')
        error_message = error_info.get('message', '')
        stack_trace = error_info.get('stack_trace', '')
        
        analysis = {
            'error_type': error_type,
            'error_category': await self._categorize_error(error_type, error_message),
            'likely_causes': await self._identify_likely_causes(error_type, error_message, code_context),
            'severity': await self._assess_severity(error_type, error_message),
            'affected_components': await self._identify_affected_components(stack_trace, code_context),
            'pattern_match': await self._check_known_patterns(error_type, error_message)
        }
        
        return analysis
    
    async def _categorize_error(self, error_type: str, error_message: str) -> str:
        """Categorize the error type"""
        error_lower = error_message.lower()
        
        if 'syntax' in error_type.lower() or 'syntax' in error_lower:
            return 'syntax'
        elif 'memory' in error_lower or 'stack' in error_lower:
            return 'resource'
        elif 'timeout' in error_lower or 'performance' in error_lower:
            return 'performance'
        elif 'import' in error_lower or 'module' in error_lower:
            return 'dependency'
        else:
            return 'logical'
    
    async def _identify_likely_causes(self, error_type: str, error_message: str, code_context: str) -> List[str]:
        """Identify likely causes of the error"""
        causes = []
        
        # Common pattern matching
        if 'NoneType' in error_message and 'object has no attribute' in error_message:
            causes.append("Uninitialized variable or missing return value")
            causes.append("Database query returned None unexpectedly")
            
        if 'index out of range' in error_message.lower():
            causes.append("Array/list access beyond bounds")
            causes.append("Empty collection accessed without check")
            
        if 'key error' in error_message.lower():
            causes.append("Dictionary key does not exist")
            causes.append("Missing configuration or data")
            
        if 'division by zero' in error_message.lower():
            causes.append("Unchecked divisor value")
            causes.append("Missing input validation")
            
        # Context-specific analysis
        if 'import' in error_message.lower():
            causes.append("Missing dependency or incorrect import path")
            causes.append("Virtual environment not activated")
            
        return causes
    
    async def _assess_severity(self, error_type: str, error_message: str) -> str:
        """Assess error severity"""
        critical_indicators = ['memory', 'segmentation', 'core dumped', 'data loss']
        high_indicators = ['timeout', 'performance', 'database connection']
        
        if any(indicator in error_message.lower() for indicator in critical_indicators):
            return 'critical'
        elif any(indicator in error_message.lower() for indicator in high_indicators):
            return 'high'
        else:
            return 'medium'
    
    async def _identify_affected_components(self, stack_trace: str, code_context: str) -> List[str]:
        """Identify affected components from stack trace"""
        components = []
        
        # Simple component extraction from stack trace
        lines = stack_trace.split('\n')
        for line in lines:
            if 'File "' in line:
                # Extract filename
                start = line.find('File "') + 6
                end = line.find('"', start)
                if start < end:
                    filename = line[start:end]
                    components.append(filename.split('/')[-1])  # Just the filename
        
        return list(set(components))  # Remove duplicates
    
    async def _check_known_patterns(self, error_type: str, error_message: str) -> Dict[str, Any]:
        """Check against known error patterns"""
        known_patterns = self.memory.get('error_patterns', {})
        
        for pattern_id, pattern in known_patterns.items():
            if (pattern.get('error_type') == error_type and 
                pattern.get('message_fragment') in error_message):
                return {
                    'pattern_match': True,
                    'pattern_id': pattern_id,
                    'known_solution': pattern.get('solution'),
                    'occurrence_count': pattern.get('count', 0) + 1
                }
        
        return {'pattern_match': False}
    
    async def _identify_root_cause(self, error_analysis: Dict) -> Dict[str, Any]:
        """Identify the root cause of the error"""
        likely_causes = error_analysis.get('likely_causes', [])
        
        return {
            'primary_cause': likely_causes[0] if likely_causes else "Unknown cause",
            'contributing_factors': likely_causes[1:] if len(likely_causes) > 1 else [],
            'confidence': 0.8 if likely_causes else 0.3,
            'investigation_path': await self._suggest_investigation_path(error_analysis)
        }
    
    async def _generate_fixes(self, root_cause: Dict, code_context: str) -> List[Dict[str, Any]]:
        """Generate potential fixes for the error"""
        fixes = []
        primary_cause = root_cause.get('primary_cause', '')
        
        if 'Uninitialized variable' in primary_cause:
            fixes.append({
                'type': 'code_fix',
                'description': 'Add null check before accessing variable',
                'code_example': 'if variable is not None:\n    # use variable',
                'risk': 'low',
                'effort': 'low'
            })
            
        if 'Array/list access beyond bounds' in primary_cause:
            fixes.append({
                'type': 'code_fix',
                'description': 'Add bounds checking before array access',
                'code_example': 'if index < len(array):\n    value = array[index]',
                'risk': 'low',
                'effort': 'low'
            })
            
        if 'Missing dependency' in primary_cause:
            fixes.append({
                'type': 'dependency_fix',
                'description': 'Install missing package',
                'command': 'pip install missing-package',
                'risk': 'low',
                'effort': 'low'
            })
        
        return fixes
    
    async def _create_prevention_strategy(self, error_analysis: Dict) -> Dict[str, Any]:
        """Create strategy to prevent similar errors"""
        error_category = error_analysis.get('error_category')
        
        strategies = {
            'syntax': ['Use linters', 'Enable IDE syntax checking', 'Code review'],
            'resource': ['Add resource monitoring', 'Implement cleanup handlers', 'Use context managers'],
            'performance': ['Add performance tests', 'Monitor resource usage', 'Implement caching'],
            'dependency': ['Use dependency management', 'Pin versions', 'Regular updates'],
            'logical': ['Add unit tests', 'Code review', 'Static analysis']
        }
        
        return {
            'immediate_actions': strategies.get(error_category, ['Code review', 'Add tests']),
            'long_term_strategies': [
                'Implement comprehensive testing',
                'Add monitoring and alerting',
                'Regular code quality assessments'
            ],
            'tools_recommendations': ['pylint', 'pytest', 'logging', 'monitoring_dashboard']
        }
    
    async def _calculate_confidence(self, error_analysis: Dict, fixes: List[Dict]) -> float:
        """Calculate confidence in the analysis and fixes"""
        base_confidence = 0.5
        
        # Increase confidence based on factors
        if error_analysis.get('pattern_match', {}).get('pattern_match'):
            base_confidence += 0.3
            
        if len(error_analysis.get('likely_causes', [])) > 0:
            base_confidence += 0.1
            
        if len(fixes) > 0:
            base_confidence += 0.1
            
        return min(1.0, base_confidence)
    
    async def _suggest_debugging_steps(self, error_analysis: Dict) -> List[str]:
        """Suggest specific debugging steps"""
        steps = [
            "Reproduce the error consistently",
            "Check recent code changes",
            "Examine logs for additional context"
        ]
        
        error_category = error_analysis.get('error_category')
        if error_category == 'performance':
            steps.extend([
                "Profile code performance",
                "Check resource usage patterns",
                "Analyze database queries"
            ])
        elif error_category == 'resource':
            steps.extend([
                "Monitor memory usage",
                "Check for memory leaks",
                "Verify resource cleanup"
            ])
            
        return steps
    
    async def _suggest_investigation_path(self, error_analysis: Dict) -> List[str]:
        """Suggest investigation path for root cause analysis"""
        path = [
            "Review error context and stack trace",
            "Check recent deployments or changes",
            "Verify environment configuration"
        ]
        
        if error_analysis.get('severity') == 'critical':
            path.insert(0, "Immediate incident response")
            path.append("Post-mortem analysis")
            
        return path
    
    async def learn_from_experience(self, experience: Dict[str, Any]):
        """Learn from debugging experiences"""
        if 'error_analysis' in experience and 'root_cause' in experience:
            error_analysis = experience['error_analysis']
            root_cause = experience['root_cause']
            
            # Store successful patterns
            pattern_key = f"{error_analysis.get('error_type')}_{error_analysis.get('error_category')}"
            
            if 'error_patterns' not in self.memory:
                self.memory['error_patterns'] = {}
                
            self.memory['error_patterns'][pattern_key] = {
                'error_type': error_analysis.get('error_type'),
                'error_category': error_analysis.get('error_category'),
                'message_fragment': experience.get('error_info', {}).get('message', '')[:50],
                'solution': root_cause.get('primary_cause'),
                'count': self.memory['error_patterns'].get(pattern_key, {}).get('count', 0) + 1
            }
    
    async def _create_improvement_plan(self, area: str) -> Dict[str, Any]:
        """Create improvement plan for debugging"""
        return {
            'area': area,
            'plan': f"Improve {area} debugging capabilities",
            'actions': [
                f"Study common {area} error patterns",
                "Analyze real debugging cases",
                "Practice root cause analysis techniques"
            ],
            'metrics': ['accuracy', 'resolution_time'],
            'timeline': '1 week'
        }
    
    async def _implement_improvement(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Implement improvement plan"""
        return {
            'plan_id': plan['area'],
            'status': 'implemented',
            'improvement_notes': f"Enhanced {plan['area']} debugging capabilities",
            'expected_impact': 'Faster and more accurate debugging'
        }
