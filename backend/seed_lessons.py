#!/usr/bin/env python3
"""
Seed script for B1 LMS - Populates database with lesson content

Usage:
    python manage.py shell < seed_lessons.py

This script creates 3 lessons on AI agent fundamentals:
- Module 00: LLM API Communication
- Module 01: Pydantic Pattern & Tool Use
- Module 02: Conversational Memory
"""

from lms.models import Lesson

# Clear existing lessons (development only)
print("Clearing existing lessons...")
Lesson.objects.all().delete()

# Module 00: LLM API Communication
lesson_00_content = """# Module 00: LLM API Communication

## Introduction

Understanding how to communicate with Large Language Models (LLMs) through APIs is the foundation of building AI agents. In this module, you'll learn the core patterns and concepts that power modern AI assistants.

## What is an LLM API?

An **LLM API** (Large Language Model Application Programming Interface) is a web service that allows you to send text to a language model and receive generated responses. Think of it as a conversation interface, but instead of clicking buttons in a chat app, you send structured data over HTTP.

### Key Concept: Request/Response Pattern

Every interaction with an LLM follows this pattern:

```
You (Client)  →  [API Request]   →  LLM Server
                                         ↓
                                    Processing
                                         ↓
You (Client)  ←  [API Response]  ←  LLM Server
```

## Anatomy of an API Request

When you call an LLM API, you typically send:

### 1. **Model Selection**
Which version of the LLM to use (e.g., `claude-3-5-sonnet-20241022`, `gpt-4-turbo`)

### 2. **Messages Array**
A list of messages representing the conversation history. Each message has:
- **role**: Who sent it (`user`, `assistant`, or `system`)
- **content**: The actual text

### 3. **Parameters** (optional)
Settings that control the response:
- **temperature** (0.0-1.0): Creativity vs determinism
- **max_tokens**: Maximum response length
- **stop_sequences**: Strings that halt generation

## Example: Anthropic Claude API

Here's a real API request using Python:

```python
import anthropic

client = anthropic.Anthropic(api_key="your-api-key")

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Explain what an API is in one sentence."
        }
    ]
)

print(response.content[0].text)
```

**Output:**
```
An API (Application Programming Interface) is a set of rules and protocols
that allows different software applications to communicate and exchange data
with each other.
```

## Message Roles Explained

### **User Role**
Messages from the human or application making the request.

```python
{"role": "user", "content": "What is Python?"}
```

### **Assistant Role**
Messages from the AI assistant (previous responses in a conversation).

```python
{"role": "assistant", "content": "Python is a high-level programming language..."}
```

### **System Role** (Optional)
Special instructions that guide the assistant's behavior throughout the conversation.

```python
{"role": "system", "content": "You are a helpful coding tutor. Keep answers concise."}
```

**Note:** Different APIs handle system messages differently. Anthropic uses a separate `system` parameter instead of a message role.

## Multi-Turn Conversations

To maintain context across multiple exchanges, you send the entire conversation history:

```python
messages = [
    {"role": "user", "content": "What is Python?"},
    {"role": "assistant", "content": "Python is a high-level programming language..."},
    {"role": "user", "content": "What can I build with it?"}
]

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=messages
)
```

The LLM can now reference previous context ("What can I build with **it**?" - it knows "it" = Python).

## Response Structure

An API response typically contains:

```python
{
    "id": "msg_01AbC123",
    "type": "message",
    "role": "assistant",
    "content": [
        {
            "type": "text",
            "text": "You can build web apps, data pipelines, ML models..."
        }
    ],
    "model": "claude-3-5-sonnet-20241022",
    "stop_reason": "end_turn",
    "usage": {
        "input_tokens": 15,
        "output_tokens": 58
    }
}
```

**Key Fields:**
- `content`: The generated text (can be multiple blocks)
- `stop_reason`: Why generation stopped (`end_turn`, `max_tokens`, `stop_sequence`)
- `usage`: Token consumption (important for billing)

## Basic Agent Loop

The simplest AI agent is just a loop that:

1. Receives user input
2. Sends it to the LLM API
3. Displays the response
4. Repeats

```python
def simple_agent():
    conversation_history = []

    while True:
        # Get user input
        user_input = input("You: ")
        if user_input.lower() == "quit":
            break

        # Add to conversation history
        conversation_history.append({
            "role": "user",
            "content": user_input
        })

        # Call LLM API
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=conversation_history
        )

        # Extract response text
        assistant_message = response.content[0].text

        # Add to conversation history
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        # Display response
        print(f"Assistant: {assistant_message}")
```

**Example Interaction:**
```
You: What is 2+2?
Assistant: 2+2 equals 4.

You: What about if I add 3 to that?
Assistant: If you add 3 to 4, you get 7.
```

Notice how the agent remembers "that" refers to 4.

## Key Takeaways

✅ **LLM APIs use HTTP request/response** - just like any web API

✅ **Messages have roles** - `user`, `assistant`, `system` (context matters)

✅ **Conversation history is manual** - you must send previous messages for context

✅ **Responses are structured** - parse the response object to extract text

✅ **Token usage matters** - each API call consumes tokens (costs money)

## What's Next?

Now that you understand basic API communication, the next module covers **Tool Use** - how agents can call functions and interact with external systems.

---

*"The beginning of wisdom is this: Get wisdom." - Proverbs 4:7 (KJV)*
"""

lesson_00_quiz = {
    "questions": [
        {
            "text": "What three roles can messages have in an LLM API conversation?",
            "options": [
                "user, assistant, system",
                "client, server, admin",
                "input, output, context",
                "human, ai, moderator"
            ],
            "correct": 1
        },
        {
            "text": "Why do you need to send conversation history with each API request?",
            "options": [
                "To save bandwidth",
                "LLMs are stateless - they don't remember previous requests",
                "To improve response speed",
                "It's optional and not recommended"
            ],
            "correct": 2
        },
        {
            "text": "What does the 'temperature' parameter control?",
            "options": [
                "API response time",
                "Token cost",
                "Creativity vs determinism in responses",
                "Maximum conversation length"
            ],
            "correct": 3
        },
        {
            "text": "What is the purpose of the 'max_tokens' parameter?",
            "options": [
                "Limit the length of the response",
                "Set the API timeout",
                "Control conversation history size",
                "Define model accuracy"
            ],
            "correct": 1
        },
        {
            "text": "In the basic agent loop, why is conversation_history a list?",
            "options": [
                "Lists are faster than dictionaries",
                "To store multiple messages in order for context",
                "To support parallel conversations",
                "To enable message encryption"
            ],
            "correct": 2
        }
    ]
}

lesson_00 = Lesson.objects.create(
    lesson_id="module-00",
    title="LLM API Communication",
    subtitle="Learn the fundamentals of communicating with Large Language Models",
    content=lesson_00_content,
    module_number=0,
    order_index=0,
    quiz_data=lesson_00_quiz
)

print(f"✓ Created: {lesson_00}")

# Module 01: Pydantic Pattern & Tool Use
lesson_01_content = """# Module 01: Pydantic Pattern & Tool Use

## Introduction

In Module 00, you learned how to send messages to an LLM and get text responses. But what if you want the LLM to **do something** - like search the web, query a database, or send an email? That's where **tool use** comes in.

## What is Tool Use?

**Tool use** (also called "function calling") allows an LLM to request that external functions be executed. Instead of just generating text, the LLM can:

1. Recognize when it needs external data or actions
2. Request that a specific tool be called with specific parameters
3. Receive the tool's output
4. Continue generating a response using that data

### Example Scenario

**User:** "What's the weather in San Francisco?"

**Without tools:** "I don't have access to real-time weather data, but San Francisco typically..."

**With tools:**
1. LLM requests: `get_weather(location="San Francisco, CA")`
2. Your code calls actual weather API
3. Returns: `{"temp": 62, "conditions": "Partly cloudy"}`
4. LLM responds: "It's currently 62°F and partly cloudy in San Francisco."

## How Tool Use Works

### Step 1: Define Available Tools

You tell the LLM what functions are available:

```python
tools = [
    {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and state, e.g. 'San Francisco, CA'"
                }
            },
            "required": ["location"]
        }
    }
]
```

### Step 2: LLM Requests Tool Use

When the LLM determines it needs to use a tool, it returns a `tool_use` response:

```python
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=tools,
    messages=[
        {"role": "user", "content": "What's the weather in Boston?"}
    ]
)

# Response contains:
{
    "stop_reason": "tool_use",
    "content": [
        {
            "type": "tool_use",
            "id": "toolu_01A2B3C4",
            "name": "get_weather",
            "input": {"location": "Boston, MA"}
        }
    ]
}
```

### Step 3: Execute the Tool

Your code actually runs the function:

```python
def get_weather(location):
    # Call real weather API
    api_response = weather_api.get_current(location)
    return {
        "temp": api_response["temperature"],
        "conditions": api_response["conditions"]
    }

# Execute tool
tool_result = get_weather("Boston, MA")
# Returns: {"temp": 45, "conditions": "Rainy"}
```

### Step 4: Send Tool Result Back

You send the result back to the LLM:

```python
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=tools,
    messages=[
        {"role": "user", "content": "What's the weather in Boston?"},
        {"role": "assistant", "content": response.content},
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": "toolu_01A2B3C4",
                    "content": json.dumps(tool_result)
                }
            ]
        }
    ]
)

# LLM now responds with:
"It's currently 45°F and rainy in Boston."
```

## Pydantic for Data Validation

**Pydantic** is a Python library for data validation using type hints. It's perfect for validating tool inputs and outputs.

### Why Use Pydantic?

❌ **Without Pydantic:**
```python
def get_weather(location):
    # What if location is None? A number? An empty string?
    # What if it's missing?
    # Manual validation needed!
    if not location or not isinstance(location, str):
        raise ValueError("Invalid location")
    ...
```

✅ **With Pydantic:**
```python
from pydantic import BaseModel, Field

class WeatherInput(BaseModel):
    location: str = Field(description="City and state, e.g. 'San Francisco, CA'")
    units: str = Field(default="fahrenheit", description="Temperature units")

def get_weather(input: WeatherInput):
    # input.location is GUARANTEED to be a string
    # input.units defaults to "fahrenheit" if not provided
    ...
```

### Pydantic Automatically:
- ✅ Validates types (string, int, float, bool)
- ✅ Enforces required fields
- ✅ Provides default values
- ✅ Converts types when possible (`"42"` → `42`)
- ✅ Generates JSON schemas for LLMs

### Converting Pydantic to Tool Schema

```python
class WeatherInput(BaseModel):
    location: str = Field(description="City and state")
    units: str = Field(default="fahrenheit")

# Pydantic can generate the tool schema automatically!
tool_schema = {
    "name": "get_weather",
    "description": "Get current weather",
    "input_schema": WeatherInput.model_json_schema()
}
```

**Generated schema:**
```json
{
    "type": "object",
    "properties": {
        "location": {
            "type": "string",
            "description": "City and state"
        },
        "units": {
            "type": "string",
            "default": "fahrenheit"
        }
    },
    "required": ["location"]
}
```

## The Agent Loop with Tools

Here's how a tool-using agent works:

```python
def agent_with_tools(user_message):
    messages = [{"role": "user", "content": user_message}]

    while True:
        # Call LLM
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )

        # Check stop reason
        if response.stop_reason == "end_turn":
            # LLM is done, return final response
            return response.content[0].text

        elif response.stop_reason == "tool_use":
            # LLM wants to use a tool
            tool_use = response.content[0]
            tool_name = tool_use.name
            tool_input = tool_use.input

            # Execute the tool
            if tool_name == "get_weather":
                result = get_weather(**tool_input)

            # Add assistant message + tool result to history
            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": json.dumps(result)
                }]
            })

            # Loop continues - LLM will use the result
```

**Flow:**
1. User asks question
2. LLM requests tool
3. Tool executes
4. Result sent back to LLM
5. LLM generates final answer

## Multiple Tools

Agents can have access to many tools:

```python
tools = [
    {
        "name": "get_weather",
        "description": "Get current weather",
        "input_schema": {...}
    },
    {
        "name": "search_web",
        "description": "Search the internet",
        "input_schema": {...}
    },
    {
        "name": "send_email",
        "description": "Send an email",
        "input_schema": {...}
    }
]
```

The LLM will choose which tool to use based on the user's request.

**User:** "Email me the weather forecast"

**Agent:**
1. Uses `get_weather` → gets forecast
2. Uses `send_email` → sends email with forecast

## Key Takeaways

✅ **Tool use lets LLMs take actions** - not just generate text

✅ **Tools are defined with schemas** - describe name, parameters, types

✅ **LLMs request tools, you execute them** - LLMs don't run code directly

✅ **Pydantic validates data** - ensures tool inputs are correct types

✅ **Agent loop handles tool calls** - back-and-forth until task complete

✅ **Multiple tools enable complex tasks** - LLM chooses the right tool

## What's Next?

You now understand how agents use tools to interact with the world. In Module 02, you'll learn about **Conversational Memory** - how to manage long conversations and context efficiently.

---

*"A wise man will hear, and will increase learning" - Proverbs 1:5 (KJV)*
"""

lesson_01_quiz = {
    "questions": [
        {
            "text": "What is 'tool use' in the context of LLM agents?",
            "options": [
                "Teaching the LLM to write better code",
                "Allowing the LLM to request external functions be executed",
                "Using tools to build the LLM",
                "Debugging LLM responses"
            ],
            "correct": 2
        },
        {
            "text": "What does the LLM return when it wants to use a tool?",
            "options": [
                "A Python function call",
                "An error message",
                "A tool_use response with the tool name and parameters",
                "Direct API access credentials"
            ],
            "correct": 3
        },
        {
            "text": "What is the main benefit of using Pydantic for tool inputs?",
            "options": [
                "Faster API responses",
                "Automatic data validation and type checking",
                "Reduced token usage",
                "Better LLM accuracy"
            ],
            "correct": 2
        },
        {
            "text": "In the agent loop with tools, what happens after a tool executes?",
            "options": [
                "The conversation ends",
                "The tool result is sent back to the LLM to continue generation",
                "A new agent starts",
                "The user must approve the result"
            ],
            "correct": 2
        },
        {
            "text": "Can an LLM execute tools directly (run code on its own)?",
            "options": [
                "Yes, LLMs can execute any Python code",
                "Only with special permissions",
                "No, the LLM requests tools and your code executes them",
                "Yes, but only JavaScript"
            ],
            "correct": 3
        }
    ]
}

lesson_01 = Lesson.objects.create(
    lesson_id="module-01",
    title="Pydantic Pattern & Tool Use",
    subtitle="Explore how agents use tools and structured data validation",
    content=lesson_01_content,
    module_number=1,
    order_index=1,
    quiz_data=lesson_01_quiz
)

print(f"✓ Created: {lesson_01}")

# Module 02: Conversational Memory
lesson_02_content = """# Module 02: Conversational Memory

## Introduction

In Modules 00 and 01, you learned how to communicate with LLMs and give them tools. But as conversations grow longer, a critical challenge emerges: **how do you manage memory?**

LLMs are **stateless** - they don't remember anything between API calls. Every request is independent. To maintain context, you must send conversation history with every request. But there's a limit to how much history you can send.

This module teaches you how to manage conversational memory effectively.

## The Context Window Problem

Every LLM has a **context window** - the maximum amount of text it can process in a single request.

### Example Context Windows:
- **GPT-4 Turbo**: ~128,000 tokens (~96,000 words)
- **Claude 3.5 Sonnet**: ~200,000 tokens (~150,000 words)
- **Claude 3 Opus**: ~200,000 tokens (~150,000 words)

**One token ≈ 0.75 words** (English text)

### The Problem

As conversations grow, you accumulate messages:

```python
messages = [
    {"role": "user", "content": "What is Python?"},           # ~5 tokens
    {"role": "assistant", "content": "Python is..."},        # ~200 tokens
    {"role": "user", "content": "How do I install it?"},     # ~7 tokens
    {"role": "assistant", "content": "You can install..."}, # ~300 tokens
    # ... 50 more exchanges ...
]
```

After a long conversation:
- **Total tokens**: Could exceed context window
- **API cost**: Scales with total tokens sent
- **Performance**: Larger contexts = slower responses

**You need a memory management strategy.**

## Memory Management Strategies

### Strategy 1: Sliding Window (Recency-Based)

Keep only the **N most recent messages**.

```python
MAX_MESSAGES = 10

def add_message(messages, role, content):
    messages.append({"role": role, "content": content})

    # Keep only last MAX_MESSAGES
    if len(messages) > MAX_MESSAGES:
        messages = messages[-MAX_MESSAGES:]

    return messages
```

**Pros:**
- ✅ Simple to implement
- ✅ Bounded memory usage
- ✅ Always includes recent context

**Cons:**
- ❌ Loses old but important information
- ❌ No prioritization (treats all messages equally)

**Best for:** Short-term conversations, chatbots with discrete sessions

### Strategy 2: Summarization

Periodically **summarize** old messages to condense them.

```python
def summarize_conversation(messages):
    # When conversation gets long, summarize old messages
    if len(messages) > 20:
        # Take first 10 messages
        old_messages = messages[:10]

        # Ask LLM to summarize them
        summary_response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"Summarize this conversation:\n{old_messages}"
            }]
        )

        summary = summary_response.content[0].text

        # Replace old messages with summary
        messages = [
            {"role": "assistant", "content": f"Summary of earlier conversation: {summary}"}
        ] + messages[10:]

    return messages
```

**Pros:**
- ✅ Retains key information from old messages
- ✅ Reduces token count significantly
- ✅ Maintains long-term context

**Cons:**
- ❌ Extra API calls (for summarization)
- ❌ Potential information loss
- ❌ More complex to implement

**Best for:** Long-running conversations, customer support, personal assistants

### Strategy 3: Semantic Search (RAG Pattern)

Store old messages in a **vector database** and retrieve relevant ones based on semantic similarity.

```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

# Store embeddings of all messages
message_store = []

def add_to_memory(message_text):
    embedding = model.encode(message_text)
    message_store.append({
        "text": message_text,
        "embedding": embedding
    })

def retrieve_relevant_messages(query, top_k=5):
    query_embedding = model.encode(query)

    # Calculate similarity scores
    similarities = []
    for msg in message_store:
        similarity = np.dot(query_embedding, msg["embedding"])
        similarities.append((similarity, msg["text"]))

    # Get top K most similar
    similarities.sort(reverse=True, key=lambda x: x[0])
    return [msg for score, msg in similarities[:top_k]]

# When user asks new question
user_query = "How do I deploy to production?"
relevant_context = retrieve_relevant_messages(user_query)

# Include only relevant past messages
messages = [
    {"role": "assistant", "content": f"Relevant context: {relevant_context}"},
    {"role": "user", "content": user_query}
]
```

**Pros:**
- ✅ Only includes relevant context
- ✅ Efficient token usage
- ✅ Scales to very long conversations

**Cons:**
- ❌ Requires vector database setup
- ❌ More complex implementation
- ❌ May miss important non-similar context

**Best for:** Knowledge bases, technical support, research assistants

### Strategy 4: Hierarchical Memory

Combine multiple strategies with different time horizons:

```python
class HierarchicalMemory:
    def __init__(self):
        self.short_term = []      # Last 10 messages (full detail)
        self.medium_term = []     # Last 50 messages (summarized)
        self.long_term = []       # All messages (semantic search)

    def add_message(self, role, content):
        message = {"role": role, "content": content}

        # Add to short-term
        self.short_term.append(message)
        if len(self.short_term) > 10:
            # Move oldest to medium-term
            old_msg = self.short_term.pop(0)
            self.medium_term.append(old_msg)

        # Summarize medium-term when it gets large
        if len(self.medium_term) > 50:
            summary = self.summarize(self.medium_term[:25])
            self.long_term.append(summary)
            self.medium_term = self.medium_term[25:]

    def get_context_for_query(self, query):
        # Combine all memory tiers
        context = []

        # Always include short-term (recent)
        context.extend(self.short_term)

        # Include relevant long-term memories
        relevant = self.semantic_search(query, self.long_term)
        context.extend(relevant)

        return context
```

**Pros:**
- ✅ Best of all approaches
- ✅ Balances recency and relevance
- ✅ Scales to very long conversations

**Cons:**
- ❌ Most complex to implement
- ❌ Requires multiple subsystems

**Best for:** Advanced agents, personal AI assistants, long-term projects

## Token Counting

To manage memory effectively, you need to know how many tokens you're using:

```python
import tiktoken  # OpenAI's tokenizer

def count_tokens(messages, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)

    total_tokens = 0
    for message in messages:
        # Each message adds metadata tokens
        total_tokens += 4  # Role + formatting
        total_tokens += len(encoding.encode(message["content"]))

    return total_tokens

# Check before sending
messages = [...]
token_count = count_tokens(messages)

if token_count > MAX_CONTEXT_WINDOW:
    # Apply memory management strategy
    messages = sliding_window(messages)
```

**Note:** Different models use different tokenizers. Always use the correct one for your model.

## System Prompts and Memory

The **system prompt** is special - it's included in every request and doesn't change (usually). This consumes tokens on every call.

**Optimization:**
- Keep system prompts concise
- Don't repeat information that's in the conversation history
- Consider moving instructions to user messages when context is tight

```python
# ❌ Wasteful - repeats context
system_prompt = '''
You are a helpful assistant.
The user is working on a Python project.
They are using Django framework.
They are deploying to AWS.
Previous conversation summary: [...]
'''

# ✅ Efficient - minimal system, context in messages
system_prompt = "You are a helpful programming assistant."

messages = [
    {"role": "user", "content": "Context: Django project on AWS"},
    # ... rest of conversation
]
```

## Best Practices

### 1. **Monitor Token Usage**
Always track how many tokens you're sending:

```python
response = client.messages.create(...)
print(f"Tokens used: {response.usage.input_tokens + response.usage.output_tokens}")
```

### 2. **Choose Strategy Based on Use Case**
- **Short conversations** → Sliding window
- **Long conversations** → Summarization
- **Knowledge-heavy** → Semantic search (RAG)
- **Complex agents** → Hierarchical

### 3. **Test Context Limits**
Don't assume the context window is accurate. Test with your actual data:

```python
# Test edge cases
very_long_conversation = [...]  # 100+ messages
try:
    response = client.messages.create(messages=very_long_conversation)
except Exception as e:
    print("Hit context limit:", e)
```

### 4. **Preserve Critical Information**
Always keep:
- System instructions
- Critical user preferences
- Current task context
- Recent messages (last 5-10)

### 5. **Consider Cost**
Token usage = cost. Optimize for both performance and budget:

```python
# Calculate cost
INPUT_COST_PER_1M_TOKENS = 3.00   # Example pricing
OUTPUT_COST_PER_1M_TOKENS = 15.00

total_cost = (
    (input_tokens / 1_000_000) * INPUT_COST_PER_1M_TOKENS +
    (output_tokens / 1_000_000) * OUTPUT_COST_PER_1M_TOKENS
)
```

## Key Takeaways

✅ **LLMs are stateless** - you manage memory, not the LLM

✅ **Context windows have limits** - plan for long conversations

✅ **Multiple strategies exist** - choose based on use case

✅ **Token counting is essential** - monitor usage constantly

✅ **Memory management is a trade-off** - balance cost, performance, accuracy

✅ **System prompts consume tokens** - keep them concise

## Congratulations!

You've completed the fundamentals of AI agent architecture:
- ✅ Module 00: LLM API Communication
- ✅ Module 01: Pydantic Pattern & Tool Use
- ✅ Module 02: Conversational Memory

You now understand how modern AI agents work under the hood!

---

*"The fear of the LORD is the beginning of knowledge" - Proverbs 1:7 (KJV)*
"""

lesson_02_quiz = {
    "questions": [
        {
            "text": "Why do LLMs need conversation history sent with each request?",
            "options": [
                "To improve response quality",
                "Because LLMs are stateless and don't remember previous interactions",
                "To train the model",
                "For security purposes"
            ],
            "correct": 2
        },
        {
            "text": "What is a 'context window'?",
            "options": [
                "The time between API requests",
                "The maximum amount of text an LLM can process in a single request",
                "A browser feature for displaying chat",
                "The UI element showing conversation"
            ],
            "correct": 2
        },
        {
            "text": "Which memory strategy keeps only the N most recent messages?",
            "options": [
                "Summarization",
                "Semantic search",
                "Sliding window",
                "Hierarchical memory"
            ],
            "correct": 3
        },
        {
            "text": "What is the main advantage of using semantic search (RAG) for memory?",
            "options": [
                "It's the simplest to implement",
                "It only includes contextually relevant past messages",
                "It requires no API calls",
                "It works without embeddings"
            ],
            "correct": 2
        },
        {
            "text": "What should you always monitor to manage conversational memory effectively?",
            "options": [
                "User satisfaction scores",
                "Token usage and context window limits",
                "Network latency",
                "GPU temperature"
            ],
            "correct": 2
        }
    ]
}

lesson_02 = Lesson.objects.create(
    lesson_id="module-02",
    title="Conversational Memory",
    subtitle="Master context management and memory strategies for AI agents",
    content=lesson_02_content,
    module_number=2,
    order_index=2,
    quiz_data=lesson_02_quiz
)

print(f"✓ Created: {lesson_02}")

print("\n" + "="*50)
print("✓ Successfully seeded 3 lessons!")
print("="*50)
print(f"\nLessons created:")
print(f"  1. {lesson_00.lesson_id}: {lesson_00.title}")
print(f"  2. {lesson_01.lesson_id}: {lesson_01.title}")
print(f"  3. {lesson_02.lesson_id}: {lesson_02.title}")
print("\nYou can now:")
print("  - View lessons via API: GET /api/lessons/")
print("  - Test quizzes with the quiz_data")
print("  - Build the CLI frontend to display this content")
