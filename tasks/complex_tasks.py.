from typing import Dict, List, Any
from enum import Enum
import uuid

class ComplexTaskType(Enum):
    MULTI_AGENT_COLLABORATION = "multi_agent_collaboration"
    WORKFLOW_ORCHESTRATION = "workflow_orchestration"
    DECISION_TREE_EXECUTION = "decision_tree_execution"
    ITERATIVE_REFINEMENT = "iterative_refinement"
    PARALLEL_PROCESSING = "parallel_processing"

class ComplexTaskBuilder:
    """Builder for complex multi-step tasks"""
    
    def __init__(self, task_manager):
        self.task_manager = task_manager
        self.complex_tasks = {}
    
    async def create_multi_agent_project(self, project_definition: Dict[str, Any]) -> str:
        """Create a complex project requiring multiple agents"""
        project_id = f"project_{uuid.uuid4().hex[:8]}"
        
        # Define task sequence based on project type
        if project_definition['type'] == 'software_development':
            tasks = await self._create_software_development_tasks(project_definition)
        elif project_definition['type'] == 'business_plan':
            tasks = await self._create_business_plan_tasks(project_definition)
        elif project_definition['type'] == 'market_analysis':
            tasks = await self._create_market_analysis_tasks(project_definition)
        else:
            tasks = await self._create_generic_project_tasks(project_definition)
        
        # Store complex task definition
        self.complex_tasks[project_id] = {
            'project_id': project_id,
            'definition': project_definition,
            'tasks': tasks,
            'status': 'planning',
            'current_step': 0,
            'results': {},
            'created_at': self._current_timestamp()
        }
        
        # Start execution
        await self._execute_complex_task(project_id)
        
        return project_id
    
    async def _create_software_development_tasks(self, project: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create task sequence for software development project"""
        requirements = project['requirements']
        
        return [
            {
                'step': 1,
                'name': 'Requirements Analysis',
                'type': 'analyze_requirements',
                'agent_type': 'business_analysis',
                'payload': {
                    'requirements': requirements,
                    'required_capabilities': ['requirements_analysis', 'domain_knowledge']
                },
                'dependencies': [],
                'priority': 'high'
            },
            {
                'step': 2,
                'name': 'System Architecture Design',
                'type': 'design_system',
                'agent_type': 'architecture',
                'payload': {
                    'requirements': requirements,
                    'required_capabilities': ['system_design', 'architecture_patterns']
                },
                'dependencies': ['step_1'],
                'priority': 'high'
            },
            {
                'step': 3,
                'name': 'Database Design',
                'type': 'design_database',
                'agent_type': 'architecture',
                'payload': {
                    'requirements': requirements,
                    'required_capabilities': ['database_design', 'data_modeling']
                },
                'dependencies': ['step_2'],
                'priority': 'medium'
            },
            {
                'step': 4,
                'name': 'API Design',
                'type': 'design_apis',
                'agent_type': 'architecture',
                'payload': {
                    'requirements': requirements,
                    'required_capabilities': ['api_design', 'rest_principles']
                },
                'dependencies': ['step_2'],
                'priority': 'medium'
            },
            {
                'step': 5,
                'name': 'Core Module Development',
                'type': 'generate_code',
                'agent_type': 'code_generation',
                'payload': {
                    'requirements': requirements,
                    'component': 'core_module',
                    'required_capabilities': ['code_generation', 'backend_development']
                },
                'dependencies': ['step_2', 'step_3', 'step_4'],
                'priority': 'high'
            },
            {
                'step': 6,
                'name': 'UI/UX Development',
                'type': 'generate_code',
                'agent_type': 'code_generation',
                'payload': {
                    'requirements': requirements,
                    'component': 'frontend',
                    'required_capabilities': ['code_generation', 'frontend_development']
                },
                'dependencies': ['step_2', 'step_4'],
                'priority': 'medium'
            },
            {
                'step': 7,
                'name': 'Integration Testing',
                'type': 'test_integration',
                'agent_type': 'code_review',
                'payload': {
                    'components': ['core_module', 'frontend'],
                    'required_capabilities': ['testing', 'integration']
                },
                'dependencies': ['step_5', 'step_6'],
                'priority': 'medium'
            },
            {
                'step': 8,
                'name': 'Documentation',
                'type': 'document_code',
                'agent_type': 'code_generation',
                'payload': {
                    'components': ['all'],
                    'required_capabilities': ['documentation', 'technical_writing']
                },
                'dependencies': ['step_5', 'step_6'],
                'priority': 'low'
            }
        ]
    
    async def _create_business_plan_tasks(self, project: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create task sequence for business plan development"""
        return [
            {
                'step': 1,
                'name': 'Market Analysis',
                'type': 'analyze_market',
                'agent_type': 'market_analysis',
                'payload': {
                    'market_definition': project.get('market_definition', {}),
                    'required_capabilities': ['market_research', 'competitor_analysis']
                },
                'dependencies': [],
                'priority': 'high'
            },
            {
                'step': 2,
                'name': 'Financial Projections',
                'type': 'financial_analysis',
                'agent_type': 'financial_analysis',
                'payload': {
                    'market_data': 'from_step_1',
                    'required_capabilities': ['financial_modeling', 'forecasting']
                },
                'dependencies': ['step_1'],
                'priority': 'high'
            },
            {
                'step': 3,
                'name': 'Strategic Planning',
                'type': 'develop_strategy',
                'agent_type': 'strategic_planning',
                'payload': {
                    'context': project.get('context', {}),
                    'required_capabilities': ['strategic_planning', 'vision_development']
                },
                'dependencies': ['step_1', 'step_2'],
                'priority': 'high'
            },
            {
                'step': 4,
                'name': 'Risk Assessment',
                'type': 'assess_risks',
                'agent_type': 'risk_management',
                'payload': {
                    'plan_data': 'from_step_3',
                    'required_capabilities': ['risk_assessment', 'mitigation_planning']
                },
                'dependencies': ['step_3'],
                'priority': 'medium'
            },
            {
                'step': 5,
                'name': 'Executive Summary',
                'type': 'create_summary',
                'agent_type': 'business_plan',
                'payload': {
                    'all_data': 'from_previous_steps',
                    'required_capabilities': ['business_writing', 'summarization']
                },
                'dependencies': ['step_1', 'step_2', 'step_3', 'step_4'],
                'priority': 'medium'
            }
        ]
    
    async def _execute_complex_task(self, project_id: str):
        """Execute a complex task by managing its step sequence"""
        complex_task = self.complex_tasks[project_id]
        complex_task['status'] = 'executing'
        
        # Create individual tasks for each step
        task_ids = {}
        for step in complex_task['tasks']:
            task_id = await self.task_manager.create_task(
                task_type=step['type'],
                payload=step['payload'],
                priority=self._parse_priority(step['priority']),
                dependencies=[task_ids[dep] for dep in step['dependencies'] if dep in task_ids]
            )
            task_ids[f"step_{step['step']}"] = task_id
        
        complex_task['task_ids'] = task_ids
        complex_task['current_step'] = 1
        
        # Start monitoring task progress
        asyncio.create_task(self._monitor_complex_task(project_id))
    
    async def _monitor_complex_task(self, project_id: str):
        """Monitor the progress of a complex task"""
        complex_task = self.complex_tasks[project_id]
        
        while complex_task['status'] in ['executing', 'paused']:
            await asyncio.sleep(5)  # Check every 5 seconds
            
            # Check task statuses
            completed_steps = 0
            failed_steps = 0
            results = {}
            
            for step_key, task_id in complex_task['task_ids'].items():
                task_status = await self.task_manager.get_task_status(task_id)
                if task_status:
                    if task_status['status'] == 'completed':
                        completed_steps += 1
                        results[step_key] = task_status['result']
                    elif task_status['status'] == 'failed':
                        failed_steps += 1
            
            total_steps = len(complex_task['tasks'])
            complex_task['current_step'] = completed_steps + 1
            complex_task['results'] = results
            
            # Update overall status
            if completed_steps == total_steps:
                complex_task['status'] = 'completed'
                break
            elif failed_steps > 0 and complex_task['status'] != 'paused':
                complex_task['status'] = 'paused'
                # Implement retry or error handling logic here
            
            progress = (completed_steps / total_steps) * 100
            complex_task['progress'] = progress
    
    async def get_complex_task_status(self, project_id: str) -> Dict[str, Any]:
        """Get status of a complex task"""
        if project_id not in self.complex_tasks:
            return {'error': 'Project not found'}
        
        complex_task = self.complex_tasks[project_id]
        
        return {
            'project_id': project_id,
            'status': complex_task['status'],
            'progress': complex_task.get('progress', 0),
            'current_step': complex_task['current_step'],
            'total_steps': len(complex_task['tasks']),
            'created_at': complex_task['created_at'],
            'results_summary': self._summarize_results(complex_task['results'])
        }
    
    def _summarize_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize complex task results"""
        summary = {
            'completed_steps': len(results),
            'key_deliverables': [],
            'overall_quality': 0.0,
            'issues_found': 0
        }
        
        for step_key, result in results.items():
            if result and isinstance(result, dict):
                if 'status' in result and result['status'] == 'success':
                    summary['key_deliverables'].append(f"Step {step_key}: Success")
                    
                    # Calculate quality score (simplified)
                    if 'quality_score' in result:
                        summary['overall_quality'] += result['quality_score']
                    else:
                        summary['overall_quality'] += 0.8  # Default quality
                
                if 'issues_found' in result:
                    summary['issues_found'] += result['issues_found']
        
        if summary['completed_steps'] > 0:
            summary['overall_quality'] /= summary['completed_steps']
        
        return summary
    
    def _parse_priority(self, priority_str: str):
        """Parse priority string to TaskPriority enum"""
        from .task_manager import TaskPriority
        
        priority_map = {
            'low': TaskPriority.LOW,
            'medium': TaskPriority.MEDIUM,
            'high': TaskPriority.HIGH,
            'critical': TaskPriority.CRITICAL
        }
        
        return priority_map.get(priority_str.lower(), TaskPriority.MEDIUM)
    
    def _current_timestamp(self):
        """Get current timestamp string"""
        from datetime import datetime
        return datetime.now().isoformat()
