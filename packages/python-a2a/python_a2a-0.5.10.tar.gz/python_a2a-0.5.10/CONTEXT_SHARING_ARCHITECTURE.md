# Multi-Agent Context Sharing Architecture

## Executive Summary

Context sharing between agents is critical for building collaborative AI systems that can solve complex problems together. Currently, python-a2a agents work sequentially with limited state sharing. This document proposes a comprehensive context sharing architecture that enables parallel execution, shared memory, and sophisticated collaboration patterns similar to how Claude Code manages sequential agent tasks.

## Current State Analysis

### Limitations in python-a2a
1. **Sequential Execution**: Agents execute one at a time in workflows
2. **Limited State Transfer**: Only pass results forward through `WorkflowContext`
3. **No Shared Memory**: Each agent maintains its own isolated state
4. **No Cross-Agent Learning**: Agents can't learn from each other's experiences
5. **Static Context**: Context is passed once and not updated during execution

### What We Can Learn from Claude Code
- **Task Decomposition**: Break complex problems into smaller agent tasks
- **Context Preservation**: Maintain conversation history and learned information
- **Result Aggregation**: Combine outputs from multiple agents
- **Error Recovery**: Share error context to prevent repeated failures

## Proposed Context Sharing Patterns

### 1. **Shared Memory Store Pattern**

A centralized memory store that all agents can read from and write to during execution.

```python
class SharedContextStore:
    """
    Distributed context store for multi-agent collaboration.
    Supports real-time updates, versioning, and conflict resolution.
    """
    
    def __init__(self, backend="redis"):
        self.backend = backend
        self.store = {}
        self.locks = {}
        self.versions = {}
        self.subscriptions = defaultdict(list)
    
    async def get(self, key: str, agent_id: str) -> Any:
        """Get value with read tracking"""
        self._track_access(key, agent_id, "read")
        return self.store.get(key)
    
    async def set(self, key: str, value: Any, agent_id: str) -> None:
        """Set value with write tracking and notifications"""
        self._track_access(key, agent_id, "write")
        old_value = self.store.get(key)
        self.store[key] = value
        self.versions[key] = self.versions.get(key, 0) + 1
        
        # Notify subscribed agents
        await self._notify_subscribers(key, value, old_value, agent_id)
    
    async def subscribe(self, key: str, agent_id: str, callback: Callable):
        """Subscribe to changes in a key"""
        self.subscriptions[key].append((agent_id, callback))
```

### 2. **Blackboard Architecture Pattern**

A shared workspace where agents can post problems, partial solutions, and collaborate asynchronously.

```python
class BlackboardSystem:
    """
    Collaborative problem-solving workspace for agents.
    Agents can post problems, solutions, and vote on approaches.
    """
    
    def __init__(self):
        self.problems = []
        self.solutions = {}
        self.hypotheses = {}
        self.knowledge_sources = {}
    
    async def post_problem(self, problem: Dict, agent_id: str):
        """Post a problem for collaborative solving"""
        problem_id = str(uuid.uuid4())
        self.problems.append({
            "id": problem_id,
            "problem": problem,
            "posted_by": agent_id,
            "timestamp": time.time(),
            "status": "open"
        })
        return problem_id
    
    async def propose_solution(self, problem_id: str, solution: Any, agent_id: str):
        """Propose a solution to a problem"""
        if problem_id not in self.solutions:
            self.solutions[problem_id] = []
        
        self.solutions[problem_id].append({
            "solution": solution,
            "proposed_by": agent_id,
            "confidence": 0.0,
            "votes": [],
            "timestamp": time.time()
        })
```

### 3. **Event-Driven Context Broadcasting**

Agents broadcast context changes to interested peers through an event system.

```python
class ContextBroadcaster:
    """
    Event-driven context broadcasting system.
    Agents can emit and listen to context change events.
    """
    
    def __init__(self):
        self.event_bus = EventBus()
        self.context_streams = {}
        
    async def broadcast_context(self, context: Dict, agent_id: str, event_type: str):
        """Broadcast context update to all interested agents"""
        event = ContextEvent(
            type=event_type,
            context=context,
            source_agent=agent_id,
            timestamp=time.time()
        )
        
        await self.event_bus.emit(event)
    
    async def subscribe_to_context(self, agent_id: str, event_types: List[str], 
                                   handler: Callable):
        """Subscribe to specific context event types"""
        for event_type in event_types:
            self.event_bus.subscribe(event_type, agent_id, handler)
```

### 4. **Hierarchical Context Inheritance**

Parent-child agent relationships where context flows hierarchically.

```python
class HierarchicalContextManager:
    """
    Manages hierarchical context inheritance between agents.
    Child agents inherit parent context with ability to override.
    """
    
    def __init__(self):
        self.agent_hierarchy = {}
        self.contexts = {}
    
    def create_child_context(self, parent_agent_id: str, child_agent_id: str):
        """Create child context that inherits from parent"""
        parent_context = self.contexts.get(parent_agent_id, {})
        child_context = ChainMap({}, parent_context)
        self.contexts[child_agent_id] = child_context
        
        # Track hierarchy
        if parent_agent_id not in self.agent_hierarchy:
            self.agent_hierarchy[parent_agent_id] = []
        self.agent_hierarchy[parent_agent_id].append(child_agent_id)
        
        return child_context
```

### 5. **Conversation Memory Pattern**

Shared conversation history and learned information across agent interactions.

```python
class ConversationMemory:
    """
    Shared conversation memory with semantic search and summarization.
    """
    
    def __init__(self):
        self.short_term = deque(maxlen=100)  # Recent interactions
        self.long_term = {}  # Summarized knowledge
        self.embeddings = {}  # Semantic search index
        
    async def add_interaction(self, agent_id: str, user_msg: str, 
                              agent_response: str, metadata: Dict):
        """Add interaction to memory with indexing"""
        interaction = {
            "agent_id": agent_id,
            "user_message": user_msg,
            "agent_response": agent_response,
            "metadata": metadata,
            "timestamp": time.time()
        }
        
        # Add to short-term memory
        self.short_term.append(interaction)
        
        # Generate embedding for semantic search
        embedding = await self._generate_embedding(f"{user_msg} {agent_response}")
        self.embeddings[str(uuid.uuid4())] = {
            "embedding": embedding,
            "interaction": interaction
        }
        
        # Trigger summarization if needed
        if len(self.short_term) >= 50:
            await self._summarize_to_long_term()
    
    async def search_relevant_context(self, query: str, k: int = 5) -> List[Dict]:
        """Search for relevant past interactions"""
        query_embedding = await self._generate_embedding(query)
        
        # Find k most similar interactions
        similarities = []
        for id, item in self.embeddings.items():
            similarity = self._cosine_similarity(query_embedding, item["embedding"])
            similarities.append((similarity, item["interaction"]))
        
        similarities.sort(reverse=True, key=lambda x: x[0])
        return [interaction for _, interaction in similarities[:k]]
```

## Implementation Strategy

### Phase 1: Foundation (Week 1-2)
```python
# 1. Create base context sharing interfaces
class IContextProvider(Protocol):
    async def get_context(self, key: str) -> Any: ...
    async def set_context(self, key: str, value: Any) -> None: ...
    async def subscribe(self, key: str, callback: Callable) -> None: ...

# 2. Implement Redis-backed shared store
class RedisContextStore(IContextProvider):
    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(redis_url)
        self.pubsub = self.redis.pubsub()
    
    async def get_context(self, key: str) -> Any:
        value = await self.redis.get(key)
        return json.loads(value) if value else None
    
    async def set_context(self, key: str, value: Any) -> None:
        await self.redis.set(key, json.dumps(value))
        await self.redis.publish(f"context:{key}", json.dumps(value))
```

### Phase 2: Integration (Week 3-4)
```python
# 1. Extend A2AClient with context sharing
class ContextAwareA2AClient(A2AClient):
    def __init__(self, *args, context_store: IContextProvider, **kwargs):
        super().__init__(*args, **kwargs)
        self.context_store = context_store
        self.agent_id = str(uuid.uuid4())
    
    async def send_message_with_context(self, message: Message) -> Message:
        # Inject relevant context
        context = await self._gather_relevant_context(message)
        message.metadata = {**message.metadata, "shared_context": context}
        
        # Send message
        response = await self.send_message_async(message)
        
        # Update shared context with response
        await self._update_shared_context(response)
        
        return response

# 2. Create context-aware workflow engine
class ContextAwareFlow(Flow):
    def __init__(self, *args, context_store: IContextProvider, **kwargs):
        super().__init__(*args, **kwargs)
        self.context_store = context_store
    
    async def execute_parallel_with_context(self, steps: List[WorkflowStep]):
        """Execute steps in parallel with shared context"""
        tasks = []
        for step in steps:
            # Each step gets access to shared context
            task = self._execute_step_with_context(step)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # Merge results into shared context
        await self._merge_results_to_context(results)
        
        return results
```

### Phase 3: Advanced Features (Week 5-6)
```python
# 1. Implement conflict resolution
class ConflictResolver:
    """Resolve conflicts when multiple agents update same context"""
    
    async def resolve(self, key: str, values: List[Tuple[str, Any]]) -> Any:
        # Strategy 1: Last Write Wins
        # Strategy 2: Voting
        # Strategy 3: Merge semantically
        pass

# 2. Add context versioning
class VersionedContext:
    """Track context changes over time"""
    
    def __init__(self):
        self.versions = defaultdict(list)
    
    async def save_version(self, key: str, value: Any, agent_id: str):
        self.versions[key].append({
            "value": value,
            "agent_id": agent_id,
            "timestamp": time.time(),
            "version": len(self.versions[key]) + 1
        })
    
    async def get_history(self, key: str) -> List[Dict]:
        return self.versions[key]

# 3. Implement context compression
class ContextCompressor:
    """Compress large contexts for efficient sharing"""
    
    async def compress(self, context: Dict) -> bytes:
        # Use MessagePack or similar for efficient serialization
        pass
    
    async def decompress(self, data: bytes) -> Dict:
        pass
```

## Use Cases and Examples

### 1. **Multi-Agent Research Task**
```python
async def collaborative_research(topic: str):
    # Create shared context store
    context_store = SharedContextStore()
    
    # Create specialized agents with shared context
    researcher = ContextAwareA2AClient("http://researcher-agent", context_store)
    analyst = ContextAwareA2AClient("http://analyst-agent", context_store)
    writer = ContextAwareA2AClient("http://writer-agent", context_store)
    
    # Phase 1: Research (parallel)
    research_tasks = [
        researcher.research_subtopic(f"{topic} - technical aspects"),
        researcher.research_subtopic(f"{topic} - business implications"),
        researcher.research_subtopic(f"{topic} - future trends")
    ]
    
    research_results = await asyncio.gather(*research_tasks)
    
    # Results automatically shared via context store
    await context_store.set("research_findings", research_results, "researcher")
    
    # Phase 2: Analysis (can access research findings)
    analysis = await analyst.analyze_with_context()
    
    # Phase 3: Writing (has access to both research and analysis)
    report = await writer.generate_report_with_context()
    
    return report
```

### 2. **Debugging Assistant Network**
```python
async def collaborative_debugging(error: Exception, code_context: str):
    blackboard = BlackboardSystem()
    
    # Post problem to blackboard
    problem_id = await blackboard.post_problem({
        "error": str(error),
        "code": code_context,
        "stack_trace": traceback.format_exc()
    }, "main")
    
    # Multiple agents propose solutions concurrently
    agents = [
        ErrorAnalyzer(),
        CodeFixer(),
        TestGenerator(),
        DocumentationAgent()
    ]
    
    tasks = []
    for agent in agents:
        task = agent.solve_on_blackboard(problem_id, blackboard)
        tasks.append(task)
    
    # Wait for all agents to contribute
    await asyncio.gather(*tasks)
    
    # Get best solution based on voting
    best_solution = await blackboard.get_best_solution(problem_id)
    
    return best_solution
```

### 3. **Customer Support Escalation**
```python
async def handle_customer_query(query: str):
    # Hierarchical context for escalation
    context_manager = HierarchicalContextManager()
    
    # Level 1: Basic support bot
    l1_agent = SupportAgent(level=1, context_manager=context_manager)
    response = await l1_agent.handle(query)
    
    if not response.resolved:
        # Level 2: Specialist with L1 context
        l2_agent = SpecialistAgent(level=2, parent=l1_agent.id, 
                                   context_manager=context_manager)
        response = await l2_agent.handle_with_context(query)
    
    if not response.resolved:
        # Level 3: Expert with full context chain
        l3_agent = ExpertAgent(level=3, parent=l2_agent.id,
                              context_manager=context_manager)
        response = await l3_agent.handle_with_full_context(query)
    
    return response
```

## Performance Considerations

### 1. **Context Size Management**
- Implement context pruning for large contexts
- Use semantic compression to reduce redundancy
- Cache frequently accessed context locally

### 2. **Latency Optimization**
- Use Redis pub/sub for real-time updates
- Implement context prefetching for predictable workflows
- Batch context updates to reduce network overhead

### 3. **Scalability**
- Partition context by domain or agent group
- Use distributed caching (Redis Cluster)
- Implement context sharding for large deployments

## Security and Privacy

### 1. **Access Control**
```python
class SecureContextStore:
    async def get_context(self, key: str, agent_id: str, permissions: List[str]):
        # Check if agent has read permission
        if not self.check_permission(key, agent_id, "read", permissions):
            raise PermissionError(f"Agent {agent_id} cannot read {key}")
        
        # Optionally redact sensitive information
        value = await self.store.get(key)
        return self.redact_sensitive(value, permissions)
```

### 2. **Audit Logging**
```python
class AuditedContextStore:
    async def audit_log(self, action: str, key: str, agent_id: str, value: Any):
        log_entry = {
            "timestamp": time.time(),
            "action": action,
            "key": key,
            "agent_id": agent_id,
            "value_hash": hashlib.sha256(str(value).encode()).hexdigest()
        }
        await self.audit_store.append(log_entry)
```

## Monitoring and Observability

### 1. **Context Metrics**
- Context access patterns (reads/writes per agent)
- Context size and growth rate
- Conflict resolution frequency
- Cache hit rates

### 2. **Context Tracing**
```python
class TracedContext:
    def __init__(self):
        self.tracer = opentelemetry.trace.get_tracer(__name__)
    
    async def get_context(self, key: str, agent_id: str):
        with self.tracer.start_as_current_span("context.get") as span:
            span.set_attribute("context.key", key)
            span.set_attribute("agent.id", agent_id)
            
            value = await self.store.get(key)
            
            span.set_attribute("context.size", len(str(value)))
            return value
```

## Migration Path

### Step 1: Add Optional Context Store
```python
# Backward compatible change
class A2AClient:
    def __init__(self, *args, context_store: Optional[IContextProvider] = None, **kwargs):
        # Existing code...
        self.context_store = context_store
```

### Step 2: Gradual Feature Adoption
1. Start with read-only shared context
2. Add write capabilities for specific use cases
3. Implement subscription/notification system
4. Enable full bidirectional context sharing

### Step 3: Default Context Sharing
```python
# Future version with context sharing by default
class A2AClient:
    def __init__(self, *args, **kwargs):
        # Auto-create context store if not provided
        self.context_store = kwargs.get('context_store') or DefaultContextStore()
```

## Conclusion

Context sharing transforms python-a2a from sequential agent execution to true multi-agent collaboration. By implementing these patterns, we enable:

1. **Parallel Problem Solving**: Agents work simultaneously on different aspects
2. **Collective Intelligence**: Agents learn from each other's experiences
3. **Fault Tolerance**: Shared context enables recovery and retry strategies
4. **Scalability**: Distributed context allows horizontal scaling
5. **Auditability**: Complete trace of agent interactions and decisions

The proposed architecture maintains backward compatibility while enabling powerful new collaboration patterns that match and exceed the capabilities of sequential agent systems like Claude Code.

---

*Document created: 2025-09-06*  
*Focus: Enabling true multi-agent collaboration through sophisticated context sharing*