# This file makes zeus a proper package namespace
# Import everything from the parent package
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import everything from the main package
from layers import *

# Define package metadata
__version__ = "3.0.0"
__author__ = "Agent Development Center Team"
__email__ = "support@zeus-ai.com"
__license__ = "MIT"
__description__ = "Zeus AI Platform - Next-generation AI Agent Development Platform"

__all__ = [
    # Basic abstractions
    "UniversalAgent",
    "AgentCapability", 
    "AgentStatus",
    "UniversalTask",
    "TaskType",
    "TaskPriority",
    "TaskRequirements",
    "UniversalContext",
    "UniversalResult",
    "ResultStatus",
    "ResultType",
    "ResultMetadata",
    
    # Cognitive abstractions
    "CognitiveUniversalAgent",
    "AgentType",
    
    # Team abstractions
    "UniversalTeam",
    "TeamType", 
    "TeamConfig",
    "CommunicationPattern",
    
    # Factory
    "AgentFactoryManager",
    
    # A2A Protocol
    "A2AMessageType",
    "A2ACapabilityType",
    "A2AProtocolVersion",
    "A2AMessage",
    "A2AProtocolHandler",
    
    # Integration
    "A2AIntegrationManager",
    "A2AAdapterBridge", 
    "A2AMessageRouter",
    
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__description__",
]
