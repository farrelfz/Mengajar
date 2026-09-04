# Orchestration Architecture

This document describes the orchestration control plane coordinating the document production lifecycle.

## Architecture Topology

```mermaid
graph TD
    Request[Production Request] --> Engine[Production Orchestrator]
    Engine --> Profile[Profile Resolver]
    Profile --> Graph[Workflow DAG Graph]
    Graph --> SM[Workflow State Machine]
    
    subgraph Execution Loop
        SM --> Exec[Stage Executor]
        Exec --> validation[Request Validation Stage]
        Exec --> directing[Material Directing Stage]
        Exec --> personalization[Personalization Stage]
        Exec --> grounding[Knowledge Grounding Stage]
        Exec --> blueprint[Blueprint Stage]
        Exec --> composition[Composition Stage]
        Exec --> quality[Quality Stage]
        Exec --> render[Rendering Stage]
    end
    
    quality --> Gate{Quality Gate}
    Gate -->|Pass| render
    Gate -->|Fail| Critic[Critic Stage]
    Critic --> Refine[Refinement Stage]
    Refine --> quality
    
    render --> Checkpoint[Checkpoint Store]
    Checkpoint --> Trace[Execution Trace]
    Trace --> Result[Pipeline Result]
```

## Key Invariants
- **Control Plane Decoupling**: Subsystems (intelligence, composition, rendering) are isolated. Stage adapters interface with them without absorbing logic.
- **Topological Stage Validation**: The system validates node ordering and dependencies before execution begins.
- **Graceful Failures**: Standardized failure tracking prevents unhandled crashes.
