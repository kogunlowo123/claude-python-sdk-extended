# claude-python-sdk-extended

Extended Python SDK with retry logic, middleware, streaming, batch processing, conversation management, structured output parsing, and cost tracking.

## Architecture

```mermaid
flowchart TB
    subgraph Client["ExtendedClient"]
        style Client fill:#0078D4,color:#fff
        CoreClient["Core Client"]
        Config["Configuration"]
    end

    subgraph Middleware["Middleware Pipeline"]
        style Middleware fill:#FF9900,color:#fff
        RequestMW["Request Middleware"]
        ResponseMW["Response Middleware"]
        RequestMW --> ResponseMW
    end

    subgraph Resilience["Retry & Rate Limiting"]
        style Resilience fill:#DD344C,color:#fff
        RetryLogic["Exponential Backoff"]
        RateLimiter["Rate Limit Handler"]
    end

    subgraph Processing["Streaming & Batch"]
        style Processing fill:#3F8624,color:#fff
        Streaming["Streaming\n(Event Handlers)"]
        BatchProcessor["Batch Processor\n(Concurrency Control)"]
        Conversation["Conversation Manager\n(Context Windowing)"]
    end

    subgraph Analytics["Cost & Output"]
        style Analytics fill:#8C4FFF,color:#fff
        CostTracker["Cost Tracker\n& Usage Analytics"]
        StructuredOutput["Structured Output\nParser (JSON/KV)"]
        ToolCalling["Tool / Function\nCalling Helpers"]
    end

    Client --> Middleware
    Middleware --> Resilience
    Resilience --> Processing
    Processing --> Analytics
    CoreClient --> Config
```

## Features

- Automatic retry with exponential backoff and rate limit handling
- Middleware pipeline for request/response processing
- Streaming support with event handlers
- Batch processing with concurrency control
- Multi-turn conversation management with context windowing
- Structured output parsing (JSON, lists, key-value)
- Cost tracking and usage analytics
- Tool/function calling helpers

## Installation

```bash
pip install claude-sdk-extended
```

## Quick Start

```python
from claude_sdk_extended import ExtendedClient

client = ExtendedClient(api_key="your-key")

response = client.complete("Explain Kubernetes in one sentence.")
print(response)
```

## License

MIT Licensed. See [LICENSE](LICENSE) for details.
