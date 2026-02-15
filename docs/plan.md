# DuckAI API Reverse Engineering Plan

## API Flow Analysis

Based on curl request analysis, DuckDuckGo AI uses a 4-step flow:

| Step | Order | Endpoint | Method | Purpose | Response |
|------|-------|----------|--------|---------|----------|
| 1 | 1 | `/country.json` | GET | Get user country | `{"country":"MA"}` |
| 2 | 2 | `/duckchat/v1/auth/token` | GET | Get auth token | `{}` (empty or token) |
| 3 | 3 | `/duckchat/v1/status` | GET | Get VQD token + status | `{"status":"0","secondaryStatus":"0","statusV2":0}` + VQD in headers |
| 4 | 4 | `/duckchat/v1/chat` | POST | Send message, stream response | SSE stream ending with `[DONE]` |

## Key Headers & Parameters

### Common Headers (All Requests)
- `access_type=dev_01` cookie (bypasses restrictions)
- Standard browser headers (User-Agent, Accept, Referer, etc.)
- Mobile Android UA to appear legitimate

### Step 3 (Status) Specific
- `x-vqd-accept: 1` - Tells server to return VQD token in response headers
- Response contains `x-vqd` header with token value

### Step 4 (Chat) Specific
- `accept: text/event-stream` - For SSE response
- `content-type: application/json`
- `x-vqd: <token_from_step_3>` - VQD token for session
- `x-fe-signals` - Base64 timing/events (optional for simplified)
- `x-fe-version` - Frontend version (optional for simplified)
- `x-vqd-hash-1` - Challenge/verification hash (**SKIPPED IN SIMPLIFIED VERSION**)

## Request Body (Chat)

```json
{
  "model": "openai/gpt-oss-120b",
  "metadata": {
    "customization": {
      "tone": "Default",
      "length": "Short",
      "shouldSeekClarity": false
    },
    "toolChoice": {
      "NewsSearch": false,
      "VideosSearch": false,
      "LocalSearch": false,
      "WeatherForecast": false
    }
  },
  "messages": [
    {"role": "user", "content": "hello what is 2 + 2"}
  ],
  "canUseTools": true,
  "canUseApproxLocation": null,
  "durableStream": {
    "messageId": "uuid-v4",
    "conversationId": "uuid-v4",
    "publicKey": {
      "alg": "RSA-OAEP-256",
      "e": "AQAB",
      "ext": true,
      "key_ops": ["encrypt"],
      "kty": "RSA",
      "n": "...base64-key...",
      "use": "enc"
    }
  }
}
```

## Response Format (SSE)

```
data: {"role":"assistant","message":"","created":1234567890,"id":"...","action":"success","model":"..."}

data: {"role":"assistant","message":"Hello","created":1234567890,"id":"...","action":"success","model":"..."}

data: {"role":"assistant","message":"Hello there","created":1234567890,"id":"...","action":"success","model":"..."}

data: [DONE]
```

## Simplified Approach

### What We'll Skip (For Now)
- [ ] `x-vqd-hash-1` challenge/verification hash generation
- [ ] `x-fe-signals` timing signals
- [ ] Message encryption (skip `publicKey`)
- [ ] Tool integration (set all to false)
- [ ] Dynamic model fetching

### What We'll Implement
- [x] Standard HTTP client with cookie handling
- [x] 4-step flow with VQD token extraction
- [x] UUID generation for message/conversation IDs
- [x] SSE response parsing
- [x] Basic streaming support
- [x] Error handling

## Implementation Phases

### Phase 1: Core HTTP Client
- Implement basic HTTP client with cookie jar
- Add request headers matching browser
- Implement step 1-3 (country, token, status)
- Extract and store VQD token

### Phase 2: Chat Functionality
- Implement step 4 (chat POST)
- Parse SSE stream
- Accumulate message chunks
- Handle [DONE] signal

### Phase 3: CLI Integration
- Wire up CLI commands
- Add interactive mode with streaming
- Handle errors gracefully
- Add conversation persistence

### Phase 4: Polish
- Add logging/debug mode
- Handle rate limiting
- Retry logic
- Better error messages

## Models Available

From observation:
- `openai/gpt-oss-120b`
- `gpt-4o-mini`
- `claude-3-haiku`
- `llama-3.1-70b`
- `mixtral-8x7b`

Note: Model names use provider/model format.

## Notes

- API endpoint: `https://duck.ai` (not `duckduckgo.com`)
- Uses SSE for streaming responses
- Requires persistent cookies across requests
- VQD token must be passed in `x-vqd` header for chat
- Simplified version may have rate limits or blocks
