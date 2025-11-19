import inspect
import ast
import importlib
import sys
from io import StringIO
from typing import Dict, List, Any

class AgentFactory:
    def __init__(self):
        self.agent_templates = self._load_agent_templates()
        self.capability_library = self._load_capability_library()
        
    async def create_specialized_agent(self, agent_spec: Dict) -> Any:
        """Dynamically create specialized AI agents"""
        
        # Generate agent code
        agent_code = await self._generate_agent_code(agent_spec)
        
        # Validate code syntax
        self._validate_agent_code(agent_code)
        
        # Create agent class dynamically
        agent_class = self._compile_agent_class(agent_code, agent_spec['name'])
        
        # Initialize agent with capabilities
        agent_instance = agent_class(
            capabilities=agent_spec['capabilities'],
            configuration=agent_spec.get('configuration', {})
        )
        
        return agent_instance
    
    def _compile_agent_class(self, code: str, class_name: str) -> Any:
        """Dynamically compile agent class from generated code"""
        
        # Create module namespace
        module_namespace = {}
        
        # Execute code in namespace
        exec(code, module_namespace)
        
        # Extract the agent class
        agent_class = module_namespace[class_name]
        
        return agent_class
    
    async def _generate_agent_code(self, agent_spec: Dict) -> str:
        """Generate complete agent implementation code"""
        
        capabilities_code = await self._generate_capabilities_code(agent_spec['capabilities'])
        learning_code = await self._generate_learning_mechanisms(agent_spec)
        communication_code = await self._generate_communication_protocols(agent_spec)
        
        agent_template = self.agent_templates['advanced_agent'].format(
            class_name=agent_spec['name'].title().replace('_', ''),
            capabilities_code=capabilities_code,
            learning_code=learning_code,
            communication_code=communication_code,
            autonomy_level=agent_spec.get('autonomy_level', 'medium')
        )
        
        return agent_template

class SelfEvolvingAgent:
    """Base class for self-evolving agents"""
    
    def __init__(self, capabilities: Dict, configuration: Dict):
        self.capabilities = capabilities
        self.configuration = configuration
        self.performance_metrics = {}
        self.learning_data = []
        self.evolution_triggers = configuration.get('evolution_triggers', [])
        
    async def evolve_capability(self, capability_name: str, performance_data: Dict):
        """Evolve specific capability based on performance"""
        
        if self._should_evolve(capability_name, performance_data):
            evolution_plan = await self.create_evolution_plan(capability_name, performance_data)
            await self.execute_evolution(evolution_plan)
            
    async self_replicate(self, new_specifications: Dict) -> str:
        """Create a new evolved version of itself"""
        
        new_capabilities = self._merge_capabilities(self.capabilities, new_specifications)
        new_agent_spec = {
            'name': f"{self.__class__.__name__}_evolved",
            'capabilities': new_capabilities,
            'configuration': self._update_configuration(new_specifications)
        }
        
        return await agent_factory.create_specialized_agent(new_agent_spec)
