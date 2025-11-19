import asyncio
from typing import Dict, List, Any, Optional
from .task_manager import TaskManager, TaskPriority
from .complex_tasks import ComplexTaskBuilder

class TaskExecutor:
    """High-level task executor that coordinates between task manager and complex tasks"""
    
    def __init__(self, agent_registry):
        self.agent_registry = agent_registry
        self.task_manager = TaskManager()
        self.complex_builder = ComplexTaskBuilder(self.task_manager)
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize the task executor"""
        if not self.is_initialized:
            await self.task_manager.start_workers(self.agent_registry)
            self.is_initialized = True
    
    async def shutdown(self):
        """Shutdown the task executor"""
        if self.is_initialized:
            await self.task_manager.stop_workers()
            self.is_initialized = False
    
    async def execute_simple_task(self, task_type: str, payload: Dict[str, Any], 
                                priority: TaskPriority = TaskPriority.MEDIUM) -> str:
        """Execute a simple single-agent task"""
        return await self.task_manager.create_task(task_type, payload, priority)
    
    async def execute_complex_project(self, project_definition: Dict[str, Any]) -> str:
        """Execute a complex multi-agent project"""
        return await self.complex_builder.create_multi_agent_project(project_definition)
    
    async def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the result of a task"""
        return await self.task_manager.get_task_status(task_id)
    
    async def get_project_status(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a complex project"""
        return await self.complex_builder.get_complex_task_status(project_id)
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        return await self.task_manager.cancel_task(task_id)
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        queue_stats = await self.task_manager.get_queue_stats()
        task_history = await self.task_manager.get_task_history(limit=10)
        
        return {
            'task_system': queue_stats,
            'recent_tasks': task_history,
            'active_agents': len(self.agent_registry),
            'agent_capabilities': self._get_agent_capabilities_summary()
        }
    
    def _get_agent_capabilities_summary(self) -> Dict[str, List[str]]:
        """Get summary of available agent capabilities"""
        capabilities_summary = {}
        
        for agent_id, agent in self.agent_registry.items():
            capabilities_summary[agent_id] = agent.capabilities
        
        return capabilities_summary
    
    async def execute_workflow(self, workflow_definition: Dict[str, Any]) -> str:
        """Execute a defined workflow"""
        workflow_id = f"workflow_{self._generate_id()}"
        
        # Parse workflow definition
        steps = workflow_definition.get('steps', [])
        conditions = workflow_definition.get('conditions', {})
        
        # Create tasks for each step
        task_map = {}
        for step in steps:
            task_id = await self.execute_simple_task(
                task_type=step['type'],
                payload=step.get('parameters', {}),
                priority=self._parse_workflow_priority(step.get('priority', 'medium'))
            )
            task_map[step['id']] = task_id
        
        # Monitor workflow execution
        asyncio.create_task(self._monitor_workflow(workflow_id, steps, task_map, conditions))
        
        return workflow_id
    
    async def _monitor_workflow(self, workflow_id: str, steps: List[Dict], 
                              task_map: Dict[str, str], conditions: Dict[str, Any]):
        """Monitor workflow execution and handle conditions"""
        completed_steps = set()
        workflow_results = {}
        
        while len(completed_steps) < len(steps):
            await asyncio.sleep(2)  # Check every 2 seconds
            
            for step in steps:
                if step['id'] in completed_steps:
                    continue
                
                task_id = task_map[step['id']]
                task_status = await self.get_task_result(task_id)
                
                if task_status and task_status['status'] == 'completed':
                    completed_steps.add(step['id'])
                    workflow_results[step['id']] = task_status['result']
                    
                    # Check if this step triggers any conditions
                    await self._evaluate_conditions(step['id'], task_status, conditions, task_map)
                
                elif task_status and task_status['status'] == 'failed':
                    # Handle step failure based on workflow definition
                    failure_handler = step.get('on_failure', 'stop')
                    if failure_handler == 'continue':
                        completed_steps.add(step['id'])
                    else:
                        # Stop workflow on failure
                        break
        
        # Workflow completed
        self._finalize_workflow(workflow_id, workflow_results)
    
    async def _evaluate_conditions(self, step_id: str, task_status: Dict, 
                                 conditions: Dict[str, Any], task_map: Dict[str, str]):
        """Evaluate workflow conditions and trigger appropriate actions"""
        step_conditions = conditions.get(step_id, [])
        
        for condition in step_conditions:
            condition_met = self._check_condition(condition, task_status)
            if condition_met:
                action = condition['action']
                if action['type'] == 'execute_step':
                    # Execute additional step
                    new_task_id = await self.execute_simple_task(
                        task_type=action['step_type'],
                        payload=action.get('parameters', {})
                    )
                    task_map[action['step_id']] = new_task_id
    
    def _check_condition(self, condition: Dict, task_status: Dict) -> bool:
        """Check if a condition is met"""
        condition_type = condition['type']
        
        if condition_type == 'result_contains':
            result = task_status.get('result', {})
            key = condition['key']
            expected_value = condition['value']
            return result.get(key) == expected_value
        
        elif condition_type == 'quality_threshold':
            result = task_status.get('result', {})
            quality_score = result.get('quality_score', 0)
            threshold = condition['threshold']
            return quality_score >= threshold
        
        return False
    
    def _finalize_workflow(self, workflow_id: str, results: Dict[str, Any]):
        """Finalize workflow execution"""
        # Store workflow results or trigger post-processing
        print(f"Workflow {workflow_id} completed with {len(results)} steps")
    
    def _parse_workflow_priority(self, priority_str: str) -> TaskPriority:
        """Parse workflow priority string"""
        priority_map = {
            'low': TaskPriority.LOW,
            'medium': TaskPriority.MEDIUM,
            'high': TaskPriority.HIGH,
            'critical': TaskPriority.CRITICAL
        }
        return priority_map.get(priority_str.lower(), TaskPriority.MEDIUM)
    
    def _generate_id(self) -> str:
        """Generate a unique ID"""
        import uuid
        return uuid.uuid4().hex[:8]
