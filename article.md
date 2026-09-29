# Hindsight’s async memory saves kept chat turns from waiting

When a support conversation ends, there are two jobs to do: answer the customer and make the conversation useful to the next agent. I wanted the first job to feel immediate without giving up the second. That led me to a small but consequential choice in NetNest: save each live turn with Hindsight’s asynchronous retention mode.

The word “async” needs a precise definition here. The application still makes a retention API call before `respond` returns; it does not launch a detached local task and forget about it. What it avoids is waiting for Hindsight to finish processing and consolidating the retained conversation before the chat can continue. That boundary matters. It is the difference between keeping a conversation responsive and pretending persistence has no cost.

## A support agent with customer-specific memory

NetNest is a broadband support assistant. Its job is not just to answer “my Wi-Fi dropped” with generic troubleshooting. It should know whether that customer has already power-cycled the router, which replacement device also failed, whether a technician is scheduled, and how the customer prefers to communicate.

The app is split into a Streamlit interface, an agent orchestration layer, and a Hindsight memory adapter. `app.py` owns the chat state and sends each new message to `agent.respond`. The agent assembles a prompt from recent chat history, the current customer’s Hindsight profile, recalled observations and ticket details, and support rules. It then generates a reply and saves the exchange so later turns can use it.

Customer identity maps to a separate Hindsight bank. This gives recall a clear boundary: a query for Bre’s history should not pull in Gavin’s modem setup. The memory adapter also makes the shape of that context explicit. It recalls consolidated observations separately from raw world and experience memories, then limits how much of each layer enters the prompt.

That structure reflects how support history gets used. A consolidated belief such as “reboots and a replacement router did not stop the evening drops” is useful for deciding what to do next. A dated raw detail is useful when the customer asks what happened before. One undifferentiated list of facts makes both jobs harder.

## The response path and the memory path

I treat response generation and durable learning as related work with different latency expectations. Before generating a reply, the agent retrieves relevant memory because it changes what the agent should say now. After generating the reply, it retains the exchange so that future conversations can benefit.

The live save packages both sides of the interaction and the customer’s current mood:

```python
content = f"{name} said: {customer_msg}\nSupport agent replied: {agent_reply}"
if mood:
    content += f"\n{name}'s mood: {mood}"
_run(lambda c: c.retain(
    bank_id=bank_for(customer_id),
    content=content,
    context="support conversation",
    timestamp=timestamp,
    retain_async=not wait,
))
```

The `wait` flag gives ingestion two modes. Live chat defaults to `wait=False`, which maps to `retain_async=True`; historical seeding can pass `wait=True` and wait for processing. That distinction is useful operationally. Bulk ingestion needs a known completion point before I depend on the seeded history. A live customer should not have to wait for consolidation to finish before moving to the next turn.

This is not a blanket claim that memory writes have zero latency. `_run` creates a worker thread and a fresh Hindsight client, and waits for the client operation to return. The asynchronous behavior applies to Hindsight’s retention processing. I keep that distinction visible because otherwise “async” becomes a misleading promise about the whole request path.

## Why retaining the reply matters

It is tempting to save only what the customer said. In a support workflow, that leaves out what the agent tried, promised, or concluded. If the next conversation starts with “the line is probably the issue after the replacement router failed,” that conclusion came from the whole exchange, not from the customer’s last sentence alone.

The agent includes the response and a frustration score in the retained content. The next turn can then recall both the technical trajectory and some emotional context. The code uses the customer’s first name in the retained text because Hindsight can use the named person as an entity to associate with the memory.

The prompt makes the intended behavior concrete:

```text
Key beliefs from their history:
{observations}

Relevant detail from past tickets:
{raw}

Rules (stored in the memory bank, follow strictly):
{rules}
- Never ask for information you already have above.
- If this is a repeat problem, acknowledge it briefly and skip basic troubleshooting.
```

For a customer whose router has already been rebooted, reset, and replaced, the useful next answer is not another reboot checklist. It is an acknowledgement of the failed attempts and a move toward signal investigation or escalation. Hindsight does not make that decision automatically; it supplies durable context, while the agent prompt and support directives turn that context into a response policy.

## Retrieval still belongs on the critical path

Asynchronous retention does not remove the need to retrieve history before answering. In `agent.respond`, frustration scoring runs concurrently with profile and context retrieval. The memory adapter uses two recall calls in one client session: observations first, then a smaller set of raw details.

```python
obs = c.recall(
    bank_id=bank, query=message, types=["observation"],
    budget="mid", max_tokens=800)
raw = c.recall(
    bank_id=bank, query=message, types=["world", "experience"],
    budget="mid", max_tokens=600)
```

The token limits are deliberate. Profile text, observations, raw memories, rules, and recent chat all compete for prompt space. Sending every stored fact would increase cost and bury the relevant information. The two-layer retrieval asks Hindsight for a concise, deduplicated view first, then a few details that can support a specific answer. The result is bounded context, not a full transcript.

There is also a practical concurrency wrinkle: Streamlit reruns its script around user interactions, and the Hindsight client’s async internals did not behave well when called directly from Streamlit’s thread. The adapter runs a client operation in a fresh worker thread and closes the client with a context manager. That avoids leaking sessions and gives those internals a clean event-loop context. It is a narrow fix, not a reason to move every operation into a thread pool.

I launch frustration scoring independently because it does not depend on memory. Profile and recall work can also overlap. The response still waits for the information it actually needs to construct a context-aware prompt. That is a sensible place to spend latency: stale or missing context can cause the agent to repeat a failed step.

## What the customer should experience

Consider this sequence: a customer says the connection is dropping again; then clarifies that it happens every evening after 7 PM; then says this is the fourth time they have explained it. With memory enabled, the agent can use the customer profile and recalled history to recognize a recurring pattern, mention prior failed fixes, and avoid reopening basic troubleshooting. The stored exchange gives a later turn or later support session something durable to recall.

With memory disabled, the system intentionally falls back to generic tier-one behavior. That comparison makes the design observable: memory is not a decorative transcript panel. It changes the context supplied to the model and, consequently, which steps the agent should skip. The code does not establish a measured reduction in resolution time or a benchmarked accuracy gain, so I would not claim either. The concrete behavior to inspect is whether the reply asks for a step the history says already failed.

The same memory bank can support escalation. After consecutive high-frustration turns, the app calls Hindsight’s `reflect` API to produce a short handoff brief describing who the customer is, what has been tried, what worked or failed, and their current mood. That lets the receiving human start with the accumulated case rather than asking the customer to reconstruct it from scratch.

## What I learned

### 1. Put expensive processing after the customer-facing answer

Not every persistence operation has to complete its full processing pipeline before the user can continue. Decide which parts of persistence must be acknowledged synchronously and which can finish asynchronously. Here, retention is requested during the turn, but Hindsight’s deeper processing need not finish first.

### 2. Save the interaction, not just the utterance

The customer’s statement is only half the support record. Saving the agent’s reply and relevant mood gives future retrieval the attempted action and the conversational outcome too. That context is what helps a later response avoid repeating the same loop.

### 3. Separate summary from evidence

Observations and raw memories serve different retrieval needs. A concise belief is useful for triage; a specific dated fact is useful for reconstructing what happened. Keeping the layers separate makes it easier to bound the prompt and inspect what the agent was given.

### 4. Say exactly what is asynchronous

The current code waits for the retain call to return, while asking Hindsight not to wait for retention processing to complete. That is a real latency boundary, but it is not fire-and-forget application code. Naming the boundary honestly makes future measurements and reliability decisions possible.

Hindsight provides the memory operations that make this design possible: retaining conversation history, recalling relevant context, maintaining a customer mental model, and reflecting over a bank to prepare a handoff. The [Hindsight GitHub repository](https://github.com/vectorize-io/hindsight) and [Hindsight documentation](https://hindsight.vectorize.io/) describe the underlying system and API. For a broader framing of persistent context in agent systems, see [Vectorize’s guide to agent memory](https://vectorize.io/what-is-agent-memory).

The engineering point is modest: a chat response and a durable memory update do not need to share the same completion boundary. Hindsight’s asynchronous retention lets NetNest capture the exchange without waiting for all memory processing to finish, while retrieval remains on the next answer’s critical path. That division keeps the conversation moving and gives future turns a history worth remembering.
