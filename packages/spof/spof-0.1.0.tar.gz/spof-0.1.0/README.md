# SPOF - Structured Prompt Output Framework

**SPOF (Structured Prompt Output Framework)** is an open-source Python framework for designing **structured, maintainable, and type-safe prompts** for Large Language Models (LLMs).

Think of it as **“Pydantic for prompts”** — SPOF lets you model prompts as composable data structures, enforce schema validation, and render them into multiple formats (JSON, XML, Markdown, plain text) without losing intent.

With SPOF, prompts become:

* **Composable** – Build reusable prompt blocks (e.g., personality, safety rules, context) and combine them like Lego pieces.
* **Type-safe** – Leverage Python’s typing and Pydantic validation to guarantee correct structures before sending to an LLM.
* **Multi-format** – Export the same structured prompt to any output format required by different providers or APIs.
* **Maintainable** – Treat prompts as code, versioned and auditable, instead of fragile strings.

SPOF provides the missing **infrastructure layer for prompt engineering at scale**, turning prompts into reliable, testable, and reusable components.


## 🚀 Quick Start

### Installation

```bash
pip install spof
```

### Basic Example

```python
from spof import InstructionBlock, Text, Items

class SimplePrompt(InstructionBlock):
    instruction: Text
    requirements: Items
    
    def __init__(self):
        super().__init__(
            instruction=Text("Analyze the following data carefully"),
            requirements=Items([
                "Be thorough and accurate",
                "Include specific examples", 
                "Provide clear conclusions"
            ])
        )

# Create and render
prompt = SimplePrompt()
print(prompt.to_xml())
```

**Output:**
```xml
<simple_prompt>
  <instruction>Analyze the following data carefully</instruction>
  <requirements>
    - Be thorough and accurate
    - Include specific examples  
    - Provide clear conclusions
  </requirements>
</simple_prompt>
```

## 📋 Core Components

### 1. InstructionBlock
The base class for all prompt components. Inherit from this to create custom blocks.

```python
class MyBlock(InstructionBlock):
    title: str
    content: str
    
    def __init__(self, title: str, content: str):
        super().__init__(title=title, content=content)
```

### 2. Text Block
For simple text content with optional custom block names.

```python
# Simple text
intro = Text("Welcome to our AI assistant")

# With custom block name
intro = Text("Welcome to our AI assistant", block_name="greeting")
```

### 3. Items Block
For lists of items, rendered as bullet points.

```python
rules = Items([
    "Be respectful and helpful",
    "Provide accurate information",
    "Ask for clarification when needed"
], block_name="guidelines")
```

### 4. ModelBlock & wrap_model()
Automatically wrap any Pydantic model to make it renderable.

```python
from pydantic import BaseModel

class UserProfile(BaseModel):
    name: str
    age: int
    role: str

user = UserProfile(name="Alice", age=30, role="Engineer")

# Wrap for rendering
user_block = wrap_model(user, block_name="user_info")
print(user_block.to_xml())
```

**Output:**
```xml
<user_info>
  <name>Alice</name>
  <age>30</age>
  <role>Engineer</role>
</user_info>
```

## 🎨 Rendering Formats

SPOF can render the same prompt structure in three formats:

### XML Format (Default)
Perfect for Claude and other models that work well with structured XML:

```python
prompt.to_xml()
# or
prompt.render(RenderFormat.XML)
```

### Markdown Format
Great for models that prefer markdown structure:

```python
prompt.to_markdown()
# or  
prompt.render(RenderFormat.MARKDOWN)
```

### JSON Format
Useful for API calls and structured data exchange:

```python
prompt.to_json()
# or
prompt.render(RenderFormat.JSON)  
```

## 🏗️ Building Complex Prompts

### Nested Structures
SPOF handles nested blocks automatically:

```python
class AnalysisPrompt(InstructionBlock):
    role: Text
    context: UserContext  # Another InstructionBlock
    instructions: InstructionSet  # Another InstructionBlock
    examples: List[ExampleCase]  # List of Pydantic models
    
    def __init__(self, user_data, examples):
        super().__init__(
            role=Text("You are a data analyst"),
            context=UserContext(user_data),
            instructions=InstructionSet(),
            examples=[wrap_model(ex) for ex in examples]
        )
```

### Working with Pydantic Models
SPOF seamlessly integrates with existing Pydantic models:

```python
from pydantic import BaseModel
from typing import List, Literal

class Message(BaseModel):
    sender: Literal["User", "Assistant"] 
    timestamp: datetime
    content: str

class ConversationContext(InstructionBlock):
    messages: List[Message]
    user_id: str
    
    def __init__(self, messages: List[Message], user_id: str):
        super().__init__(messages=messages, user_id=user_id)

# Messages are automatically wrapped in ModelBlocks when rendered
```

### Custom Block Names
Control how your blocks appear in the output:

```python
# Class-level naming
class UserInstructions(InstructionBlock):
    __block_name__ = "custom_instructions"
    
# Instance-level naming  
intro = Text("Hello", block_name="greeting")
rules = Items(["Rule 1", "Rule 2"], block_name="policies")
```

## 📱 Complete Example: Chatbot Prompt

Here's a full example showing how to build a structured chatbot prompt:

```python
from typing import List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel
from spof import InstructionBlock, Text, Items

class ChatMessage(BaseModel):
    """Individual chat message with sender, timestamp, and content"""
    sender: Literal["User", "Assistant"]
    timestamp: datetime
    content: str

class PersonalityBlock(InstructionBlock):
    """Define the chatbot's personality and behavior"""
    name: str
    traits: List[str]
    communication_style: str

    def __init__(self):
        super().__init__(
            name="Alex",
            traits=[
                "Friendly and approachable",
                "Helpful and proactive", 
                "Curious and engaging",
                "Professional but warm"
            ],
            communication_style="Conversational, clear, and empathetic. Use 'I' naturally when speaking."
        )

class DirectionsBlock(InstructionBlock):
    """Clear instructions for the chatbot"""
    primary_goals: Items
    response_guidelines: Items
    safety_rules: Items

    def __init__(self):
        super().__init__(
            primary_goals=Items([
                "Listen carefully to understand user needs",
                "Provide helpful, accurate information", 
                "Ask clarifying questions when needed",
                "Maintain a friendly, professional tone"
            ], block_name="goals"),
            
            response_guidelines=Items([
                "Keep responses concise but thorough",
                "Use examples when helpful",
                "Acknowledge when you don't know something", 
                "Offer follow-up suggestions"
            ], block_name="guidelines"),
            
            safety_rules=Items([
                "Never provide harmful or dangerous advice",
                "Protect user privacy and data",
                "Be respectful of all individuals and groups",
                "Decline inappropriate requests politely"
            ], block_name="safety")
        )

class ConversationHistoryBlock(InstructionBlock):
    """Recent conversation messages for context"""
    messages: List[ChatMessage]
    total_messages: int

    def __init__(self, messages: List[ChatMessage]):
        super().__init__(
            messages=messages[-10:],  # Keep last 10 messages
            total_messages=len(messages)
        )

class ChatbotPrompt(InstructionBlock):
    """Complete chatbot prompt structure"""
    introduction: Text
    personality: PersonalityBlock
    directions: DirectionsBlock
    conversation_history: Optional[ConversationHistoryBlock]
    current_context: Text
    final_instruction: Text

    def __init__(self, user_message: str, conversation_history: Optional[List[ChatMessage]] = None):
        super().__init__(
            introduction=Text(
                "You are Alex, a helpful AI assistant. Respond naturally and helpfully to user messages.",
                block_name="role"
            ),
            
            personality=PersonalityBlock(),
            directions=DirectionsBlock(), 
            
            conversation_history=(
                ConversationHistoryBlock(conversation_history) 
                if conversation_history else None
            ),
            
            current_context=Text(f"User's current message: {user_message}", block_name="current_request"),
            
            final_instruction=Text(
                "Based on the user's message and conversation context, provide a helpful, "
                "friendly response that follows your personality and guidelines.",
                block_name="task"
            )
        )

# Usage
user_input = "Hi! Can you help me plan a weekend trip to Paris?"

chat_history = [
    ChatMessage(
        sender="User",
        timestamp=datetime(2025, 9, 6, 14, 30, 0),
        content="Hello there!"
    ),
    ChatMessage(
        sender="Assistant", 
        timestamp=datetime(2025, 9, 6, 14, 30, 5),
        content="Hi! I'm Alex, your helpful assistant. How can I help you today?"
    ),
    ChatMessage(
        sender="User",
        timestamp=datetime(2025, 9, 6, 14, 31, 0), 
        content="I'm looking for travel advice"
    ),
    ChatMessage(
        sender="Assistant",
        timestamp=datetime(2025, 9, 6, 14, 31, 3),
        content="I'd love to help with travel planning! What destination are you considering?"
    )
]

prompt = ChatbotPrompt(user_input, chat_history)
```

### Output (XML Format):

```xml
<chatbot_prompt>
  <introduction>You are Alex, a helpful AI assistant. Respond naturally and helpfully to user messages.</introduction>
  <personality_block>
    <name>Alex</name>
    <traits>
      - Friendly and approachable
      - Helpful and proactive
      - Curious and engaging
      - Professional but warm
    </traits>
    <communication_style>Conversational, clear, and empathetic. Use 'I' naturally when speaking.</communication_style>
  </personality_block>
  <directions_block>
    <goals>
      - Listen carefully to understand user needs
      - Provide helpful, accurate information
      - Ask clarifying questions when needed
      - Maintain a friendly, professional tone
    </goals>
    <guidelines>
      - Keep responses concise but thorough
      - Use examples when helpful
      - Acknowledge when you don't know something
      - Offer follow-up suggestions
    </guidelines>
    <safety>
      - Never provide harmful or dangerous advice
      - Protect user privacy and data
      - Be respectful of all individuals and groups
      - Decline inappropriate requests politely
    </safety>
  </directions_block>
  <conversation_history_block>
    <messages>
      <chat_message>
        <sender>User</sender>
        <timestamp>2025-09-06 14:30:00</timestamp>
        <content>Hello there!</content>
      </chat_message>
      <chat_message>
        <sender>Assistant</sender>
        <timestamp>2025-09-06 14:30:05</timestamp>
        <content>Hi! I'm Alex, your helpful assistant. How can I help you today?</content>
      </chat_message>
      <chat_message>
        <sender>User</sender>
        <timestamp>2025-09-06 14:31:00</timestamp>
        <content>I'm looking for travel advice</content>
      </chat_message>
      <chat_message>
        <sender>Assistant</sender>
        <timestamp>datetime(2025, 9, 6, 14, 31, 3)</timestamp>
        <content>I'd love to help with travel planning! What destination are you considering?</content>
      </chat_message>
    </messages>
    <total_messages>4</total_messages>
  </conversation_history_block>
  <current_request>User's current message: Hi! Can you help me plan a weekend trip to Paris?</current_request>
  <task>Based on the user's message and conversation context, provide a helpful, friendly response that follows your personality and guidelines.</task>
</chatbot_prompt>
```

## 🛠️ Advanced Features

### Field Exclusion
Exclude certain fields from rendering:

```python
user_block = wrap_model(user_model, exclude_fields=["password", "internal_id"])
```

### Custom Rendering Logic
Override rendering for specific block types:

```python
class CustomBlock(InstructionBlock):
    def render(self, format: RenderFormat = None, indent_level: int = 0) -> str:
        # Custom rendering logic
        if format == RenderFormat.XML:
            return "<custom>My custom XML</custom>"
        return super().render(format, indent_level)
```

### Runtime Block Names
Change block names at runtime:

```python
dynamic_block = Text("Content", block_name=f"section_{section_id}")
```

## 🔧 Best Practices

1. **Separate Structure from Content**: Define your prompt structure once, reuse everywhere
2. **Use Type Hints**: Leverage Pydantic's validation and IDE support  
3. **Compose Prompts**: Build complex prompts from simple, reusable blocks
4. **Test Different Formats**: Same structure works for XML, Markdown, and JSON
5. **Version Control Friendly**: Prompt changes are clear in diffs

## 📚 API Reference

### Core Classes

- **`InstructionBlock`**: Base class for all prompt blocks
- **`Text`**: Simple text content block
- **`Items`**: List/bullet point block  
- **`ModelBlock`**: Wrapper for Pydantic models
- **`RenderFormat`**: Enum for output formats (XML, MARKDOWN, JSON)

### Key Methods

- **`render(format, indent_level)`**: Render block in specified format
- **`to_xml()`**: Convenience method for XML output
- **`to_markdown()`**: Convenience method for Markdown output  
- **`to_json()`**: Convenience method for JSON output
- **`to_struct()`**: Convert to dictionary structure


## 🤝 Contributing

All contibutions are welcomed.


---

**SPOF** makes building structured prompts as easy as defining Pydantic models, while giving you the flexibility to render them in whatever format your LLM prefers. Build once, render everywhere! 🚀
