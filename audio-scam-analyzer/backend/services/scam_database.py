"""
Known Scam Database & Comparison Service
=========================================
Maintains database of known scam patterns and compares incoming calls
against them to detect if it matches known fraud campaigns.

This provides IMMEDIATE recognition of known scams.
"""

import logging
from typing import Dict, List, Tuple
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class KnownScamDatabase:
    """Database of known scam patterns and campaigns"""

    def __init__(self):
        """Initialize scam database"""
        logger.info("KnownScamDatabase initialized")
        
        # Known scam campaigns (real-world patterns)
        self.scam_campaigns = {
            "bank_otp_scam": {
                "name": "Bank OTP Phishing Scam",
                "severity": "CRITICAL",
                "description": "Scammer impersonates bank, asks for OTP",
                "keywords": ["otp", "verification code", "confirm", "urgent", "bank"],
                "common_phrases": [
                    "your account has been compromised",
                    "verify your identity",
                    "we detected unusual activity",
                    "share your otp",
                    "for security purposes"
                ],
                "typical_targets": ["Any bank customer"],
                "loss_average": "₹50,000 - ₹5,00,000",
            },
            "tax_authority_scam": {
                "name": "Tax Authority Impersonation",
                "severity": "CRITICAL",
                "description": "Scammer claims to be from tax dept, threatens arrest",
                "keywords": ["tax", "it", "income tax", "investigation", "arrest"],
                "common_phrases": [
                    "income tax investigation",
                    "you are involved in illegal activity",
                    "we will take action",
                    "pay immediately",
                    "this is your last warning"
                ],
                "typical_targets": ["Anyone with income"],
                "loss_average": "₹1,00,000 - ₹10,00,000",
            },
            "police_impersonation": {
                "name": "Police Authority Impersonation",
                "severity": "CRITICAL",
                "description": "Scammer claims to be police officer",
                "keywords": ["police", "crime", "complaint", "arrest", "criminal"],
                "common_phrases": [
                    "we have a case against you",
                    "you are involved in a crime",
                    "your name has been found",
                    "meet us immediately",
                    "we need to register your details"
                ],
                "typical_targets": ["Anyone with criminal concerns"],
                "loss_average": "₹50,000 - ₹5,00,000",
            },
            "loan_disbursement_scam": {
                "name": "Fake Loan Disbursement",
                "severity": "HIGH",
                "description": "Scammer offers loan, asks for advance fees",
                "keywords": ["loan", "disbursement", "approved", "processing", "fee"],
                "common_phrases": [
                    "your loan is approved",
                    "process immediately",
                    "processing fee required",
                    "disburse to your account",
                    "limited time offer"
                ],
                "typical_targets": ["Loan seekers"],
                "loss_average": "₹10,000 - ₹50,000",
            },
            "amazon_refund_scam": {
                "name": "E-commerce Refund Scam",
                "severity": "HIGH",
                "description": "Scammer claims to process refund, asks for details",
                "keywords": ["amazon", "refund", "order", "return", "account"],
                "common_phrases": [
                    "we need to process your refund",
                    "confirm your account details",
                    "link your bank account",
                    "update your payment method",
                    "verify your identity"
                ],
                "typical_targets": ["Online shoppers"],
                "loss_average": "₹20,000 - ₹2,00,000",
            },
            "tech_support_scam": {
                "name": "Tech Support Scam",
                "severity": "HIGH",
                "description": "Scammer claims virus on device, asks to install software",
                "keywords": ["virus", "malware", "security", "software", "install"],
                "common_phrases": [
                    "we detected a virus on your computer",
                    "your device is compromised",
                    "install this security software",
                    "give us remote access",
                    "your data is at risk"
                ],
                "typical_targets": ["Tech users"],
                "loss_average": "₹30,000 - ₹3,00,000",
            },
            "insurance_claim_scam": {
                "name": "Insurance Claim Scam",
                "severity": "HIGH",
                "description": "Scammer claims to help file insurance claim",
                "keywords": ["insurance", "claim", "policy", "accident", "premium"],
                "common_phrases": [
                    "we need to verify your policy",
                    "update your claim information",
                    "deposit required for claim processing",
                    "your claim is approved",
                    "collect your settlement"
                ],
                "typical_targets": ["Insurance policyholders"],
                "loss_average": "₹1,00,000 - ₹5,00,000",
            },
            "prize_money_scam": {
                "name": "Prize/Lottery Scam",
                "severity": "MEDIUM",
                "description": "Scammer claims you won prize/lottery",
                "keywords": ["prize", "lottery", "win", "congratulations", "reward"],
                "common_phrases": [
                    "congratulations you have won",
                    "claim your prize",
                    "tax or fees applicable",
                    "process your winnings",
                    "verify your details"
                ],
                "typical_targets": ["Anyone"],
                "loss_average": "₹10,000 - ₹1,00,000",
            }
        }

    def compare_call_with_campaigns(self, transcription: str) -> Dict:
        """
        Compare transcribed call against known scam campaigns.
        
        Args:
            transcription: Transcribed call text
            
        Returns:
            Dict with matching campaigns and confidence scores
        """
        
        text_lower = transcription.lower()
        matches = []
        
        # Compare against each campaign
        for campaign_id, campaign_info in self.scam_campaigns.items():
            match_score = self._calculate_campaign_match_score(
                text_lower,
                campaign_info
            )
            
            if match_score > 0:
                matches.append({
                    "campaign_id": campaign_id,
                    "campaign_name": campaign_info["name"],
                    "severity": campaign_info["severity"],
                    "match_confidence": match_score,
                    "description": campaign_info["description"],
                    "typical_targets": campaign_info["typical_targets"],
                    "loss_average": campaign_info["loss_average"],
                    "matched_keywords": self._get_matched_keywords(text_lower, campaign_info),
                    "matched_phrases": self._get_matched_phrases(text_lower, campaign_info),
                })
        
        # Sort by confidence (highest first)
        matches.sort(key=lambda x: x["match_confidence"], reverse=True)
        
        analysis = {
            "campaigns_matched": len(matches),
            "top_match": matches[0] if matches else None,
            "all_matches": matches,
            "is_known_scam": len(matches) > 0,
            "overall_match_confidence": matches[0]["match_confidence"] if matches else 0.0,
        }
        
        if matches:
            logger.warning(f"KNOWN SCAM DETECTED: {matches[0]['campaign_name']} (confidence: {matches[0]['match_confidence']})")
        
        return analysis

    def _calculate_campaign_match_score(self, text: str, campaign: Dict) -> float:
        """Calculate how closely text matches a campaign"""
        
        # Check keyword matches
        keyword_matches = sum(1 for kw in campaign["keywords"] if kw in text)
        keyword_score = (keyword_matches / len(campaign["keywords"])) if campaign["keywords"] else 0
        
        # Check phrase matches
        phrase_matches = sum(1 for phrase in campaign["common_phrases"] if phrase.lower() in text)
        phrase_score = (phrase_matches / len(campaign["common_phrases"])) if campaign["common_phrases"] else 0
        
        # Weight phrases more heavily (they're more specific)
        overall_score = (keyword_score * 0.3 + phrase_score * 0.7)
        
        # Only return if significant match
        return float(overall_score) if overall_score > 0.2 else 0.0

    def _get_matched_keywords(self, text: str, campaign: Dict) -> List[str]:
        """Get keywords that matched"""
        matched = []
        for keyword in campaign["keywords"]:
            if keyword in text:
                matched.append(keyword)
        return matched

    def _get_matched_phrases(self, text: str, campaign: Dict) -> List[str]:
        """Get common phrases that matched"""
        matched = []
        for phrase in campaign["common_phrases"]:
            if phrase.lower() in text:
                matched.append(phrase)
        return matched[:3]  # Top 3 phrases

    def get_campaign_statistics(self) -> Dict:
        """Get statistics about known scam campaigns"""
        return {
            "total_campaigns": len(self.scam_campaigns),
            "critical_severity": sum(1 for c in self.scam_campaigns.values() if c["severity"] == "CRITICAL"),
            "high_severity": sum(1 for c in self.scam_campaigns.values() if c["severity"] == "HIGH"),
            "medium_severity": sum(1 for c in self.scam_campaigns.values() if c["severity"] == "MEDIUM"),
            "campaigns": list(self.scam_campaigns.keys()),
        }

    def add_campaign(self, campaign_data: Dict) -> bool:
        """Add new scam campaign to database"""
        try:
            campaign_id = campaign_data.get("id")
            if campaign_id and campaign_id not in self.scam_campaigns:
                self.scam_campaigns[campaign_id] = campaign_data
                logger.info(f"New campaign added: {campaign_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error adding campaign: {e}")
            return False
