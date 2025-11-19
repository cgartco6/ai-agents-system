import uuid
import asyncio
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

class BaseAgent(ABC):
    """Base class for all AI agents in the system"""
    
    def __init__(self, agent_id: str, name: str, capabilities: List[str], config: Dict[str, Any]):
        self.agent_id = agent_id or f"agent_{uuid.uuid4().hex[:8]}"
        self.name = name
        self.capabilities = capabilities
        self.config = config
        self.memory = {}
        self.performance_metrics = {}
        self.learning_rate = config.get('learning_rate', 0.1)
        self.autonomy_level = config.get('autonomy_level', 'medium')
        self.is_active = False
        self.task_queue = asyncio.Queue()
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        logger = logging.getLogger(f"{self.__class__.__name__}_{self.agent_id}")
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    @abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task - to be implemented by subclasses"""
        pass

    @abstractmethod
    async def learn_from_experience(self, experience: Dict[str, Any]):
        """Learn from previous experiences"""
        pass

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task with error handling and performance tracking"""
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Agent {self.name} starting task: {task.get('type', 'unknown')}")
            result = await self.process_task(task)
            
            # Track performance
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_performance_metrics(task, result, execution_time, True)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Agent {self.name} failed task: {str(e)}")
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_performance_metrics(task, {"error": str(e)}, execution_time, False)
            
            return {
                "status": "error",
                "error": str(e),
                "agent_id": self.agent_id,
                "task_id": task.get('task_id', 'unknown')
            }

    def _update_performance_metrics(self, task: Dict, result: Dict, execution_time: float, success: bool):
        """Update agent performance metrics"""
        task_type = task.get('type', 'unknown')
        
        if task_type not in self.performance_metrics:
            self.performance_metrics[task_type] = {
                'total_tasks': 0,
                'successful_tasks': 0,
                'total_execution_time': 0,
                'average_execution_time': 0
            }
        
        metrics = self.performance_metrics[task_type]
        metrics['total_tasks'] += 1
        metrics['total_execution_time'] += execution_time
        metrics['average_execution_time'] = metrics['total_execution_time'] / metrics['total_tasks']
        
        if success:
            metrics['successful_tasks'] += 1

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report for the agent"""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'capabilities': self.capabilities,
            'performance_metrics': self.performance_metrics,
            'success_rate': self._calculate_success_rate(),
            'total_tasks_processed': sum(m['total_tasks'] for m in self.performance_metrics.values())
        }

    def _calculate_success_rate(self) -> float:
        """Calculate overall success rate across all task types"""
        if not self.performance_metrics:
            return 0.0
            
        total_tasks = sum(m['total_tasks'] for m in self.performance_metrics.values())
        successful_tasks = sum(m['successful_tasks'] for m in self.performance_metrics.values())
        
        return (successful_tasks / total_tasks) * 100 if total_tasks > 0 else 0.0

    async def self_improve(self) -> Dict[str, Any]:
        """Self-improvement mechanism for the agent"""
        improvement_areas = self._identify_improvement_areas()
        improvements = {}
        
        for area in improvement_areas:
            improvement_plan = await self._create_improvement_plan(area)
            improvement_result = await self._implement_improvement(improvement_plan)
            improvements[area] = improvement_result
            
        return improvements

    def _identify_improvement_areas(self) -> List[str]:
        """Identify areas where the agent needs improvement"""
        improvement_areas = []
        
        for task_type, metrics in self.performance_metrics.items():
            success_rate = (metrics['successful_tasks'] / metrics['total_tasks']) * 100
            if success_rate < 80:  # Threshold for improvement
                improvement_areas.append(f"success_rate_{task_type}")
                
            if metrics['average_execution_time'] > 30:  # More than 30 seconds average
                improvement_areas.append(f"efficiency_{task_type}")
                
        return improvement_areas

    @abstractmethod
    async def _create_improvement_plan(self, area: str) -> Dict[str, Any]:
        """Create improvement plan for specific area"""
        pass

    @abstractmethod
    async def _implement_improvement(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Implement improvement plan"""
        pass

class CollaborativeAgent(BaseAgent):
    """Base class for agents that can collaborate with others"""
    
    def __init__(self, agent_id: str, name: str, capabilities: List[str], config: Dict[str, Any]):
        super().__init__(agent_id, name, capabilities, config)
        self.collaboration_network = {}
        self.communication_protocols = config.get('communication_protocols', {})
        
    async def collaborate(self, other_agent: BaseAgent, task: Dict[str, Any]) -> Dict[str, Any]:
        """Collaborate with another agent on a task"""
        collaboration_id = f"collab_{uuid.uuid4().hex[:8]}"
        
        self.logger.info(f"Initiating collaboration {collaboration_id} with {other_agent.name}")
        
        # Establish communication channel
        communication_channel = await self._establish_communication(other_agent)
        
        # Divide task based on capabilities
        task_division = await self._divide_task(task, other_agent)
        
        # Execute subtasks in parallel
        results = await asyncio.gather(
            self.execute(task_division['subtask_1']),
            other_agent.execute(task_division['subtask_2']),
            return_exceptions=True
        )
        
        # Synthesize results
        final_result = await self._synthesize_results(results, task)
        
        # Update collaboration network
        self._update_collaboration_network(other_agent, True)
        
        return final_result

    async def _establish_communication(self, other_agent: BaseAgent) -> Dict[str, Any]:
        """Establish communication channel with another agent"""
        return {
            'channel_id': f"comm_{uuid.uuid4().hex[:8]}",
            'agents': [self.agent_id, other_agent.agent_id],
            'protocol': self.communication_protocols.get('default', 'direct'),
            'established_at': datetime.now().isoformat()
        }

    async def _divide_task(self, task: Dict[str, Any], other_agent: BaseAgent) -> Dict[str, Any]:
        """Divide task based on agent capabilities"""
        # Simple division based on capabilities match
        our_capabilities = set(self.capabilities)
        their_capabilities = set(other_agent.capabilities)
        
        common_capabilities = our_capabilities.intersection(their_capabilities)
        our_unique = our_capabilities - their_capabilities
        their_unique = their_capabilities - our_capabilities
        
        return {
            'subtask_1': {
                **task,
                'focus_capabilities': list(our_unique) if our_unique else list(common_capabilities),
                'assigned_agent': self.agent_id
            },
            'subtask_2': {
                **task,
                'focus_capabilities': list(their_unique) if their_unique else list(common_capabilities),
                'assigned_agent': other_agent.agent_id
            }
        }

    async def _synthesize_results(self, results: List[Dict], original_task: Dict) -> Dict[str, Any]:
        """Synthesize results from multiple agents"""
        successful_results = [r for r in results if not isinstance(r, Exception) and r.get('status') != 'error']
        
        if not successful_results:
            return {
                'status': 'error',
                'message': 'All collaborative agents failed',
                'individual_results': results
            }
            
        return {
            'status': 'success',
            'synthesized_result': await self._merge_results(successful_results),
            'individual_results': results,
            'collaboration_success_rate': len(successful_results) / len(results) * 100
        }

    @abstractmethod
    async def _merge_results(self, results: List[Dict]) -> Dict[str, Any]:
        """Merge multiple results into a cohesive output"""
        pass

    def _update_collaboration_network(self, other_agent: BaseAgent, success: bool):
        """Update collaboration network with experience"""
        if other_agent.agent_id not in self.collaboration_network:
            self.collaboration_network[other_agent.agent_id] = {
                'collaboration_count': 0,
                'successful_collaborations': 0,
                'last_collaboration': None
            }
            
        network_entry = self.collaboration_network[other_agent.agent_id]
        network_entry['collaboration_count'] += 1
        network_entry['last_collaboration'] = datetime.now().isoformat()
        
        if success:
            network_entry['successful_collaborations'] += 1
