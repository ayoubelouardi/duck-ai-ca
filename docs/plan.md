# DuckAI API Implementation Plan

## Overview
Reverse engineer DuckDuckGo AI Chat API for use as a CLI tool and Python library.

## API Endpoints

### Base URL
```
https://duckduckgo.com
```

### Endpoints

#### 1. Get Status & VQD Token
```
GET /duckchat/v1/status
```

**Headers:**
```
accept: text/event-stream
accept-language: en-US,en;q=0.9
cache-control: no-cache
content-type: application/json
pragma: no-cache
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
origin: https://duckduckgo.com
referer: https://duckduckgo.com/
x-vqd-accept: 1
```

**Response Headers:**
- `x-vqd-4`: The VQD token (required for chat)
- `x-vqd-hash-1`: Optional hash (pass if present)

**Response Body:**
```json
{"status":"0","secondaryStatus":"0","statusV2":0}
```

#### 2. Chat
```
POST /duckchat/v1/chat
```

**Headers:**
```
accept: text/event-stream
accept-language: en-US,en;q=0.9
content-type: application/json
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
origin: https://duckduckgo.com
referer: https://duckduckgo.com/
x-vqd-4: <token from step 1>
```

**Request Body:**
```json
{
  "model": "gpt-4o-mini",
  "messages": [
    {"role": "user", "content": "Your question"}
  ]
}
```

**Response:**
Server-Sent Events (SSE) stream:
```
data: {"message":"Hello","created":1234567890,"id":"...","action":"success","model":"gpt-4o-mini"}

data: {"message":" there","created":1234567890,"id":"...","action":"success","model":"gpt-4o-mini"}

data: [DONE]
```

## Available Models

- `gpt-4o-mini` (default)
- `claude-3-haiku-20240307`
- `meta-llama/Llama-3.3-70B-Instruct-Turbo`
- `o3-mini`
- `mistralai/Mistral-Small-24B-Instruct-2501`

## Implementation Tasks

### Core Client
- [ ] Update BASE_URL to `https://duckduckgo.com`
- [ ] Update VQD header to `x-vqd-4`
- [ ] Remove JS challenge solver code
- [ ] Simplify request body (remove encryption/complex metadata)
- [ ] Implement proper SSE streaming
- [ ] Add conversation history support

### CLI
- [ ] Wire up chat command
- [ ] Implement interactive mode
- [ ] Add model selection
- [ ] Handle errors gracefully

### Testing
- [ ] Test single chat message
- [ ] Test streaming
- [ ] Test conversation continuity
- [ ] Test model switching
- [ ] Test error handling

## Architecture

```
src/duckai/
├── __init__.py          # Package exports
├── client.py            # DuckAIClient - main API client
└── models.py            # Data models (Message, Conversation)

cli/
├── __init__.py
└── main.py              # CLI entry point

docs/
├── plan.md              # This file
└── progress.md          # Implementation progress
```

## Key Design Decisions

1. **No external dependencies**: Use only Python stdlib
2. **Streaming support**: Real-time response streaming
3. **Conversation history**: Maintain context across messages
4. **Minimal complexity**: Remove unnecessary encryption/challenge logic
5. **Proven endpoint**: Use duckduckgo.com (validated by other projects)
