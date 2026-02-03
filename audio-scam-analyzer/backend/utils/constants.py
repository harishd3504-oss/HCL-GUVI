"""
Scam Detection Constants & Patterns
================================
This module contains all patterns, keywords, and rules used for 
scam detection. Organized by social engineering category.

PRIVACY NOTE: This module is for pattern analysis only. No actual 
call data is stored or transmitted.
"""

# =================
# SCAM KEYWORDS DETECTION
# =================

# Urgency & Pressure Keywords (trigger immediate action)
URGENCY_KEYWORDS = [
    "immediately",
    "right now",
    "quickly",
    "within 24 hours",
    "expire",
    "act now",
    "don't wait",
    "must act",
]

# Financial & Banking Keywords (exploitation angle)
BANKING_KEYWORDS = [
    "bank",
    "account",
    "credit card",
    "debit card",
    "transfer",
    "wire",
    "payment",
    "atm",
    "otp",
    "verification",
    "authenticate",
    "confirm identity",
    "balance",
    "transaction",
    "amount",
    "rupees",
    "dollars",
    "password",
    "pin",
    "cvv",
    "expiry",
]

# Authority Impersonation Keywords (fake legitimacy)
AUTHORITY_KEYWORDS = [
    "bank",
    "rbi",
    "police",
    "government",
    "tax",
    "revenue",
    "cybercrime",
    "official",
    "federal",
    "administrator",
    "compliance",
    "verification center",
    "security team",
    "fraud team",
    "legal",
]

# Fear & Threat Keywords (emotional manipulation)
FEAR_KEYWORDS = [
    "fraud",
    "scam",
    "compromised",
    "hacked",
    "stolen",
    "suspicious",
    "illegal",
    "crime",
    "arrest",
    "block",
    "suspend",
    "close",
    "freeze",
    "locked",
    "violation",
    "penalty",
    "lawsuit",
    "action",
]

# Trust Manipulation Keywords (false reassurance)
TRUST_KEYWORDS = [
    "verify",
    "confirm",
    "secure",
    "protection",
    "safe",
    "trusted",
    "official",
    "legitimate",
    "guarantee",
    "promise",
    "assure",
    "ensure",
]

# OTP & Verification Requests (critical red flag)
OTP_KEYWORDS = [
    "otp",
    "code",
    "verification code",
    "pin",
    "password",
    "secret",
    "one-time",
    "confirm code",
    "digits",
    "numbers",
    "tell me",
    "provide",
    "share",
]

# =================
# PATTERN RULES
# =================

# Scam Pattern Thresholds (fine-tuning detection)
PATTERNS = {
    "urgency_count_threshold": 2,  # 2+ urgency keywords = flag
    "banking_count_threshold": 3,  # 3+ banking keywords = flag
    "otp_request": 100,  # OTP request = high risk
    "authority_impersonation": 80,  # Authority claim = medium-high risk
    "fear_based_pressure": 70,  # Fear + urgency = medium risk
    "trust_building": 40,  # False reassurance = lower risk alone
}

# =================
# EXPLAINABILITY MESSAGES
# =================

EXPLANATION_TEMPLATES = {
    "otp_request": "🚨 CRITICAL: OTP/Password request detected. Legitimate institutions NEVER ask for OTP/passwords via phone.",
    "urgency_pressure": "⚠️ HIGH PRESSURE: Artificial urgency detected with time-pressure language ('{keywords}')",
    "authority_fake": "👤 IMPERSONATION: Caller claims to represent {authority} without verification.",
    "fear_based": "😨 FEAR TACTIC: Threat language detected ('{keywords}') designed to panic you into action.",
    "financial_exploitation": "💰 FINANCIAL TARGET: Multiple banking keywords detected ('{keywords}') - attempt to access money/data.",
    "multi_angle_attack": "🔴 COMPLEX ATTACK: Combination of urgency + authority + financial requests = sophisticated scam pattern.",
}

# =================
# RISK SCORING FACTORS
# =================

RISK_FACTORS = {
    "otp_request_score": 100,  # Absolute red flag
    "banking_keywords_score": 10,  # Reduced from 15
    "urgency_keywords_score": 15,  # Reduced from 20
    "authority_claim_score": 20,  # Reduced from 25
    "fear_keywords_score": 25,  # Increased as it's a stronger scam indicator
    "request_for_info_score": 30,  
}

# =================
# LINGUISTIC PATTERNS (Multilingual Support)
# =================

# Hindi scam indicators (Whisper supports Hindi)
HINDI_INDICATORS = {
    "urgency": ["jaldi", "turant", "abhi", "aaj hi"],
    "banking": ["account", "bank", "otp", "verify"],
    "fear": ["block", "police", "jel", "action"],
}

# Tamil indicators
TAMIL_INDICATORS = {
    "urgency": ["seekiram", "udanae", "ippovae", "kaala neram", "mudivaiyum"],
    "banking": ["panam", "kaasu", "bank-u", "account-u", "attain", "card-u", "verify seiya", "anuppunga"],
    "fear": ["block aagidum", "police-u", "moraikedi", "thiruttu", "kaithu", "lawsuit"],
    "otp": ["otp anuppunga", "code sollunga", "numbers kollunga", "secret code"],
}

# =================
# SAFE INDICATORS (Helps reduce false positives)
# =================

SAFE_INDICATORS = [
    "would you like",
    "please take your time",
    "no rush",
    "think about it",
    "optional",
    "voluntary",
    "at your convenience",
]

# =================
# RESPONSE TEMPLATES (For explainability)
# =================

RISK_CLASSIFICATION = {
    "90-100": ("CRITICAL_SCAM", "🔴"),
    "70-89": ("HIGH_RISK", "🟠"),
    "50-69": ("MEDIUM_RISK", "🟡"),
    "30-49": ("LOW_MEDIUM_RISK", "🟢"),
    "0-29": ("LIKELY_SAFE", "✅"),
}
