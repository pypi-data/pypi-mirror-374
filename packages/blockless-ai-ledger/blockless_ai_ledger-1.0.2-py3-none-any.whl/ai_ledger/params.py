"""
Core configuration parameters for the AI Ledger system.
All constants and default values are defined here.
"""

from decimal import Decimal

# Schema versioning
SCHEMA_VERSION = 1

# Consensus parameters
N_VALIDATORS = 7
QUORUM_K = 5
MAX_RISK_AVG = 0.25
OPINION_TIMEOUT_SECS = 1.5
MIN_DISTINCT_VALIDATORS = 3
MAX_CLOCK_SKEW_SECS = 120

# Asset configuration
DEFAULT_ASSET = "LABS"
ASSET_DECIMALS = {
    "LABS": 18,
    "USD": 6
}
GENESIS_SUPPLY = Decimal("1000")

# Network parameters
MAX_TX_SIZE = 10_000
MAX_NL_DESCRIPTION_LEN = 500
MAX_PENDING_PER_ACCOUNT = 5
RATE_LIMIT_TPS = 10

# LLM configuration
LLM_MODE = "stub"  # "openai", "stub", or "rule_only"
OPENAI_MODEL = "gpt-4-turbo-preview"
MAX_PROMPT_TOKENS = 1000
LLM_TEMPERATURE = 0.0
LLM_MAX_TOKENS = 200

# Security
PROMPT_SANITIZE = True
REQUIRE_SIGNATURE_DOMAIN = "ai_ledger"
SIGNATURE_VERSION = 1

# Demo mode
DEMO_SEED = 42
DEMO_PORTS = [8001, 8002, 8003, 8004, 8005]

# Storage
LOG_DIR_DEFAULT = "logs"
FSYNC_RECEIPTS = True

# Network timeouts
VALIDATOR_REQUEST_TIMEOUT = 2.0
VALIDATOR_HEALTH_CHECK_INTERVAL = 30.0

# Reputation system
INITIAL_VALIDATOR_REPUTATION = 1.0
MIN_REPUTATION_FOR_SELECTION = 0.1
REPUTATION_DECAY_FACTOR = 0.95

# Metrics and monitoring
METRICS_COLLECTION_INTERVAL = 10.0
HEALTH_CHECK_GRACE_PERIOD = 5.0