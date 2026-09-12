"""
Agent Orchestration - Verifiable register of agents, authorizations, and human supervisors.

Maps to the Eight-Domain Stack "Agent Orchestration" domain:
  - Verifiable register of agent authorizations
  - Human supervisor tracking
  - Authorization scope enforcement
"""

from .registry import AgentRegistry, AgentRegistration, Supervisor, Authorization

__all__ = ["AgentRegistry", "AgentRegistration", "Supervisor", "Authorization"]
