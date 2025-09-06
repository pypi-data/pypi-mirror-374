# Epic LLM Gateway Authentication Middleware - Final Implementation Plan

## Overview

This document outlines the implementation plan for a reusable authentication middleware system that extends providers without native gateway authentication support. The system provides a unified authentication interface across all providers while maintaining security and ease of use.

## Architecture

### System Design

```
External Access:
┌─────────────────┐    ┌──────────────────────┐
│   Client        │───▶│  Auth Middleware     │
│                 │    │  0.0.0.0:8081       │ (Public Port)
│  Bearer Token   │    │  (Gateway Auth)      │
└─────────────────┘    └──────────────────────┘
                                │
                                │ Forward authenticated requests
                                ▼
Localhost Only:         ┌─────────────────────┐
                        │  Upstream Provider   │
                        │  127.0.0.1:8082     │ (Internal Port)
                        │  (Original Server)   │
                        └─────────────────────┘
```

### Security Model

- **Public Port**: Auth middleware on `0.0.0.0:8081` (externally accessible)
- **Internal Port**: Upstream provider on `127.0.0.1:8082` (localhost only)
- **No Firewall Required**: OS-level network isolation via localhost binding
- **Random Port Allocation**: Internal ports assigned dynamically
- **Process Management**: Both processes managed as single unit

## Gateway Key Support Classification

### Enhanced Enum Definition

```python
class GatewayKeySupport(Enum):
    NONE = "none"           # No gateway authentication
    SINGLE = "single"       # Native single key support  
    MULTIPLE = "multiple"   # Native multiple key support
    MW_MULTIPLE = "mw_multiple"  # Middleware-provided multiple key support
```

### Provider Classification

| Provider | Support Level | Implementation | Description |
|----------|---------------|----------------|-------------|
| **Claude** | `MULTIPLE` | Native | Built-in via `API_KEYS` environment variable |
| **Gemini** | `SINGLE` | Native | Built-in via `GEMINI_AUTH_PASSWORD` environment variable |
| **Copilot** | `MW_MULTIPLE` | Middleware | Custom auth layer with multiple key support |

## Implementation Components

### 1. Authentication Middleware (`epic_llm/utils/auth_middleware.py`)

```python
class AuthMiddleware:
    def __init__(self, upstream_port: int, gateway_keys: list[str]):
        self.upstream_host = "127.0.0.1"  # Localhost only
        self.upstream_port = upstream_port
        self.gateway_keys = set(gateway_keys)
        self.server = None
        
    async def validate_request(self, request):
        """Validate Authorization: Bearer <token> header"""
        
    async def forward_request(self, request):
        """Proxy authenticated requests to upstream provider"""
        
    async def start(self, public_port: int):
        """Start middleware server on public port"""
        
    async def stop(self):
        """Stop middleware server"""
```

### 2. Enhanced State Management

```python
# State structure for middleware providers
{
    "copilot": {
        "process_id": 12345,        # Auth middleware PID
        "upstream_process_id": 12346, # Upstream provider PID
        "port": 8081,               # Public port (middleware)
        "upstream_port": 8082,      # Internal port (provider)
        "gateway_keys": ["key1"],
        "is_middleware": True,
        "gw_key_num_support": "mw_multiple"
    }
}
```

### 3. Multi-Process Lifecycle Management

#### Start Process (Middleware Providers)
1. Allocate random internal port for upstream provider
2. Start upstream provider on `127.0.0.1:<internal_port>`
3. Start auth middleware on `0.0.0.0:<public_port>`
4. Configure middleware with gateway keys
5. Store both PIDs in state management
6. Perform health checks on both services

#### Stop Process (Middleware Providers)
1. Terminate auth middleware process
2. Terminate upstream provider process
3. Clear state for both processes
4. Verify both processes are stopped

## User Interface

### Status Command Output

```bash
$ epic-llm status

Provider Status:
┌─────────┬────────────┬─────────┬──────────────┬─────────────────┐
│ Name    │ Status     │ Port    │ Internal     │ GW Key Support  │
├─────────┼────────────┼─────────┼──────────────┼─────────────────┤
│ claude  │ ✅ Running │ 8000    │ -            │ Multiple        │
│ gemini  │ ✅ Running │ 8888    │ -            │ Single          │
│ copilot │ ✅ Running │ 8081    │ 8082 (auth)  │ MW Multiple     │
└─────────┴────────────┴─────────┴──────────────┴─────────────────┘
```

### Gateway Key Management

```bash
# Set gateway key (works for all supported providers)
epic-llm set-gateway-key copilot --key "my-secret-key"
epic-llm set-gateway-key claude --key "claude-api-key"
epic-llm set-gateway-key gemini --key "gemini-password"

# Show gateway status with provider-specific information
$ epic-llm show-gateway-key copilot
🔐 Gateway authentication: ENABLED
📋 API Key: my-secr...tkey
🔧 GW Key Support: mw_multiple
💡 Note: Authentication provided by middleware (original provider has no auth)

Usage example:
curl -H "Authorization: Bearer my-secret-key" \
     http://localhost:8081/v1/models

$ epic-llm show-gateway-key claude  
🔐 Gateway authentication: ENABLED
📋 API Key: claude-...tkey
🔧 GW Key Support: multiple
💡 Note: Native authentication support

Usage example:
curl -H "Authorization: Bearer claude-api-key" \
     http://localhost:8000/v1/models
```

### Error Handling

```bash
# Attempt to set key on unsupported provider
$ epic-llm set-gateway-key some-future-provider --key "test"
❌ Provider 'some-future-provider' does not support gateway keys
💡 Supported providers: claude, gemini, copilot
```

## Configuration Management

### Gateway Configuration Files

**Copilot**: `~/.local/share/epic-llm/pkg/copilot/gateway_config.json`
```json
{
    "gateway_keys": ["user-api-key-123", "backup-key-456"],
    "auth_enabled": true,
    "middleware_type": "bearer_token",
    "support_level": "mw_multiple"
}
```

**Claude**: `~/.local/share/epic-llm/pkg/claude/gateway_config.json`
```json
{
    "gateway_api_keys": ["claude-key-1", "claude-key-2"],
    "auth_enabled": true,
    "support_level": "multiple"
}
```

**Gemini**: `~/.local/share/epic-llm/pkg/gemini/gateway_config.json`
```json
{
    "gateway_api_key": "single-gemini-key",
    "auth_enabled": true,
    "support_level": "single"
}
```

## Implementation Steps

### Phase 1: Core Infrastructure
1. **Create authentication middleware utility** (`auth_middleware.py`)
2. **Update GatewayKeySupport enum** (add `MW_MULTIPLE`)
3. **Enhance state manager** (support dual processes)
4. **Create middleware configuration system**

### Phase 2: Provider Integration
5. **Modify Copilot provider** (implement middleware mode)
6. **Update base provider class** (handle middleware providers)
7. **Enhance process lifecycle management**

### Phase 3: CLI Enhancement
8. **Update CLI commands** (handle middleware providers)
9. **Enhance status display** (show internal ports)
10. **Improve error messages** (provider-specific guidance)

### Phase 4: Testing & Documentation
11. **Create comprehensive tests** (middleware, multi-process, auth)
12. **Update CRUSH.md** (add middleware commands)
13. **Update README.md** (document authentication models)
14. **Add troubleshooting guide**

## Benefits

### Security
- ✅ **No external access** to upstream provider (localhost binding)
- ✅ **No firewall configuration** needed
- ✅ **Multiple authentication layers** available
- ✅ **Consistent token validation** across all providers

### User Experience
- ✅ **Transparent operation** (same CLI interface)
- ✅ **Clear provider capabilities** (MW Multiple vs Multiple)
- ✅ **Unified authentication** across all providers
- ✅ **Educational feedback** (native vs middleware)

### Architecture
- ✅ **Extensible design** (any provider can be extended)
- ✅ **Clean process management** (kill both on stop)
- ✅ **Backward compatible** (existing providers unchanged)
- ✅ **Future-proof** (easy to add new auth methods)

## Success Criteria

1. **Copilot provider supports gateway authentication** via middleware
2. **CLI commands work consistently** across all provider types
3. **Status command clearly shows** middleware vs native support
4. **Security is maintained** without user configuration
5. **Documentation is comprehensive** and easy to follow
6. **All existing functionality remains** unchanged

This implementation provides enterprise-grade authentication capabilities while maintaining Epic LLM's principle of simplicity and ease of use.