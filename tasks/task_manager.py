import asyncio
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskManager:
    """Manager for coordinating and tracking AI agent tasks"""
    
    def __init__(self):
        self.tasks = {}
        self.task_queue = asyncio.Queue()
        self.worker_tasks = []
        self.max_workers = 5
        self.is_running = False
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        logger = logging.getLogger("TaskManager")
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    async def create_task(self, task_type: str, payload: Dict[str, Any], 
                         priority: TaskPriority = TaskPriority.MEDIUM,
                         dependencies: List[str] = None,
                         timeout: int = 300) -> str:
        """Create a new task and add it to the queue"""
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        task = {
            'task_id': task_id,
            'type': task_type,
            'payload': payload,
            'priority': priority,
            'status': TaskStatus.PENDING,
            'dependencies': dependencies or [],
            'timeout': timeout,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'retry_count': 0,
            'max_retries': 3,
            'assigned_agent': None,
            'result': None,
            'error': None
        }
        
        self.tasks[task_id] = task
        await self.task_queue.put(task)
        self.logger.info(f"Created task {task_id} of type {task_type} with priority {priority.value}")
        
        return task_id

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific task"""
        task = self.tasks.get(task_id)
        if task:
            return {
                'task_id': task['task_id'],
                'type': task['type'],
                'status': task['status'].value,
                'priority': task['priority'].value,
                'created_at': task['created_at'],
                'updated_at': task['updated_at'],
                'assigned_agent': task['assigned_agent'],
                'result': task['result'],
                'error': task['error']
            }
        return None

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or in-progress task"""
        task = self.tasks.get(task_id)
        if task and task['status'] in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]:
            task['status'] = TaskStatus.CANCELLED
            task['updated_at'] = datetime.now().isoformat()
            self.logger.info(f"Cancelled task {task_id}")
            return True
        return False

    async def start_workers(self, agent_registry):
        """Start task worker processes"""
        self.is_running = True
        self.agent_registry = agent_registry
        
        # Start worker tasks
        for i in range(self.max_workers):
            worker_task = asyncio.create_task(self._worker(f"worker-{i+1}"))
            self.worker_tasks.append(worker_task)
        
        self.logger.info(f"Started {self.max_workers} task workers")

    async def stop_workers(self):
        """Stop all task workers"""
        self.is_running = False
        
        # Wait for workers to finish
        if self.worker_tasks:
            await asyncio.gather(*self.worker_tasks, return_exceptions=True)
            self.worker_tasks.clear()
        
        self.logger.info("Stopped all task workers")

    async def _worker(self, worker_id: str):
        """Worker process for executing tasks"""
        self.logger.info(f"Worker {worker_id} started")
        
        while self.is_running:
            try:
                # Get task from queue with timeout
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                
                # Check if task is still relevant
                if task['status'] == TaskStatus.CANCELLED:
                    self.task_queue.task_done()
                    continue
                
                # Process task
                await self._process_task(task, worker_id)
                self.task_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Worker {worker_id} error: {str(e)}")
                continue
        
        self.logger.info(f"Worker {worker_id} stopped")

    async def _process_task(self, task: Dict[str, Any], worker_id: str):
        """Process a single task"""
        task_id = task['task_id']
        
        try:
            # Update task status
            task['status'] = TaskStatus.IN_PROGRESS
            task['assigned_agent'] = worker_id
            task['updated_at'] = datetime.now().isoformat()
            
            self.logger.info(f"Worker {worker_id} processing task {task_id}")
            
            # Check dependencies
            if task['dependencies']:
                deps_met = await self._check_dependencies(task['dependencies'])
                if not deps_met:
                    task['status'] = TaskStatus.FAILED
                    task['error'] = "Dependencies not met"
                    return
            
            # Find appropriate agent for task type
            agent = await self._find_agent_for_task(task)
            if not agent:
                task['status'] = TaskStatus.FAILED
                task['error'] = f"No suitable agent found for task type: {task['type']}"
                return
            
            # Execute task with timeout
            try:
                result = await asyncio.wait_for(
                    agent.execute(task),
                    timeout=task['timeout']
                )
                
                task['result'] = result
                task['status'] = TaskStatus.COMPLETED
                self.logger.info(f"Task {task_id} completed successfully")
                
            except asyncio.TimeoutError:
                task['status'] = TaskStatus.FAILED
                task['error'] = f"Task timeout after {task['timeout']} seconds"
                self.logger.warning(f"Task {task_id} timed out")
                
            except Exception as e:
                task['status'] = TaskStatus.FAILED
                task['error'] = str(e)
                self.logger.error(f"Task {task_id} failed: {str(e)}")
                
                # Retry logic
                if task['retry_count'] < task['max_retries']:
                    task['retry_count'] += 1
                    task['status'] = TaskStatus.PENDING
                    task['assigned_agent'] = None
                    task['error'] = None
                    await self.task_queue.put(task)
                    self.logger.info(f"Retrying task {task_id} (attempt {task['retry_count']})")
        
        except Exception as e:
            task['status'] = TaskStatus.FAILED
            task['error'] = f"Unexpected error: {str(e)}"
            self.logger.error(f"Unexpected error processing task {task_id}: {str(e)}")

    async def _find_agent_for_task(self, task: Dict[str, Any]):
        """Find the most suitable agent for a task"""
        task_type = task['type']
        required_capabilities = task.get('payload', {}).get('required_capabilities', [])
        
        best_agent = None
        best_score = 0
        
        for agent in self.agent_registry.values():
            # Calculate suitability score
            score = await self._calculate_agent_suitability(agent, task_type, required_capabilities)
            
            if score > best_score:
                best_agent = agent
                best_score = score
        
        return best_agent if best_score > 0 else None

    async def _calculate_agent_suitability(self, agent, task_type: str, required_capabilities: List[str]) -> float:
        """Calculate how suitable an agent is for a task"""
        score = 0.0
        
        # Check if agent has the required capabilities
        agent_capabilities = set(agent.capabilities)
        required_capabilities_set = set(required_capabilities)
        
        if required_capabilities_set.issubset(agent_capabilities):
            score += 0.5
        
        # Check performance history for similar tasks
        performance = agent.get_performance_report()
        task_performance = performance['performance_metrics'].get(task_type, {})
        
        if task_performance:
            success_rate = task_performance.get('successful_tasks', 0) / task_performance.get('total_tasks', 1)
            score += success_rate * 0.3
        
        # Consider agent's current workload (simplified)
        score += 0.2  # Base score for availability
        
        return score

    async def _check_dependencies(self, dependencies: List[str]) -> bool:
        """Check if all task dependencies are met"""
        for dep_id in dependencies:
            dep_task = self.tasks.get(dep_id)
            if not dep_task or dep_task['status'] != TaskStatus.COMPLETED:
                return False
        return True

    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get statistics about the task queue"""
        pending_tasks = len([t for t in self.tasks.values() if t['status'] == TaskStatus.PENDING])
        in_progress_tasks = len([t for t in self.tasks.values() if t['status'] == TaskStatus.IN_PROGRESS])
        completed_tasks = len([t for t in self.tasks.values() if t['status'] == TaskStatus.COMPLETED])
        failed_tasks = len([t for t in self.tasks.values() if t['status'] == TaskStatus.FAILED])
        
        # Calculate average completion time for completed tasks
        completion_times = []
        for task in self.tasks.values():
            if task['status'] == TaskStatus.COMPLETED':
                created = datetime.fromisoformat(task['created_at'])
                updated = datetime.fromisoformat(task['updated_at'])
                completion_times.append((updated - created).total_seconds())
        
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
        
        return {
            'total_tasks': len(self.tasks),
            'pending_tasks': pending_tasks,
            'in_progress_tasks': in_progress_tasks,
            'completed_tasks': completed_tasks,
            'failed_tasks': failed_tasks,
            'queue_size': self.task_queue.qsize(),
            'active_workers': len([w for w in self.worker_tasks if not w.done()]),
            'average_completion_time_seconds': avg_completion_time,
            'success_rate': completed_tasks / len(self.tasks) if self.tasks else 0
        }

    async def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Clean up old completed or failed tasks"""
        now = datetime.now()
        tasks_to_remove = []
        
        for task_id, task in self.tasks.items():
            if task['status'] in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                created = datetime.fromisoformat(task['created_at'])
                if (now - created).total_seconds() > max_age_hours * 3600:
                    tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del self.tasks[task_id]
        
        if tasks_to_remove:
            self.logger.info(f"Cleaned up {len(tasks_to_remove)} old tasks")

    async def get_task_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent task history"""
        tasks_list = list(self.tasks.values())
        tasks_list.sort(key=lambda x: x['created_at'], reverse=True)
        
        return [
            {
                'task_id': task['task_id'],
                'type': task['type'],
                'status': task['status'].value,
                'priority': task['priority'].value,
                'created_at': task['created_at'],
                'assigned_agent': task['assigned_agent'],
                'error': task.get('error')
            }
            for task in tasks_list[:limit]
        ]
