#!/usr/bin/env python3
import asyncio
import sys
import os
import argparse
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from brain.orchestrator.strategic_intelligence import StrategicIntelligence
from brain.orchestrator.synthetic_intelligence import SyntheticIntelligence
from brain.orchestrator.deep_agents_manager import DeepAgentsManager

class AISystemOrchestrator:
    def __init__(self):
        self.strategic_intelligence = StrategicIntelligence()
        self.synthetic_intelligence = SyntheticIntelligence()
        self.deep_agents_manager = DeepAgentsManager()
        self.system_status = "initialized"
        
    async def initialize_system(self):
        """Initialize the complete AI system"""
        print("🚀 Initializing Advanced AI System...")
        
        # Load system configuration
        await self._load_configuration()
        
        # Initialize core components
        await self._initialize_core_components()
        
        # Create initial agent ecosystem
        await self._create_initial_agents()
        
        self.system_status = "ready"
        print("✅ AI System Ready for Complex Tasks")
    
    async def execute_complex_task(self, task_description: str, task_type: str = "strategic") -> Dict:
        """Execute complex tasks using the AI agent ecosystem"""
        
        print(f"🎯 Executing Complex Task: {task_description}")
        
        if task_type == "strategic":
            return await self._handle_strategic_task(task_description)
        elif task_type == "creative":
            return await self._handle_creative_task(task_description)
        elif task_type == "technical":
            return await self._handle_technical_task(task_description)
        else:
            return await self._handle_generic_task(task_description)
    
    async def _handle_strategic_task(self, task_description: str) -> Dict:
        """Handle strategic planning and analysis tasks"""
        
        # Strategic analysis
        strategic_analysis = await self.strategic_intelligence.analyze_complex_system(task_description)
        
        # Create agent ecosystem for execution
        agents = await self.strategic_intelligence.create_agent_ecosystem(strategic_analysis)
        
        # Execute with coordinated agents
        results = await self.deep_agents_manager.coordinate_agent_swarm({
            'task': task_description,
            'strategic_analysis': strategic_analysis,
            'agents': agents
        })
        
        return results

async def main():
    parser = argparse.ArgumentParser(description='Advanced AI System Orchestrator')
    parser.add_argument('--task', type=str, help='Task to execute')
    parser.add_argument('--task-type', choices=['strategic', 'creative', 'technical'], default='strategic')
    parser.add_argument('--auto-evolve', action='store_true', help='Enable auto-evolution')
    
    args = parser.parse_args()
    
    # Initialize system
    orchestrator = AISystemOrchestrator()
    await orchestrator.initialize_system()
    
    if args.task:
        # Execute specific task
        results = await orchestrator.execute_complex_task(args.task, args.task_type)
        print("\n📊 Task Results:")
        print(json.dumps(results, indent=2))
    else:
        # Interactive mode
        print("\n🤖 AI System Ready - Interactive Mode")
        print("Enter tasks for the AI system (type 'exit' to quit):")
        
        while True:
            try:
                task = input("\n🎯 Task: ").strip()
                if task.lower() in ['exit', 'quit']:
                    break
                
                if task:
                    results = await orchestrator.execute_complex_task(task)
                    print(f"\n✅ Task Completed: {results.get('summary', 'Task finished')}")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
