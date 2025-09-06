# Epic LLM

**Break free from vendor lock-in.** Use your personal LLM subscriptions anywhere, with any client.

> **Language**: English | [中文](README-zh.md)

## ⚠️ Important Disclaimers

**READ THIS BEFORE USING**

### Terms of Service Warning
**Using this tool may violate the Terms of Service of LLM providers.** We are not responsible for any consequences including but not limited to:
- **Account suspension or termination**
- **Loss of subscription access**
- **Violation of provider terms**
- **Any damages or losses**

### User Responsibilities
- ✅ **Personal use only** - Use only with subscriptions you personally own and pay for
- ❌ **No sharing** - Do not share API access across multiple users or organizations
- ❌ **No commercial use** - Do not use for commercial API resale or business operations
- ⚖️ **Your risk** - You assume all legal and financial risks of using this tool

### Legal Notice - Third-Party Tools
**IMPORTANT: Epic LLM does NOT include any third-party API tools.** All provider tools are developed by independent third-party developers (NOT affiliated with Epic LLM, Anthropic, Google, GitHub, or other AI companies):

- **claude-code-api**: Third-party tool by independent developers (separate download required)
- **copilot-api**: Third-party tool by independent developers (separate download required)  
- **geminicli2api**: Third-party tool by independent developers (separate download required)

**Epic LLM only provides orchestration and management** - it does not bundle, distribute, or provide any third-party tools. Users are solely responsible for:
- Downloading third-party tools at their own discretion
- Compliance with each tool's license and the AI provider's Terms of Service
- Any legal implications of using unofficial third-party API tools

**This separation protects both users and Epic LLM from potential legal issues with AI service providers.**

### Provider-Specific Risks
- **Claude**: May detect automated usage patterns
- **GitHub Copilot**: Intended for development environments only
- **Gemini**: OAuth usage tracking may flag unusual access patterns

**USE AT YOUR OWN RISK. WE PROVIDE NO WARRANTIES AND ASSUME NO LIABILITY.**

---

## What is Epic LLM?

Epic LLM is a **AI subscription converter service** that helps you manage third-party tools to transform your personal LLM subscriptions (Claude Pro, GitHub Copilot, Gemini Advanced) into unified OpenAI-compatible APIs. Unlike traditional gateways like LiteLLM that require API keys, this orchestration tool helps you leverage your existing consumer subscriptions through **automated third-party repository management**.

### The Problem

- **Vendor Lock-in**: Each LLM provider forces you to use their official clients only
- **Limited Access**: Your Claude Pro subscription only works in Claude's web interface and Claude Code. A lot of LLM subscription service follow the same pattern.
- **Fragmented Workflow**: Switch between different apps for different models
- **Subscription Waste**: Pay for multiple subscriptions but can't use them in your preferred tools
- **Complex Manual Setup**: Each provider requires finding and cloning different GitHub repositories, learning various authentication methods, and managing separate tools
- **Dependency Hell**: Installing Node.js packages, Python tools, CLI utilities, and keeping them updated across different provider repositories

### The Solution

Epic LLM **automatically downloads and manages third-party repositories** created by independent developers to help aggregate your existing subscriptions into standard OpenAI-compatible APIs:

**🤖 Automated Repository Cloning**: One command finds and clones all third-party provider repositories - no manual repo hunting  
**🔧 Unified Management**: Single interface to start/stop/monitor all third-party tools instead of juggling multiple repositories  
**⚡ Zero Configuration**: Intelligent dependency detection and auto-installation of required tools (Node.js, npm packages, CLI tools)  
**🎯 One-Stop Setup**: `epic-llm install` handles everything - clones third-party repos, installs dependencies, sets up authentication

```bash
# Your Claude Pro subscription → Available anywhere
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'

# Your GitHub Copilot → Available anywhere  
curl http://localhost:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Write a function"}]
  }'
```

### Why This Matters

**🚀 Skip the Setup Nightmare**: No more hunting through GitHub repos, reading installation docs, or debugging dependency conflicts  
**🔓 Unlock Your Subscriptions**: Use Claude Pro in VSCode, Cursor, or any OpenAI-compatible tool  
**💰 Maximize Value**: Get full utility from subscriptions you're already paying for  
**🔧 Universal Access**: One API format works with hundreds of existing tools  
**🔒 Private & Secure**: Your credentials stay on your machine with optional gateway authentication
**⚡ Team-Friendly**: Share subscription access securely with API key protection
**⏱️ Save Hours**: What takes hours of manual setup now works in minutes with automated installation

## How It Works

1. **Check Dependencies**: `epic-llm check` scans your system and shows what's needed
2. **Auto-Clone Repositories**: `epic-llm install` finds and clones provider repositories automatically  
3. **Authenticate Once**: Use official provider methods (Claude CLI, GitHub CLI, Google OAuth) - Epic LLM guides you through each step
4. **Start & Forget**: `epic-llm start` launches all provider tools with automatic port management and health monitoring
5. **Use Anywhere**: Your subscriptions are now available as standard OpenAI APIs in any compatible tool

*Note: Epic LLM manages external GitHub repositories that use official provider authentication methods. Rate limits from the original services still apply.*

```mermaid
graph LR
    A[Your Tools] --> B[Epic LLM]
    B --> C[Claude Pro]
    B --> D[GitHub Copilot] 
    B --> E[Gemini Advanced]
    
    A --> F[VSCode/Cursor]
    A --> G[Custom Scripts]
    A --> H[AI Tools]
```

## Supported Providers

| Provider | Subscription Required | Port | Authentication |
|----------|----------------------|------|----------------|
| **Claude** | Claude Pro/Team | 8000 | Claude CLI (`claude auth login`) |
| **Copilot** | GitHub Copilot | 8081 | GitHub CLI (`gh auth login`) |
| **Gemini** | Gemini Advanced | 8888 | Google OAuth (web flow) |

## Quick Start

### NOTE: Operating system limitations
Some OS like Windows doesn't support some providers natively. You should run this inside a Linux Subsystem (WSL) layer to get this script to work. 

### 1. Run Epic LLM (No Installation Required!)

```bash
# Run Epic LLM directly with uvx - no installation needed!
uvx epic-llm --help

# Check what's needed for each provider
uvx epic-llm check

# Install third-party provider tools automatically
uvx epic-llm check --install
```

### 2. Alternative: Install Epic LLM

If you prefer to install Epic LLM:

```bash
# Install with uv (recommended)
uv tool install epic-llm

# Or install with pip
pip install epic-llm

# Then use normally
epic-llm --help
```

### 3. Automated Setup (One Command!)

```bash
# Check what's needed and auto-install everything
uvx epic-llm check --install

# This automatically clones and sets up third-party tools:
# ✅ claude-code-api repository (third-party Claude tool)
# ✅ copilot-api repository (third-party GitHub Copilot tool) 
# ✅ geminicli2api repository (third-party Gemini tool)
# ✅ All Node.js dependencies
# ✅ Required Python packages and CLI tools
```

### 4. Authenticate (Epic LLM guides you)

```bash
# Epic LLM will prompt you through each step
uvx epic-llm auth-status  # Shows what authentication is needed

# Claude: One command login
claude auth login

# Copilot: GitHub authentication  
gh auth login

# Gemini: OAuth flow opens automatically when first started
```

### 5. Start Everything

```bash
# One command starts all provider repositories with automatic port management
uvx epic-llm start

# Epic LLM handles:
# ✅ Starting downloaded repository tools
# ✅ Port allocation (avoiding conflicts)
# ✅ Process monitoring
# ✅ Health checks
# ✅ Restart on failure

# Or start specific providers
uvx epic-llm start claude copilot

# Check status anytime
uvx epic-llm status
```

### 6. Use Anywhere (Your Subscriptions Are Now APIs)

```python
# In your Python code
import openai

# Use Claude Pro subscription
client = openai.OpenAI(base_url="http://localhost:8000/v1", api_key="dummy")
response = client.chat.completions.create(
    model="claude-sonnet-4",
    messages=[{"role": "user", "content": "Hello Claude!"}]
)

# Use GitHub Copilot subscription  
client = openai.OpenAI(base_url="http://localhost:8081/v1", api_key="dummy")
response = client.chat.completions.create(
    model="gpt-4", 
    messages=[{"role": "user", "content": "Write a function"}]
)
```

## Management Commands

```bash
# List available providers
uvx epic-llm list

# Install provider dependencies
uvx epic-llm install

# Start/stop services
uvx epic-llm start [provider...]
uvx epic-llm stop [provider...]

# Check status and health
uvx epic-llm status
uvx epic-llm auth-status

# Verify dependencies
uvx epic-llm check [provider]

# Gateway Security (Protect your provider endpoints)
uvx epic-llm set-gateway-key claude --key "your-secure-key"    # Enable authentication
uvx epic-llm set-gateway-key claude                            # Disable authentication  
uvx epic-llm show-gateway-key claude                          # Show current status
```

## 🔒 Gateway Security

Secure your provider endpoints with API key authentication to control access:

### Use Case: IoT Development Teams
**Scenario**: Your IoT development team needs access to Gemini models for device automation and edge AI, but doesn't want to purchase separate API keys when team members already have Gemini subscriptions through their Google accounts.

**Solution**: Use Epic LLM with gateway authentication:

```bash
# Setup Gemini with your existing Google account
uvx epic-llm install gemini
uvx epic-llm start gemini

# Secure the gateway for team access  
uvx epic-llm set-gateway-key gemini --key "iot-team-secure-key-2024"

# Team members access via OpenAI-compatible endpoint
curl -H "Authorization: Bearer iot-team-secure-key-2024" \
     -H "Content-Type: application/json" \
     -d '{"model": "gemini-2.5-flash", "messages": [{"role": "user", "content": "Generate IoT sensor calibration code"}]}' \
     http://your-server:8888/v1/chat/completions
```

**Benefits**:
- ✅ Reuse existing Google subscriptions instead of buying API keys
- ✅ Secure team access with shared gateway authentication  
- ✅ OpenAI-compatible API works with existing codebases
- ✅ Cost-effective solution for development teams
- ✅ Control access to your subscription-based endpoints

## Directory Structure

```
~/.local/share/epic-llm/
├── state.json                     # Service status and configuration
└── pkg/                          # Downloaded provider repositories
    ├── claude-code-api/          # Git repo: https://github.com/codingworkflow/claude-code-api.git
    ├── copilot-api/              # Git repo: https://github.com/ericc-ch/copilot-api.git  
    └── geminicli2api/            # Git repo: https://github.com/gzzhongqi/geminicli2api.git
        └── oauth_creds.json      # Gemini OAuth credentials
```

External authentication (managed by official CLIs):
- **Claude**: `~/.claude/.credentials.json`
- **Copilot**: `~/.config/gh/hosts.yml` 
- **Gemini**: OAuth tokens in pkg directory

## Port Configuration

- **Claude**: `localhost:8000` (configurable)
- **Copilot**: `localhost:8081` (configurable)  
- **Gemini**: `localhost:8888` (configurable)
- **⚠️ Port 8080**: Reserved for Gemini OAuth callback (hardcoded, cannot change)

Override default ports:
```bash
uvx epic-llm start --port claude:8001 --port gemini:8889
```

## Compared to Other Solutions

| Feature | Epic LLM | Manual Setup | LiteLLM | Official APIs |
|---------|----------|--------------|---------|---------------|
| **Uses existing subscriptions** | ✅ | ✅ | ❌ | ❌ |
| **No additional API costs** | ✅ | ✅ | ❌ | ❌ |
| **Automated installation** | ✅ | ❌ | ❌ | ❌ |
| **Unified management interface** | ✅ | ❌ | ✅ | ❌ |
| **Dependency auto-detection** | ✅ | ❌ | ❌ | ❌ |
| **One-command setup** | ✅ | ❌ | ❌ | ❌ |
| **Automatic port management** | ✅ | ❌ | ❌ | ❌ |
| **Health monitoring** | ✅ | ❌ | ❌ | ❌ |
| **Setup time** | 5 minutes | 2-4 hours | 30 minutes | N/A |
| **Unified OpenAI format** | ✅ | ❌ | ✅ | ❌ |
| **Self-hosted** | ✅ | ✅ | ✅ | ❌ |

### Manual Setup Reality Check

**Without Epic LLM, you'd need to:**
- Find and clone 3+ different GitHub repositories:
  - `claude-code-api` for Claude Pro
  - `copilot-api` for GitHub Copilot  
  - `geminicli2api` for Gemini Advanced
- Install Node.js, npm, Python tools, and various CLI utilities
- Read through multiple README files and installation guides
- Debug version conflicts and dependency issues
- Manually configure authentication for each provider repository
- Set up port management to avoid conflicts between tools
- Create your own monitoring and restart scripts
- Keep everything updated as provider repositories change

**With Epic LLM:**
```bash
# That's it. Epic LLM handles the repository management automatically.
epic-llm install  # Clones all repos and installs dependencies
epic-llm start    # Starts all provider tools with management
```

## Use Cases

- **Developers**: Use Claude Pro in VSCode, Cursor, or custom tools
- **Researchers**: Access multiple models through a single interface
- **Teams**: Share subscription access across different applications
- **Automation**: Build scripts using premium models you already pay for
- **Privacy**: Keep everything local - no external API calls or key sharing

## Contributing

We welcome contributions! Epic LLM is designed to be extensible with new providers.

### Quick Start
```bash
# Set up development environment
git clone https://github.com/your-username/epic-llm.git
cd epic-llm
uv sync --dev

# Test your changes
./scripts/quick-test.sh

# Check code quality
uv run ruff check .
```

### Common Contributions
- 🚀 **Add New Providers**: Support for OpenAI API, Anthropic API, Local models
- 🐛 **Fix Bugs**: Check [GitHub Issues](https://github.com/epic-llm/epic-llm/issues)  
- 📚 **Improve Documentation**: User guides, examples, translations
- 🧪 **Add Tests**: Increase coverage and reliability

### Detailed Guide
See **[CONTRIBUTING.md](CONTRIBUTING.md)** for:
- Adding new LLM providers (step-by-step guide)
- Bug fix workflow
- Code style guidelines
- Testing requirements
- Security considerations

### Getting Help
- 📖 Read [CONTRIBUTING.md](CONTRIBUTING.md) first
- 🐛 Check [GitHub Issues](https://github.com/epic-llm/epic-llm/issues) 
- 💬 Start a [GitHub Discussion](https://github.com/epic-llm/epic-llm/discussions)
- 🧪 Look at existing provider implementations for examples

## Legal & Ethics

**⚠️ WARNING: Use at your own risk. Account bans possible.**

This tool may violate LLM provider Terms of Service. Users assume all responsibility for:

### Prohibited Uses
- ❌ **Multi-user sharing** - Do not share API access with others
- ❌ **Commercial resale** - Do not resell or monetize API access
- ❌ **Terms violations** - Respect each provider's usage policies
- ❌ **Rate limit abuse** - Do not exceed reasonable usage patterns

### Recommended Practices
- ✅ **Personal use only** - Use with your own subscriptions exclusively
- ✅ **Moderate usage** - Don't abuse or exceed normal usage patterns
- ✅ **Monitor ToS changes** - Provider terms may change and affect this tool

### Liability Disclaimer
**THE SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND. WE ARE NOT LIABLE FOR:**
- Account suspensions, bans, or terminations
- Loss of subscription access or services  
- Violation of third-party terms of service
- Any direct, indirect, incidental, or consequential damages

**You acknowledge that using this software may result in account restrictions and you assume all risks.**

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**💡 Tip**: Star this repo if it helps you get more value from your LLM subscriptions! Share this with a friend to free them from vendor lock-in. 