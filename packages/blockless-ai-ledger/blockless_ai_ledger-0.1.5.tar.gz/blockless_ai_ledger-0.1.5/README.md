# AI Ledger - AI-First Distributed Ledger System

> **Revolutionary ledger technology that replaces blockchain mining with AI-powered validation**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![AI-Powered](https://img.shields.io/badge/AI-Powered-green.svg)](https://github.com/ai-ledger)

## 🚀 What This Is

**NOT another blockchain!** AI Ledger is a fundamentally different approach to distributed ledger technology:

- **Natural Language Transactions**: `"Alice pays Bob 50 LABS for design work"`
- **AI Validators**: Replace energy-hungry miners with intelligent AI validators
- **Instant Finality**: Transactions finalize in ~1-2 seconds, not minutes or hours
- **Human-Readable**: Every transaction, receipt, and decision is explainable
- **Zero Energy Waste**: No proof-of-work, no mining, no environmental impact

## 🎯 Key Features

### 🧠 AI-Powered Consensus
- **Multiple AI Validators** independently evaluate each transaction
- **Risk Assessment** with explainable scoring (0.0 = safe, 1.0 = risky)  
- **Quorum Decision** requires 5 of 7 validators to approve with low risk
- **Human Judgment** layer on top of deterministic rules

### ⚡ Production Ready
- **Battle-Tested Security**: Ed25519 signatures, domain separation, replay protection
- **Decimal Precision**: No floating-point errors, proper financial math
- **Comprehensive Validation**: Clock skew protection, rate limiting, nonce management
- **Durable Storage**: Checksummed logs with fsync guarantees

### 🔍 Transparency & Verification
- **Tamper-Evident Receipts**: Every transaction gets a cryptographic receipt
- **Merkle Trees**: Account state integrity with inclusion proofs
- **Full Audit Trail**: Every decision is logged and verifiable
- **Real-Time Monitoring**: Health checks, metrics, and observability

## 🚀 Quick Start

### Prerequisites
- **Python 3.9 or higher**
- **OpenAI API key** (required for production nodes) - Get one at [platform.openai.com](https://platform.openai.com/api-keys)
- 8GB RAM (for OpenAI mode)  
- 1GB disk space

**Demo Mode (no API key needed):**
```bash
python3 -m venv ailedger
source ailedger/bin/activate  # On Windows: ailedger\Scripts\activate
pip install blockless-ai-ledger
python -m ai_ledger.demo
```

**Production Node (OpenAI API key required):**
```bash
python3 -m venv ailedger
source ailedger/bin/activate
pip install blockless-ai-ledger
export OPENAI_API_KEY="your-openai-api-key"
python -m ai_ledger.node --port 8001
```

### Installation

**One-line installer (handles all the complexity):**
```bash
curl -sSL https://raw.githubusercontent.com/netharalabs/blockless/main/install.sh | bash
```

**Option 2: From Source (Works with Python 3.9+)**
```bash
# Clone the repository (works with older Python versions)
git clone https://github.com/netharalabs/blockless.git
cd blockless

# Install dependencies
pip3 install -e .

# Run the interactive demo (no API keys needed!)
python3 -m ai_ledger.demo
```

> **⚠️ Python Version Note**: The PyPI package requires Python 3.11+ due to packaging requirements. If you have Python 3.9-3.10, use the source installation method above.

### Try with Real AI (OpenAI)

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-key-here"

# Run demo with real AI validation
python3 -m ai_ledger.demo --mode openai
```

## 📖 Demo Walkthrough

The demo runs 5 realistic transactions and shows you exactly how AI validation works:

```bash
🚀 AI Ledger Demo
Mode: STUB
============================================================

🌍 Initial State:
  alice       100.0 LABS (nonce=0, txs=0)
  bob           0.0 LABS (nonce=0, txs=0)
  treasury    900.0 LABS (nonce=0, txs=0)

💫 Demo Transactions
============================================================

Transaction 1: Normal Payment
  📤 Submitting: Alice pays Bob 25 LABS for web design work
    alice → bob: 25.0 LABS
    ✓ Accepted: abc123def456...
    🤖 Validator Opinions:
      ✓ val001: Risk=0.15 █▌ Normal meal transaction  
      ✓ val002: Risk=0.12 █▏ Valid transaction
      ✓ val003: Risk=0.18 █▊ Normal payment pattern
    ✅ APPROVED (5/7 validators, risk=0.150, time=1.2s)

📊 Final Results
============================================================
  alice          75.0 LABS (nonce=1, txs=1)
  bob            25.0 LABS (nonce=0, txs=1)

🎉 Demo completed successfully!
```

## 🏗️ Architecture Overview

```
User submits "Pay Bob $50" → Node → AI Validators → Quorum → Receipt
                              ↓        ↓             ↓        ↓
                           Mempool  AI+Rules    Consensus   Chain
```

### Core Components

1. **Transaction Layer**: Natural language transactions with comprehensive validation
2. **Validator Network**: AI-powered validators with fallback rule systems
3. **Quorum Manager**: Collects opinions and determines consensus  
4. **Storage Engine**: Durable, checksummed append-only logs
5. **Account Manager**: Balance tracking with atomic operations

### Trust Model

Instead of proof-of-work:
1. **Transaction Submitted** in natural language to any node
2. **Multiple AI Validators** evaluate independently using rules + AI judgment  
3. **Quorum Consensus** requires 5/7 validators to approve with average risk ≤0.25
4. **Tamper-Evident Receipt** created with cryptographic proofs
5. **Account State Updated** atomically with full audit trail

## 🛠️ Usage Examples

### Running a Node

```bash
# Start a node on port 8001 (OpenAI API key required!)
export OPENAI_API_KEY="your-key-here"
python3 -m ai_ledger.node --port 8001

# With custom log directory
export OPENAI_API_KEY="your-key-here"
python3 -m ai_ledger.node --port 8001 --log-dir ./my-logs

# Enable debug logging
export OPENAI_API_KEY="your-key-here"
python3 -m ai_ledger.node --port 8001 --log-level DEBUG
```

### Submit Transactions via API

```python
import httpx

async def send_payment():
    async with httpx.AsyncClient() as client:
        # Submit transaction
        response = await client.post("http://localhost:8001/submit", json={
            "nl_description": "Alice pays Bob 25 LABS for lunch",
            "from_acct": "alice", 
            "to_acct": "bob",
            "amount": "25.0",
            "nonce": 1
        })
        
        tx_id = response.json()["transaction_id"]
        print(f"Transaction submitted: {tx_id}")
        
        # Wait for finality
        while True:
            receipt = await client.get(f"http://localhost:8001/receipt/{tx_id}")
            if receipt.status_code == 200 and "receipt_id" in receipt.json():
                print("Transaction finalized!")
                break
            await asyncio.sleep(1)
```

### Generate Validator Keys

```bash
# Generate 7 validators for production
python3 -m ai_ledger.keygen generate --count 7 --output-dir ./production-keys

# Verify generated keys
python3 -m ai_ledger.keygen verify --file ./production-keys/validators.json
```

### Verify System Integrity

```bash
# Check specific receipt
python3 -m ai_ledger.verify receipt abc123def456...

# Verify account chain integrity  
python3 -m ai_ledger.verify account alice

# Full storage integrity check
python3 -m ai_ledger.verify storage-integrity

# Verify all recent receipts
python3 -m ai_ledger.verify all-receipts --limit 100
```

## 🔧 Configuration

### Environment Variables

```bash
# REQUIRED for production nodes and OpenAI mode
export OPENAI_API_KEY="your-openai-api-key"

# Optional configuration
export AI_LEDGER_LOG_LEVEL="INFO"
export AI_LEDGER_LOG_DIR="./logs"
export AI_LEDGER_PORT="8001"
```

### ⚠️ Important: OpenAI API Key Requirements

- **Demo Mode**: No API key needed for `python3 -m ai_ledger.demo`
- **Production Nodes**: OpenAI API key **REQUIRED** for `python3 -m ai_ledger.node`
- **Real Validation**: Without API key, nodes use stub/rule-only validation
- **Get API Key**: Sign up at [platform.openai.com](https://platform.openai.com/api-keys)

### Configuration Files

Edit `ai_ledger/params.py` to customize:

```python
# Consensus parameters
N_VALIDATORS = 7          # Number of validators
QUORUM_K = 5             # Required approvals
MAX_RISK_AVG = 0.25      # Maximum average risk score

# LLM configuration  
LLM_MODE = "stub"        # "openai", "stub", or "rule_only"
OPENAI_MODEL = "gpt-4-turbo-preview"

# Security settings
MAX_CLOCK_SKEW_SECS = 120
RATE_LIMIT_TPS = 10
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python3 -m pytest

# Run specific test categories
python3 -m pytest ai_ledger/tests/test_canonical.py   # Deterministic hashing
python3 -m pytest ai_ledger/tests/test_quorum.py      # Consensus mechanics
python3 -m pytest ai_ledger/tests/test_replay.py      # Replay protection
python3 -m pytest ai_ledger/tests/test_llm_safety.py  # AI safety

# Run with coverage
python3 -m pytest --cov=ai_ledger --cov-report=html
```

### Test Coverage
- **Canonical JSON**: Deterministic serialization and hashing
- **Quorum Consensus**: Validator opinion collection and consensus rules
- **Replay Protection**: Nonce management and duplicate prevention  
- **LLM Safety**: Prompt injection resistance and consistent behavior
- **Storage Integrity**: Checksum verification and corruption detection

## 📊 Monitoring & Observability

### Health Checks

```bash
curl http://localhost:8001/health
```

```json
{
  "status": "healthy",
  "uptime_seconds": 3600,
  "components": {
    "storage": {"status": "healthy", "stats": {...}},
    "validators": {"status": "healthy", "eligible_validators": 5},
    "accounts": {"status": "healthy", "account_count": 3}
  }
}
```

### Metrics (Prometheus Compatible)

```bash
curl http://localhost:8001/metrics
```

```
# HELP transactions_submitted Total transactions submitted
# TYPE transactions_submitted counter
transactions_submitted 1250

# HELP avg_finality_time Average time to finality in seconds  
# TYPE avg_finality_time gauge
avg_finality_time 1.234
```

### Debug Endpoints

```bash
# View mempool contents
curl http://localhost:8001/debug/mempool

# Get consensus parameters
curl http://localhost:8001/params

# Check account balances
curl http://localhost:8001/account/alice
```

## 🔐 Security Model

### Cryptographic Security
- **Ed25519 Signatures** for all validator opinions and receipts
- **Domain Separation** prevents cross-protocol signature reuse
- **Blake3 Hashing** for tamper-evident integrity
- **Merkle Trees** for efficient state verification

### Economic Security  
- **Validator Reputation** system with automatic stake adjustment
- **Rate Limiting** prevents spam and DoS attacks  
- **Nonce Management** prevents replay attacks
- **Clock Skew Protection** prevents timestamp manipulation

### AI Safety
- **Fail-Closed Design**: Errors result in transaction rejection
- **Prompt Injection Resistance**: Multiple layers of input sanitization
- **Deterministic Fallbacks**: Rule-only mode when AI unavailable
- **Multi-Validator Consensus**: No single AI can approve transactions

## 🎯 Production Deployment

### System Requirements

**Minimum**:
- 2 CPU cores
- 4GB RAM  
- 10GB SSD storage
- 100 Mbps network

**Recommended**:
- 4 CPU cores
- 8GB RAM
- 50GB SSD storage  
- 1 Gbps network

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -e .

EXPOSE 8001
CMD ["python3", "-m", "ai_ledger.node", "--port", "8001", "--host", "0.0.0.0"]
```

```bash
# Build and run
docker build -t ai-ledger .
docker run -p 8001:8001 -v ./logs:/app/logs ai-ledger
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-ledger-node
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-ledger
  template:
    metadata:
      labels:
        app: ai-ledger
    spec:
      containers:
      - name: ai-ledger
        image: ai-ledger:latest
        ports:
        - containerPort: 8001
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: ai-ledger-secrets
              key: openai-api-key
        volumeMounts:
        - name: logs
          mountPath: /app/logs
```

## 🛣️ Roadmap

### Phase 1: Core System ✅
- [x] AI-powered transaction validation
- [x] Quorum consensus mechanism
- [x] Deterministic state management
- [x] Comprehensive test coverage
- [x] Production security features

### Phase 2: Network Layer 🚧
- [ ] Multi-node consensus protocol
- [ ] Network partition tolerance
- [ ] Validator discovery and selection
- [ ] Cross-node receipt verification

### Phase 3: Advanced Features 📋
- [ ] Multi-asset support (USD, EUR, BTC)
- [ ] Smart contract equivalent (AI-validated programs)
- [ ] Web dashboard and explorer
- [ ] Mobile SDK and wallet apps
- [ ] Enterprise integrations

### Phase 4: Scale & Optimize 📋
- [ ] Horizontal scaling (1000+ TPS)
- [ ] Advanced AI models (GPT-5, Claude-4)
- [ ] Zero-knowledge privacy features
- [ ] Cross-ledger interoperability

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone and install in development mode
git clone https://github.com/netharalabs/blockless.git
cd blockless
pip3 install -e ".[dev]"

# Run tests
python3 -m pytest

# Format code  
black ai_ledger/
ruff ai_ledger/

# Type checking
mypy ai_ledger/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT models that power our AI validators
- **NaCl/libsodium** for production-grade cryptography
- **Blake3** for high-performance hashing
- **FastAPI** for the modern web framework
- **Pydantic** for data validation and serialization

## 📞 Support & Community

- **Documentation**: [docs.ai-ledger.org](https://docs.ai-ledger.org)
- **Issues**: [GitHub Issues](https://github.com/netharalabs/blockless/issues)
- **Discussions**: [GitHub Discussions](https://github.com/netharalabs/blockless/discussions)
- **Discord**: [Join our community](https://discord.gg/ai-ledger)

---

**Built with ❤️ by the AI Ledger team**

*"The future of money is intelligent, transparent, and instant."*