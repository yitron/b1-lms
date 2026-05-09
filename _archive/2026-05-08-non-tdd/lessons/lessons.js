/**
 * LMS Lessons Data
 * Extracted from /learning/ curriculum (Modules 00-02)
 *
 * Content Source: 42 School-style agent programming curriculum
 * - Module 00: /learning/module-00/subject.md
 * - Module 01: /learning/module-01/subject.md
 * - Module 02: /learning/module-02/subject.md
 */

const lessons = [
    {
        id: 'lesson-00',
        moduleNumber: '00',
        title: 'Hello World: Your First LLM Call',
        subtitle: 'Learn the fundamentals of talking to an LLM',
        duration: '2-3 hours',
        difficulty: '⭐☆☆☆☆',
        objectives: [
            'Understand what an LLM API is and how to call it',
            'Make your first API request to an LLM provider',
            'Handle JSON responses from the API',
            'Display formatted output to the user',
            'Learn basic error handling for API calls'
        ],
        content: `
            <h2>Introduction</h2>
            <p>Welcome to your first step in building AI agents! In this module, you'll learn the most fundamental skill: talking to a Large Language Model (LLM).</p>

            <p>An <strong>agent</strong> is a program that uses an LLM to:</p>
            <ol>
                <li>Understand what a user wants</li>
                <li>Think about how to help</li>
                <li>Take actions or respond with helpful information</li>
            </ol>

            <p>Before we can build agents, we need to learn how to communicate with LLMs. Think of it like learning to use a phone before you can have a conversation.</p>

            <h3>What You'll Build</h3>
            <p>A simple Python program that:</p>
            <ul>
                <li>Takes user input</li>
                <li>Sends it to an LLM API</li>
                <li>Displays the LLM's response</li>
            </ul>

            <p>It's that simple! But this is the foundation of everything.</p>

            <div class="info-box">
                <h4>📚 Key Concept: LLM API</h4>
                <p>An <strong>API (Application Programming Interface)</strong> is how your code talks to an LLM service like OpenAI, Anthropic, or OpenRouter. You send a request (with your question), and the API sends back a response (with the LLM's answer).</p>
            </div>

            <h3>API Request Format</h3>
            <p>Your API request should follow this structure (example for OpenRouter):</p>

            <pre><code>import requests
import json

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
data = {
    "model": "meta-llama/llama-3.1-8b-instruct:free",
    "messages": [
        {"role": "user", "content": "Your user's question here"}
    ],
    "temperature": 0.7
}

response = requests.post(url, headers=headers, json=data)</code></pre>

            <p>The response will be JSON like this:</p>
            <pre><code>{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "The capital of France is Paris."
      }
    }
  ]
}</code></pre>

            <h3>Expected Program Behavior</h3>
            <pre><code>$ python hello_llm.py "What is 2+2?"
[LLM Response]
2 + 2 equals 4.

$ python hello_llm.py
Error: Please provide a question as an argument
Usage: python hello_llm.py "your question here"

$ API_KEY="" python hello_llm.py "test"
Error: API key not found. Set the API_KEY environment variable.</code></pre>

            <h3>Error Handling</h3>
            <p>Good error handling is essential for production code. Your program should gracefully handle:</p>
            <ul>
                <li><strong>Missing API key</strong> → Show clear error message</li>
                <li><strong>Network errors</strong> → Indicate connection issues</li>
                <li><strong>API errors</strong> → Display API error message</li>
                <li><strong>Invalid input</strong> → Guide user to correct usage</li>
            </ul>

            <div class="tip-box">
                <h4>💡 Pro Tip</h4>
                <p>Never hardcode API keys in your code! Use environment variables:</p>
                <pre><code>import os
api_key = os.getenv("API_KEY")</code></pre>
            </div>

            <h3>Next Steps</h3>
            <p>Once you've mastered this module, you'll move on to <strong>Module 01: Your First Tool</strong>, where you'll learn how to give your agent superpowers! 🛠️</p>
        `,
        diagram: {
            type: 'flow',
            title: 'LLM API Request/Response Flow',
            description: 'Visual representation of how your code communicates with an LLM API',
            content: `
                <div class="diagram-flow">
                    <div class="flow-step">
                        <div class="flow-icon">👤</div>
                        <div class="flow-label">User</div>
                        <div class="flow-desc">"What is 2+2?"</div>
                    </div>
                    <div class="flow-arrow">→</div>
                    <div class="flow-step">
                        <div class="flow-icon">💻</div>
                        <div class="flow-label">Your Code</div>
                        <div class="flow-desc">Formats API request</div>
                    </div>
                    <div class="flow-arrow">→</div>
                    <div class="flow-step">
                        <div class="flow-icon">🌐</div>
                        <div class="flow-label">API Request</div>
                        <div class="flow-desc">POST /chat/completions</div>
                    </div>
                    <div class="flow-arrow">→</div>
                    <div class="flow-step">
                        <div class="flow-icon">🤖</div>
                        <div class="flow-label">LLM</div>
                        <div class="flow-desc">Processes request</div>
                    </div>
                    <div class="flow-arrow">→</div>
                    <div class="flow-step">
                        <div class="flow-icon">📦</div>
                        <div class="flow-label">API Response</div>
                        <div class="flow-desc">JSON with answer</div>
                    </div>
                    <div class="flow-arrow">→</div>
                    <div class="flow-step">
                        <div class="flow-icon">💻</div>
                        <div class="flow-label">Your Code</div>
                        <div class="flow-desc">Parses JSON</div>
                    </div>
                    <div class="flow-arrow">→</div>
                    <div class="flow-step">
                        <div class="flow-icon">👤</div>
                        <div class="flow-label">User</div>
                        <div class="flow-desc">"2 + 2 equals 4"</div>
                    </div>
                </div>
            `
        },
        quiz: {
            questions: [
                {
                    id: 'q1',
                    question: 'What is the primary purpose of an API when working with LLMs?',
                    options: [
                        'To store LLM responses in a database',
                        'To provide a structured way for your code to communicate with an LLM service',
                        'To train the LLM model',
                        'To generate API keys automatically'
                    ],
                    correct: 1,
                    explanation: 'An API (Application Programming Interface) provides a structured way for your code to send requests to and receive responses from an LLM service. It\'s the communication bridge between your application and the LLM.'
                },
                {
                    id: 'q2',
                    question: 'Which of the following is the correct format for sending a user message in an API request?',
                    options: [
                        '{"user": "What is AI?"}',
                        '{"role": "user", "content": "What is AI?"}',
                        '{"message": "What is AI?", "sender": "user"}',
                        '{"question": "What is AI?"}'
                    ],
                    correct: 1,
                    explanation: 'The standard format for chat API messages is {"role": "user", "content": "your message"}. The "role" field indicates who sent the message (user, assistant, or system), and "content" contains the actual message text.'
                },
                {
                    id: 'q3',
                    question: 'Why should you never hardcode API keys directly in your source code?',
                    options: [
                        'It makes the code run slower',
                        'It\'s a security risk if the code is shared or committed to version control',
                        'API keys don\'t work when hardcoded',
                        'It violates Python syntax rules'
                    ],
                    correct: 1,
                    explanation: 'Hardcoding API keys is a major security risk. If you commit your code to GitHub or share it, anyone can see and use your API key, potentially racking up charges on your account. Always use environment variables to store sensitive credentials.'
                },
                {
                    id: 'q4',
                    question: 'What type of data format do LLM APIs typically use for requests and responses?',
                    options: [
                        'XML',
                        'CSV',
                        'JSON',
                        'Plain text'
                    ],
                    correct: 2,
                    explanation: 'LLM APIs use JSON (JavaScript Object Notation) for both requests and responses. JSON is lightweight, human-readable, and widely supported across programming languages.'
                }
            ]
        }
    },
    {
        id: 'lesson-01',
        moduleNumber: '01',
        title: 'Your First Tool: Teaching the LLM to Take Action',
        subtitle: 'Define tools using Pydantic and complete the agent loop',
        duration: '4-6 hours',
        difficulty: '⭐⭐☆☆☆',
        objectives: [
            'Understand what a "tool" is in agent programming',
            'Define a tool using Pydantic models',
            'Generate JSON schemas that LLMs can understand',
            'Parse tool calls from LLM responses',
            'Execute tools and return results',
            'Complete a full agent loop: LLM → Tool → LLM'
        ],
        content: `
            <h2>Introduction</h2>
            <p>In Module 00, you learned to talk to an LLM. But the LLM could only respond with text. What if we want it to:</p>
            <ul>
                <li>Perform calculations</li>
                <li>Look up information in a database</li>
                <li>Send emails</li>
                <li>Control smart home devices</li>
            </ul>

            <p>This is where <strong>tools</strong> come in!</p>

            <h3>What is a Tool?</h3>
            <p>A tool is a function that:</p>
            <ol>
                <li>The LLM knows exists (via a schema)</li>
                <li>The LLM can decide to call</li>
                <li>Your code executes</li>
                <li>Returns results back to the LLM</li>
            </ol>

            <div class="comparison-box">
                <div class="comparison-item">
                    <h4>Without Tools</h4>
                    <p>LLM is a smart person in a room with no hands</p>
                </div>
                <div class="comparison-item">
                    <h4>With Tools</h4>
                    <p>LLM is a smart person who can ask you to do things</p>
                </div>
            </div>

            <h3>The Pydantic Pattern</h3>
            <p>Modern agent frameworks (Claude Code, LangChain, etc.) use <strong>Pydantic</strong> for tools because:</p>

            <pre><code>from pydantic import BaseModel, Field

class CalculatorInput(BaseModel):
    """Input for calculator tool"""
    operation: str = Field(description="Operation: add, subtract, multiply, divide")
    a: float = Field(description="First number")
    b: float = Field(description="Second number")</code></pre>

            <p>This Pydantic model automatically:</p>
            <ul>
                <li>✅ Validates inputs</li>
                <li>✅ Generates JSON schema for the LLM</li>
                <li>✅ Documents parameters</li>
                <li>✅ Provides type safety</li>
            </ul>

            <div class="info-box">
                <h4>🎯 Key Insight</h4>
                <p>This is the pattern you'll learn in this module. <strong>This is how Claude Code, LangChain, and all modern frameworks define tools.</strong></p>
            </div>

            <h3>Generating JSON Schema</h3>
            <p>You need to convert your Pydantic model to JSON schema:</p>

            <pre><code>tool_definition = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Perform basic arithmetic operations",
        "parameters": CalculatorInput.model_json_schema()
    }
}</code></pre>

            <p>This creates:</p>
            <pre><code>{
  "type": "function",
  "function": {
    "name": "calculator",
    "description": "Perform basic arithmetic operations",
    "parameters": {
      "type": "object",
      "properties": {
        "operation": {
          "type": "string",
          "description": "The operation to perform: 'add', 'subtract', 'multiply', or 'divide'"
        },
        "a": {
          "type": "number",
          "description": "The first number"
        },
        "b": {
          "type": "number",
          "description": "The second number"
        }
      },
      "required": ["operation", "a", "b"]
    }
  }
}</code></pre>

            <h3>Detecting Tool Calls</h3>
            <p>The LLM's response will look like this when it wants to use a tool:</p>

            <pre><code>{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": null,
      "tool_calls": [{
        "id": "call_123",
        "type": "function",
        "function": {
          "name": "calculator",
          "arguments": "{\\"operation\\": \\"add\\", \\"a\\": 25, \\"b\\": 17}"
        }
      }]
    }
  }]
}</code></pre>

            <h3>Why Pydantic?</h3>

            <div class="code-comparison">
                <div class="code-block">
                    <h4>Without Pydantic - Manual Validation</h4>
                    <pre><code>def calculator(operation, a, b):
    if not isinstance(operation, str):
        raise TypeError("operation must be string")
    if not isinstance(a, (int, float)):
        raise TypeError("a must be number")
    # ... etc</code></pre>
                </div>

                <div class="code-block">
                    <h4>With Pydantic - Automatic Validation</h4>
                    <pre><code>class CalculatorInput(BaseModel):
    operation: str
    a: float
    b: float

# Pydantic does all validation automatically!</code></pre>
                </div>
            </div>

            <div class="tip-box">
                <h4>💡 Pro Tip</h4>
                <p>When the LLM calls a tool, you must:</p>
                <ol>
                    <li>Parse the <code>arguments</code> JSON string</li>
                    <li>Validate with your Pydantic model</li>
                    <li>Execute your function</li>
                    <li>Send the result back to the LLM as a tool message</li>
                    <li>Get the final answer from the LLM</li>
                </ol>
            </div>

            <h3>Common Pitfalls</h3>
            <ol>
                <li><strong>Forgetting to send tools in API request:</strong> The tools array must be included, or the LLM won't know tools are available.</li>
                <li><strong>Not parsing arguments JSON:</strong> The arguments field is a string, not an object. You must parse it.</li>
                <li><strong>Not sending tool result back:</strong> The LLM needs the result to give a final answer to the user.</li>
            </ol>
        `,
        diagram: {
            type: 'flow',
            title: 'Agent Loop with Tools',
            description: 'Complete cycle from user question to final answer via tool execution',
            content: `
                <div class="diagram-agent-loop">
                    <div class="loop-step" data-step="1">
                        <div class="step-number">1</div>
                        <div class="step-icon">👤</div>
                        <div class="step-label">User asks question</div>
                        <div class="step-detail">"What is 25 + 17?"</div>
                    </div>
                    <div class="loop-arrow">↓</div>
                    <div class="loop-step" data-step="2">
                        <div class="step-number">2</div>
                        <div class="step-icon">📤</div>
                        <div class="step-label">Send to LLM with tools</div>
                        <div class="step-detail">Include calculator tool definition</div>
                    </div>
                    <div class="loop-arrow">↓</div>
                    <div class="loop-step" data-step="3">
                        <div class="step-number">3</div>
                        <div class="step-icon">🤖</div>
                        <div class="step-label">LLM decides to use tool</div>
                        <div class="step-detail">Returns tool_call: calculator(add, 25, 17)</div>
                    </div>
                    <div class="loop-arrow">↓</div>
                    <div class="loop-step" data-step="4">
                        <div class="step-number">4</div>
                        <div class="step-icon">⚙️</div>
                        <div class="step-label">Execute tool</div>
                        <div class="step-detail">calculator("add", 25, 17) → 42</div>
                    </div>
                    <div class="loop-arrow">↓</div>
                    <div class="loop-step" data-step="5">
                        <div class="step-number">5</div>
                        <div class="step-icon">📥</div>
                        <div class="step-label">Send result back to LLM</div>
                        <div class="step-detail">Tool message: "42"</div>
                    </div>
                    <div class="loop-arrow">↓</div>
                    <div class="loop-step" data-step="6">
                        <div class="step-number">6</div>
                        <div class="step-icon">🤖</div>
                        <div class="step-label">LLM formats answer</div>
                        <div class="step-detail">"The answer is 42."</div>
                    </div>
                    <div class="loop-arrow">↓</div>
                    <div class="loop-step" data-step="7">
                        <div class="step-number">7</div>
                        <div class="step-icon">👤</div>
                        <div class="step-label">Display to user</div>
                        <div class="step-detail">"The answer is 42."</div>
                    </div>
                </div>
            `
        },
        quiz: {
            questions: [
                {
                    id: 'q1',
                    question: 'What is the primary benefit of using Pydantic for tool definitions?',
                    options: [
                        'It makes API calls faster',
                        'It automatically validates inputs and generates JSON schemas',
                        'It reduces the cost of API usage',
                        'It allows tools to run without an LLM'
                    ],
                    correct: 1,
                    explanation: 'Pydantic provides automatic input validation and JSON schema generation. This means you define your tool structure once, and Pydantic handles validation and creates the schema that LLMs need to understand how to use your tool.'
                },
                {
                    id: 'q2',
                    question: 'In the agent loop, what happens after the LLM responds with a tool call?',
                    options: [
                        'The conversation ends',
                        'Your code executes the tool and sends the result back to the LLM',
                        'The LLM automatically executes the tool',
                        'The user must manually approve the tool execution'
                    ],
                    correct: 1,
                    explanation: 'After the LLM indicates it wants to use a tool (via tool_calls in the response), your code must: 1) Execute the tool with the provided parameters, 2) Send the result back to the LLM as a tool message, 3) Let the LLM format a final answer for the user.'
                },
                {
                    id: 'q3',
                    question: 'Which of the following is NOT automatically handled by Pydantic?',
                    options: [
                        'Type validation (ensuring a is a float)',
                        'JSON schema generation',
                        'Parameter documentation',
                        'Executing the actual tool function'
                    ],
                    correct: 3,
                    explanation: 'Pydantic handles validation, schema generation, and documentation, but it doesn\'t execute your tool function. You still need to write the actual business logic (like performing the calculation). Pydantic just ensures the inputs are valid before your function runs.'
                },
                {
                    id: 'q4',
                    question: 'What format is the "arguments" field in a tool_call response?',
                    options: [
                        'A Python dictionary',
                        'A JSON string that needs to be parsed',
                        'A Pydantic model instance',
                        'An array of values'
                    ],
                    correct: 1,
                    explanation: 'The "arguments" field in a tool_call is a JSON string, not an already-parsed object. You must use json.loads() to parse it into a dictionary before you can validate it with Pydantic or use it in your tool function.'
                }
            ]
        }
    },
    {
        id: 'lesson-02',
        moduleNumber: '02',
        title: 'Conversational Memory: Multi-Turn Agents',
        subtitle: 'Build stateful agents that remember context across turns',
        duration: '3-4 hours',
        difficulty: '⭐⭐☆☆☆',
        objectives: [
            'Understand message history and context',
            'Implement multi-turn conversations',
            'Manage token limits',
            'Build a stateful agent'
        ],
        content: `
            <h2>Introduction</h2>
            <p>So far, your agents have been "stateless" - they forget everything after each question. Real agents need <strong>memory</strong> to have conversations.</p>

            <p>In this module, you'll learn to:</p>
            <ul>
                <li>Maintain message history across turns</li>
                <li>Keep context for the LLM</li>
                <li>Handle tools across multiple turns</li>
                <li>Manage growing conversation length</li>
            </ul>

            <div class="info-box">
                <h4>🎯 Key Concept: Stateful vs Stateless</h4>
                <p><strong>Stateless</strong> (Module 00): Each request is independent. The agent has no memory.</p>
                <p><strong>Stateful</strong> (this module): The agent maintains context across requests. It remembers what was said earlier.</p>
            </div>

            <h3>Message History</h3>
            <p>Every message must be preserved in order:</p>
            <ol>
                <li>User input</li>
                <li>Assistant response (possibly with tool calls)</li>
                <li>Tool results</li>
                <li>Assistant final response</li>
                <li>Next user input...</li>
            </ol>

            <p>Example conversation history:</p>
            <pre><code>messages = [
    {"role": "user", "content": "What is 10 + 5?"},
    {"role": "assistant", "content": None, "tool_calls": [...]},
    {"role": "tool", "content": "15", "tool_call_id": "..."},
    {"role": "assistant", "content": "The answer is 15."},
    {"role": "user", "content": "Multiply that by 2"},  # New turn - references "that"
    # ... agent can understand "that" refers to 15
]</code></pre>

            <div class="info-box">
                <h4>💡 Why History Matters</h4>
                <p>Without history, when the user says "Multiply that by 2", the LLM has no idea what "that" refers to. With history, it knows the previous answer was 15, so it can calculate 15 × 2 = 30.</p>
            </div>

            <h3>Building a Conversational Agent</h3>
            <p>Your conversational agent should:</p>

            <pre><code>You: What is 10 + 5?
Agent: The answer is 15.

You: Multiply that by 2
Agent: 15 multiplied by 2 is 30.

You: And add 10 more
Agent: 30 plus 10 equals 40.

You: exit</code></pre>

            <h3>Context Window Management</h3>
            <p>Models have token limits (usually 4k-128k tokens). Each turn adds tokens. Eventually, you'll hit the limit.</p>

            <div class="warning-box">
                <h4>⚠️ The Problem</h4>
                <p>As conversations grow, token count increases. At some point, you'll exceed the model's context window and get errors.</p>
            </div>

            <p>Solutions:</p>
            <ol>
                <li><strong>Track token usage:</strong> Monitor cumulative tokens and warn when approaching limits</li>
                <li><strong>Trim old messages:</strong> Keep system message + last N messages only</li>
                <li><strong>Summarize history:</strong> Compress old turns into a summary (advanced)</li>
            </ol>

            <h3>Token Tracking</h3>
            <p>Most API responses include token usage:</p>
            <pre><code>{
  "usage": {
    "prompt_tokens": 120,
    "completion_tokens": 45,
    "total_tokens": 165
  }
}</code></pre>

            <p>Your agent should:</p>
            <ul>
                <li>Track cumulative tokens across all turns</li>
                <li>Display token usage per turn</li>
                <li>Warn when approaching the model's limit</li>
            </ul>

            <h3>Interactive Loop (REPL)</h3>
            <p>A conversational agent typically runs in an interactive loop:</p>

            <pre><code>messages = []  # Initialize empty history

while True:
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit"]:
        break

    # Add user message to history
    messages.append({"role": "user", "content": user_input})

    # Send full history to LLM
    response = call_llm(messages)

    # Handle tool calls if present
    # ...

    # Add assistant response to history
    messages.append({"role": "assistant", "content": response_text})

    print(f"Agent: {response_text}")</code></pre>

            <div class="tip-box">
                <h4>💡 Pro Tip</h4>
                <p>Always send the <strong>full message history</strong> on each turn. The LLM has no memory between API calls - the only way it knows context is if you send it in the messages array.</p>
            </div>

            <h3>Session Persistence (Bonus)</h3>
            <p>For bonus points, you can save conversations to disk:</p>
            <ul>
                <li>Save as JSON: <code>my_session.json</code></li>
                <li>Load previous conversations: <code>--load my_session.json</code></li>
                <li>Resume where you left off</li>
            </ul>

            <h3>Best Practices</h3>
            <ol>
                <li><strong>Always track tokens:</strong> Know how close you are to limits</li>
                <li><strong>Validate message structure:</strong> Ensure correct role ordering</li>
                <li><strong>Handle interruptions:</strong> Save state on Ctrl+C</li>
                <li><strong>Clear history option:</strong> Let users start fresh mid-conversation</li>
            </ol>
        `,
        diagram: {
            type: 'structure',
            title: 'Message History Structure',
            description: 'How messages accumulate over multiple turns in a conversation',
            content: `
                <div class="diagram-message-history">
                    <div class="message-turn" data-turn="1">
                        <div class="turn-label">Turn 1</div>
                        <div class="message user-message">
                            <div class="message-role">user</div>
                            <div class="message-content">"What is 10 + 5?"</div>
                        </div>
                        <div class="message assistant-message">
                            <div class="message-role">assistant</div>
                            <div class="message-content">tool_calls: [calculator(add, 10, 5)]</div>
                        </div>
                        <div class="message tool-message">
                            <div class="message-role">tool</div>
                            <div class="message-content">Result: 15</div>
                        </div>
                        <div class="message assistant-message">
                            <div class="message-role">assistant</div>
                            <div class="message-content">"The answer is 15."</div>
                        </div>
                    </div>

                    <div class="history-arrow">⬇️ History grows...</div>

                    <div class="message-turn" data-turn="2">
                        <div class="turn-label">Turn 2 (includes Turn 1)</div>
                        <div class="previous-indicator">[ Previous 4 messages ]</div>
                        <div class="message user-message">
                            <div class="message-role">user</div>
                            <div class="message-content">"Multiply that by 2"</div>
                            <div class="context-note">↑ "that" refers to 15 from history</div>
                        </div>
                        <div class="message assistant-message">
                            <div class="message-role">assistant</div>
                            <div class="message-content">tool_calls: [calculator(multiply, 15, 2)]</div>
                        </div>
                        <div class="message tool-message">
                            <div class="message-role">tool</div>
                            <div class="message-content">Result: 30</div>
                        </div>
                        <div class="message assistant-message">
                            <div class="message-role">assistant</div>
                            <div class="message-content">"15 multiplied by 2 is 30."</div>
                        </div>
                    </div>

                    <div class="history-arrow">⬇️ History continues...</div>

                    <div class="message-turn" data-turn="3">
                        <div class="turn-label">Turn 3 (includes Turns 1 & 2)</div>
                        <div class="previous-indicator">[ Previous 8 messages ]</div>
                        <div class="message user-message">
                            <div class="message-role">user</div>
                            <div class="message-content">"And add 10 more"</div>
                            <div class="context-note">↑ Context knows "30" from previous</div>
                        </div>
                        <div class="dots-indicator">...</div>
                    </div>

                    <div class="token-warning">
                        <div class="warning-icon">⚠️</div>
                        <div class="warning-text">
                            Each turn adds tokens. Monitor usage to stay under model limits!
                        </div>
                    </div>
                </div>
            `
        },
        quiz: {
            questions: [
                {
                    id: 'q1',
                    question: 'Why do stateful agents need to send the full message history with each API request?',
                    options: [
                        'To make the API calls more expensive',
                        'Because LLMs have no memory between API calls',
                        'To test the API\'s ability to handle large requests',
                        'It\'s not necessary; the API remembers previous calls'
                    ],
                    correct: 1,
                    explanation: 'LLMs are stateless between API calls - they don\'t remember anything from previous requests. The only way an LLM knows about earlier parts of the conversation is if you include the full message history in each request.'
                },
                {
                    id: 'q2',
                    question: 'What is the primary challenge of maintaining long conversations?',
                    options: [
                        'Users get bored',
                        'Token limits - models have maximum context window sizes',
                        'It takes too much disk space',
                        'The LLM\'s responses become less accurate'
                    ],
                    correct: 1,
                    explanation: 'Models have token limits (context windows) ranging from 4k to 128k tokens. As conversations grow, you accumulate more tokens. Eventually, you\'ll exceed the limit and get errors. You must manage this by tracking token usage and potentially trimming old messages.'
                },
                {
                    id: 'q3',
                    question: 'In a conversational agent, what should happen when a user says "Multiply that by 2"?',
                    options: [
                        'Return an error because "that" is not defined',
                        'Ask the user to clarify what "that" refers to',
                        'Use message history to understand "that" refers to the previous answer',
                        'Assume "that" means the number 1'
                    ],
                    correct: 2,
                    explanation: 'With message history, the LLM can use context to resolve pronouns like "that." It looks back through the conversation history to understand what the user is referring to. This is why maintaining proper message history is crucial for natural conversations.'
                }
            ]
        }
    }
];

// Glossary terms
const glossary = [
    {
        term: 'Agent',
        definition: 'A program that uses an LLM to understand user requests, think about solutions, and take actions or respond with helpful information.'
    },
    {
        term: 'API (Application Programming Interface)',
        definition: 'A structured way for your code to communicate with external services like LLM providers. You send requests with questions and receive responses with answers.'
    },
    {
        term: 'LLM (Large Language Model)',
        definition: 'An AI model trained on vast amounts of text data, capable of understanding and generating human-like text. Examples: GPT-4, Claude, Llama.'
    },
    {
        term: 'Tool',
        definition: 'A function that an LLM can invoke to perform actions beyond text generation, such as calculations, database lookups, API calls, or file operations.'
    },
    {
        term: 'Pydantic',
        definition: 'A Python library for data validation and settings management. Used in agent programming to define tool interfaces, validate inputs, and generate JSON schemas.'
    },
    {
        term: 'JSON Schema',
        definition: 'A vocabulary that allows you to annotate and validate JSON documents. LLMs use schemas to understand what parameters a tool accepts and what types they should be.'
    },
    {
        term: 'Agent Loop',
        definition: 'The cycle of: User → LLM → Tool Call → Execute Tool → Return Result → LLM → Final Response → User'
    },
    {
        term: 'Message History',
        definition: 'The complete record of all messages in a conversation: user inputs, assistant responses, tool calls, and tool results. Required for maintaining context.'
    },
    {
        term: 'Context Window',
        definition: 'The maximum number of tokens (words/pieces of words) that an LLM can process in a single request. Typical ranges: 4k-128k tokens.'
    },
    {
        term: 'Token',
        definition: 'A piece of text that an LLM processes. Roughly 1 token = 0.75 words in English. Both input and output consume tokens.'
    },
    {
        term: 'Stateless',
        definition: 'An agent that has no memory between requests. Each question is treated independently without context from previous turns.'
    },
    {
        term: 'Stateful',
        definition: 'An agent that maintains conversation history across multiple turns, allowing it to understand context and references to earlier parts of the conversation.'
    },
    {
        term: 'Tool Call',
        definition: 'When an LLM decides to use a tool instead of responding with text. The response includes the tool name and parameters to pass to it.'
    },
    {
        term: 'REPL (Read-Eval-Print Loop)',
        definition: 'An interactive programming environment that reads user input, evaluates it, prints the result, and loops. Used for conversational agents.'
    }
];

// Export for use in script.js
if (typeof window !== 'undefined') {
    window.lessonsData = lessons;
    window.glossaryData = glossary;
}
