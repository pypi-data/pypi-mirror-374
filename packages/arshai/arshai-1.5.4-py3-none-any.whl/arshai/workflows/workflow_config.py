from typing import Dict, Any, List, Type, Optional
from arshai.core.interfaces.iworkflow import IWorkflowConfig, IWorkflowOrchestrator, INode
from arshai.workflows.workflow_orchestrator import BaseWorkflowOrchestrator
from arshai.utils import get_logger

class WorkflowConfig(IWorkflowConfig):
    """Base implementation of workflow configuration.
    
    This implementation provides a foundation for workflow configuration where:
    - The config creates and configures the workflow orchestrator
    - The config defines the workflow structure (nodes and edges)
    - The config provides routing logic for input
    - Components are injected directly rather than through Settings
    """
    
    def __init__(
        self,
        debug_mode: bool = False,
        **kwargs: Any
    ):
        """Initialize workflow configuration.
        
        Args:
            debug_mode: Whether to enable debug mode for verbose logging
            **kwargs: Additional configuration options that subclasses can use
        
        Note:
            Subclasses should accept their required dependencies directly in their
            constructors rather than relying on a Settings object. This follows
            the three-layer architecture where developers have full control over
            component instantiation.
        
        Example:
            class MyWorkflowConfig(WorkflowConfig):
                def __init__(self, llm_client: ILLM, memory_manager: IMemoryManager, **kwargs):
                    super().__init__(**kwargs)
                    self.llm_client = llm_client
                    self.memory_manager = memory_manager
        """
        self.debug_mode = debug_mode
        self._kwargs = kwargs
        self._logger = get_logger(__name__)
        
        # Nodes and edges will be created in _configure_workflow
        self.nodes: Dict[str, INode] = {}
        self.edges: Dict[str, str] = {}
    
    def create_workflow(self) -> IWorkflowOrchestrator:
        """Create the workflow orchestrator (without configuration).
        
        This method:
        1. Creates a new workflow orchestrator
        2. Returns the unconfigured orchestrator
        
        Note: Call _configure_workflow(workflow) separately to configure it
        
        Returns:
            Unconfigured workflow orchestrator
        """
        self._logger.debug("Creating workflow orchestrator")
        
        # Create the workflow orchestrator
        workflow = BaseWorkflowOrchestrator(debug_mode=self.debug_mode)
        
        return workflow
    
    def _configure_workflow(self, workflow: IWorkflowOrchestrator) -> None:
        """Configure the workflow with nodes, edges, and entry points (sync).
        
        This method can be implemented by subclasses for sync configuration:
        1. What nodes the workflow contains
        2. How nodes are connected with edges
        3. Entry points and routing logic
        
        Args:
            workflow: The workflow orchestrator to configure
        """
        # Default implementation - subclasses can override for sync configuration
        raise NotImplementedError("Subclasses must implement _configure_workflow or _configure_workflow_async")
    
    async def _configure_workflow_async(self, workflow: IWorkflowOrchestrator) -> None:
        """Configure the workflow with nodes, edges, and entry points (async).
        
        This method can be implemented by subclasses for async configuration:
        1. What nodes the workflow contains (async)
        2. How nodes are connected with edges
        3. Entry points and routing logic
        
        Args:
            workflow: The workflow orchestrator to configure
        """
        # Default implementation - subclasses can override for async configuration
        raise NotImplementedError("Subclasses must implement _configure_workflow or _configure_workflow_async")
    
    def _route_input(self, input_data: Dict[str, Any]) -> str:
        """Route to appropriate entry node based on input.
        
        This method must be implemented by subclasses to define the routing logic
        that determines which entry node to start with based on the input data.
        
        Args:
            input_data: The input data to route
            
        Returns:
            The name of the entry node to start with
        """
        # This method should be overridden by subclasses
        raise NotImplementedError("Subclasses must implement _route_input")
    
    def _create_nodes(self) -> Dict[str, INode]:
        """Create all nodes for the workflow.
        
        This method must be implemented by subclasses to create all the nodes
        that will be used in the workflow.
        
        Returns:
            Dictionary mapping node names to node instances
        """
        # This method should be overridden by subclasses
        raise NotImplementedError("Subclasses must implement _create_nodes")
    
    def _define_edges(self) -> Dict[str, str]:
        """Define the edges between nodes.
        
        This method must be implemented by subclasses to define the edges
        that connect nodes in the workflow.
        
        Returns:
            Dictionary mapping source node names to destination node names
        """
        # This method should be overridden by subclasses
        raise NotImplementedError("Subclasses must implement _define_edges") 