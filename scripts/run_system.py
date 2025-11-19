#!/usr/bin/env python3
"""
Advanced AI System - Main Runner
Orchestrates all AI agents and system components
"""

import asyncio
import sys
import os
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from brain.orchestrator.strategic_intelligence import StrategicIntelligence
from brain.orchestrator.synthetic_intelligence import SyntheticIntelligence
from brain.orchestrator.deep_agents_manager import DeepAgentsManager

from agents.coding_agents.code_generation_agent import CodeGenerationAgent
from agents.coding_agents.code_review_agent import CodeReviewAgent
from agents.coding_agents.architecture_agent import ArchitectureAgent
from agents.coding_agents.debugging_agent import DebuggingAgent

from agents.business_agents.market_analysis_agent import MarketAnalysisAgent
from agents.business_agents.business_plan_agent import BusinessPlanAgent
from agents.business_agents.financial_analysis_agent import FinancialAnalysisAgent
from agents.business_agents.strategy_development_agent import StrategyDevelopmentAgent

from agents.strategic_agents.strategic_planning_agent import StrategicPlanningAgent
from agents.strategic_agents.risk_management_agent import RiskManagementAgent
from agents.strategic_agents.innovation_agent import InnovationAgent
from agents.strategic_agents.decision_support_agent import DecisionSupportAgent

from tasks.task_executor import TaskExecutor
from memory.vector_store import VectorStore
from memory.knowledge_base import KnowledgeBase

from tools.code_generation import CodeGenerationTool
from tools.web_scraper import WebScraper
from tools.api_integrator import APIIntegrator
from tools.system_controller import SystemController

class AISystemOrchestrator:
    """Main orchestrator for the Advanced AI System"""
    
    def __init__(self, config_path: str = "config/system_config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.agent_registry = {}
        self.system_components = {}
        self.is_running = False
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/system/system.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger("AISystemOrchestrator")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load system configuration"""
        # Simplified config loading - in production would use YAML/JSON
        return {
            'system': {
                'name': 'Advanced AI System',
                'version': '1.0.0',
                'environment': 'development'
            },
            'agents': {
                'enabled': True,
                'auto_creation': True
            },
            'memory': {
                'enabled': True,
                'persistence': True
            }
        }
    
    async def initialize_system(self):
        """Initialize the complete AI system"""
        self.logger.info("🚀 Initializing Advanced AI System...")
        
        try:
            # Initialize core intelligence systems
            await self._initialize_core_intelligence()
            
            # Initialize memory systems
            await self._initialize_memory_systems()
            
            # Initialize AI agents
            await self._initialize_agents()
            
            # Initialize tools
            await self._initialize_tools()
            
            # Initialize task execution system
            await self._initialize_task_system()
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.is_running = True
            self.logger.info("✅ AI System Ready for Complex Tasks")
            
        except Exception as e:
            self.logger.error(f"❌ System initialization failed: {str(e)}")
            raise
    
    async def _initialize_core_intelligence(self):
        """Initialize core intelligence systems"""
        self.logger.info("🧠 Initializing Core Intelligence Systems...")
        
        self.system_components['strategic_intelligence'] = StrategicIntelligence()
        self.system_components['synthetic_intelligence'] = SyntheticIntelligence()
        self.system_components['deep_agents_manager'] = DeepAgentsManager()
        
        self.logger.info("✅ Core Intelligence Systems Ready")
    
    async def _initialize_memory_systems(self):
        """Initialize memory and knowledge systems"""
        self.logger.info("💾 Initializing Memory Systems...")
        
        self.system_components['vector_store'] = VectorStore()
        self.system_components['knowledge_base'] = KnowledgeBase()
        
        self.logger.info("✅ Memory Systems Ready")
    
    async def _initialize_agents(self):
        """Initialize all AI agents"""
        self.logger.info("🤖 Initializing AI Agents...")
        
        # Coding Agents
        self.agent_registry['code_generation'] = CodeGenerationAgent()
        self.agent_registry['code_review'] = CodeReviewAgent()
        self.agent_registry['architecture'] = ArchitectureAgent()
        self.agent_registry['debugging'] = DebuggingAgent()
        
        # Business Agents
        self.agent_registry['market_analysis'] = MarketAnalysisAgent()
        self.agent_registry['business_plan'] = BusinessPlanAgent()
        self.agent_registry['financial_analysis'] = FinancialAnalysisAgent()
        self.agent_registry['strategy_development'] = StrategyDevelopmentAgent()
        
        # Strategic Agents
        self.agent_registry['strategic_planning'] = StrategicPlanningAgent()
        self.agent_registry['risk_management'] = RiskManagementAgent()
        self.agent_registry['innovation'] = InnovationAgent()
        self.agent_registry['decision_support'] = DecisionSupportAgent()
        
        self.logger.info(f"✅ {len(self.agent_registry)} AI Agents Initialized")
    
    async def _initialize_tools(self):
        """Initialize system tools"""
        self.logger.info("🛠️ Initializing System Tools...")
        
        self.system_components['code_generation_tool'] = CodeGenerationTool()
        self.system_components['web_scraper'] = WebScraper()
        self.system_components['api_integrator'] = APIIntegrator()
        self.system_components['system_controller'] = SystemController()
        
        self.logger.info("✅ System Tools Ready")
    
    async def _initialize_task_system(self):
        """Initialize task execution system"""
        self.logger.info("⚡ Initializing Task Execution System...")
        
        self.system_components['task_executor'] = TaskExecutor(self.agent_registry)
        await self.system_components['task_executor'].initialize()
        
        self.logger.info("✅ Task Execution System Ready")
    
    async def _start_background_tasks(self):
        """Start background system tasks"""
        self.logger.info("🔄 Starting Background Tasks...")
        
        # Start system monitoring
        asyncio.create_task(self._monitor_system_health())
        
        # Start memory maintenance
        asyncio.create_task(self._maintain_memory_systems())
        
        # Start agent self-improvement
        asyncio.create_task(self._run_agent_self_improvement())
        
        self.logger.info("✅ Background Tasks Started")
    
    async def _monitor_system_health(self):
        """Monitor system health in background"""
        while self.is_running:
            try:
                system_status = await self.system_components['system_controller'].get_system_status()
                
                # Log system health
                overall_health = system_status['overall_health']['score']
                if overall_health < 60:
                    self.logger.warning(f"System health degraded: {overall_health}")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"System health monitoring error: {str(e)}")
                await asyncio.sleep(60)
    
    async def _maintain_memory_systems(self):
        """Maintain memory systems in background"""
        while self.is_running:
            try:
                # Clean up old memories
                self.system_components['vector_store'].cleanup_old_memories()
                
                # Backup knowledge base
                await self.system_components['knowledge_base'].export_knowledge(
                    f"backups/knowledge_backup_{asyncio.get_event_loop().time()}.json"
                )
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                self.logger.error(f"Memory maintenance error: {str(e)}")
                await asyncio.sleep(3600)
    
    async def _run_agent_self_improvement(self):
        """Run agent self-improvement in background"""
        while self.is_running:
            try:
                for agent_name, agent in self.agent_registry.items():
                    try:
                        improvements = await agent.self_improve()
                        if improvements:
                            self.logger.info(f"Agent {agent_name} self-improved: {improvements}")
                    except Exception as e:
                        self.logger.error(f"Agent {agent_name} self-improvement failed: {str(e)}")
                
                await asyncio.sleep(7200)  # Run every 2 hours
                
            except Exception as e:
                self.logger.error(f"Agent self-improvement error: {str(e)}")
                await asyncio.sleep(7200)
    
    async def execute_complex_task(self, task_description: str, 
                                 task_type: str = "strategic",
                                 priority: str = "medium") -> Dict[str, Any]:
        """Execute complex tasks using the AI agent ecosystem"""
        self.logger.info(f"🎯 Executing Complex Task: {task_description}")
        
        try:
            if task_type == "strategic":
                return await self._handle_strategic_task(task_description, priority)
            elif task_type == "creative":
                return await self._handle_creative_task(task_description, priority)
            elif task_type == "technical":
                return await self._handle_technical_task(task_description, priority)
            elif task_type == "business":
                return await self._handle_business_task(task_description, priority)
            else:
                return await self._handle_generic_task(task_description, priority)
                
        except Exception as e:
            self.logger.error(f"Task execution failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'task_description': task_description
            }
    
    async def _handle_strategic_task(self, task_description: str, priority: str) -> Dict[str, Any]:
        """Handle strategic planning and analysis tasks"""
        # Use strategic intelligence for analysis
        strategic_analysis = await self.system_components['strategic_intelligence'].analyze_complex_system(task_description)
        
        # Create agent ecosystem for execution
        agents = await self.system_components['strategic_intelligence'].create_agent_ecosystem(strategic_analysis)
        
        # Execute with coordinated agents
        task_payload = {
            'task': task_description,
            'strategic_analysis': strategic_analysis,
            'agents': agents,
            'priority': priority
        }
        
        task_id = await self.system_components['task_executor'].execute_simple_task(
            'strategic_planning', task_payload
        )
        
        # Wait for completion and return results
        return await self._wait_for_task_completion(task_id)
    
    async def _handle_creative_task(self, task_description: str, priority: str) -> Dict[str, Any]:
        """Handle creative and innovative tasks"""
        # Use synthetic intelligence for creative solutions
        creative_solution = await self.system_components['synthetic_intelligence'].synthesize_solution(
            task_description, {}
        )
        
        return {
            'status': 'success',
            'task_type': 'creative',
            'solution': creative_solution,
            'innovation_score': creative_solution.get('innovation_score', 0),
            'feasibility': creative_solution.get('feasibility_analysis', {})
        }
    
    async def _handle_technical_task(self, task_description: str, priority: str) -> Dict[str, Any]:
        """Handle technical and coding tasks"""
        # Use coding agents for technical tasks
        task_payload = {
            'description': task_description,
            'priority': priority,
            'required_capabilities': ['code_generation', 'problem_solving']
        }
        
        task_id = await self.system_components['task_executor'].execute_simple_task(
            'code_generation', task_payload
        )
        
        return await self._wait_for_task_completion(task_id)
    
    async def _handle_business_task(self, task_description: str, priority: str) -> Dict[str, Any]:
        """Handle business and analysis tasks"""
        # Use business agents for business tasks
        task_payload = {
            'description': task_description,
            'priority': priority,
            'required_capabilities': ['business_analysis', 'market_research']
        }
        
        task_id = await self.system_components['task_executor'].execute_simple_task(
            'business_analysis', task_payload
        )
        
        return await self._wait_for_task_completion(task_id)
    
    async def _handle_generic_task(self, task_description: str, priority: str) -> Dict[str, Any]:
        """Handle generic tasks using the most appropriate agents"""
        # Analyze task to determine best approach
        task_analysis = await self._analyze_task_requirements(task_description)
        
        # Create appropriate task payload
        task_payload = {
            'description': task_description,
            'priority': priority,
            'analysis': task_analysis,
            'required_capabilities': task_analysis.get('required_capabilities', [])
        }
        
        task_id = await self.system_components['task_executor'].execute_simple_task(
            task_analysis.get('task_type', 'generic'),
            task_payload
        )
        
        return await self._wait_for_task_completion(task_id)
    
    async def _analyze_task_requirements(self, task_description: str) -> Dict[str, Any]:
        """Analyze task requirements to determine best approach"""
        # This would use AI to analyze the task and determine requirements
        return {
            'task_type': 'generic',
            'complexity': 'medium',
            'required_capabilities': ['problem_solving', 'analysis'],
            'estimated_duration': 'short',
            'suitable_agents': ['strategic_planning', 'decision_support']
        }
    
    async def _wait_for_task_completion(self, task_id: str, timeout: int = 300) -> Dict[str, Any]:
        """Wait for task completion with timeout"""
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            task_status = await self.system_components['task_executor'].get_task_result(task_id)
            
            if task_status and task_status.get('status') in ['completed', 'failed']:
                return task_status
            
            await asyncio.sleep(1)
        
        return {
            'status': 'error',
            'error': f"Task timeout after {timeout} seconds",
            'task_id': task_id
        }
    
    async def execute_complex_project(self, project_definition: Dict[str, Any]) -> str:
        """Execute a complex multi-agent project"""
        self.logger.info(f"🏗️ Starting Complex Project: {project_definition.get('name', 'Unknown')}")
        
        project_id = await self.system_components['task_executor'].execute_complex_project(project_definition)
        
        self.logger.info(f"✅ Project Started with ID: {project_id}")
        return project_id
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        system_health = await self.system_components['system_controller'].get_system_status()
        task_stats = await self.system_components['task_executor'].get_system_stats()
        
        return {
            'system_health': system_health,
            'task_system': task_stats,
            'agents': {
                'total_agents': len(self.agent_registry),
                'active_agents': [name for name, agent in self.agent_registry.items()],
                'agent_performance': {
                    name: agent.get_performance_report()
                    for name, agent in self.agent_registry.items()
                }
            },
            'memory': {
                'vector_store': self.system_components['vector_store'].get_memory_statistics(),
                'knowledge_base': await self.system_components['knowledge_base'].get_statistics()
            },
            'is_running': self.is_running
        }
    
    async def shutdown(self):
        """Gracefully shutdown the AI system"""
        self.logger.info("🛑 Shutting down AI System...")
        
        self.is_running = False
        
        # Shutdown task executor
        if 'task_executor' in self.system_components:
            await self.system_components['task_executor'].shutdown()
        
        # Close memory systems
        if 'vector_store' in self.system_components:
            self.system_components['vector_store'].save()
        
        self.logger.info("✅ AI System Shutdown Complete")

async def main():
    """Main entry point for the AI System"""
    parser = argparse.ArgumentParser(description='Advanced AI System Orchestrator')
    parser.add_argument('--task', type=str, help='Task to execute')
    parser.add_argument('--task-type', choices=['strategic', 'creative', 'technical', 'business'], default='strategic')
    parser.add_argument('--project', type=str, help='Project definition JSON file')
    parser.add_argument('--interactive', action='store_true', help='Start in interactive mode')
    parser.add_argument('--auto-evolve', action='store_true', help='Enable auto-evolution')
    parser.add_argument('--config', type=str, default='config/system_config.yaml', help='Config file path')
    
    args = parser.parse_args()
    
    # Initialize system
    orchestrator = AISystemOrchestrator(args.config)
    
    try:
        await orchestrator.initialize_system()
        
        if args.task:
            # Execute specific task
            results = await orchestrator.execute_complex_task(args.task, args.task_type)
            print("\n📊 Task Results:")
            print_json(results)
            
        elif args.project:
            # Execute project from file
            import json
            with open(args.project, 'r') as f:
                project_definition = json.load(f)
            
            project_id = await orchestrator.execute_complex_project(project_definition)
            print(f"\n🏗️ Project Started: {project_id}")
            
            # Monitor project progress
            while True:
                project_status = await orchestrator.system_components['task_executor'].get_project_status(project_id)
                print(f"\r📈 Project Progress: {project_status.get('progress', 0):.1f}%", end='')
                
                if project_status.get('status') in ['completed', 'failed']:
                    print(f"\n✅ Project {project_status['status']}!")
                    break
                
                await asyncio.sleep(5)
                
        elif args.interactive:
            # Interactive mode
            await interactive_mode(orchestrator)
            
        else:
            # Display system status
            system_status = await orchestrator.get_system_status()
            print("\n🤖 AI System Status:")
            print_json(system_status)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"❌ System error: {e}")
    finally:
        await orchestrator.shutdown()

async def interactive_mode(orchestrator):
    """Run system in interactive mode"""
    print("\n🤖 AI System Ready - Interactive Mode")
    print("Available commands:")
    print("  task <description> [type] - Execute a task")
    print("  status - Show system status")
    print("  agents - List available agents")
    print("  monitor - Show real-time monitoring")
    print("  exit - Shutdown system")
    print("\nEnter commands below:")
    
    while True:
        try:
            user_input = input("\n🎯 AI System> ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['exit', 'quit', 'q']:
                break
                
            elif user_input.lower() == 'status':
                status = await orchestrator.get_system_status()
                print_json(status)
                
            elif user_input.lower() == 'agents':
                agents = list(orchestrator.agent_registry.keys())
                print(f"🤖 Available Agents ({len(agents)}):")
                for agent in agents:
                    print(f"  - {agent}")
                    
            elif user_input.lower() == 'monitor':
                await show_realtime_monitoring(orchestrator)
                
            elif user_input.startswith('task '):
                parts = user_input[5:].split(' ', 1)
                task_description = parts[0] if len(parts) > 0 else ""
                task_type = parts[1] if len(parts) > 1 else "strategic"
                
                if task_description:
                    print(f"🎯 Executing task: {task_description}")
                    results = await orchestrator.execute_complex_task(task_description, task_type)
                    print_json(results)
                else:
                    print("❌ Please provide a task description")
                    
            else:
                print("❌ Unknown command. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")

async def show_realtime_monitoring(orchestrator):
    """Show real-time system monitoring"""
    print("📊 Starting real-time monitoring (Ctrl+C to stop)...")
    
    try:
        while True:
            system_status = await orchestrator.get_system_status()
            health = system_status['system_health']['overall_health']
            
            print(f"\r🔄 System Health: {health['score']}% ({health['status']}) | "
                  f"Agents: {len(system_status['agents']['active_agents'])} | "
                  f"Tasks: {system_status['task_system']['task_system']['active_workers']} active", end='')
            
            await asyncio.sleep(2)
            
    except KeyboardInterrupt:
        print("\n📊 Monitoring stopped")

def print_json(data):
    """Pretty print JSON data"""
    import json
    print(json.dumps(data, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())
