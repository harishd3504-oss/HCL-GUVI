"""
Entity and Information Extractor
==================================
Extracts phone numbers, account numbers, names, and suspicious entities
from transcribed text.

This is crucial for understanding what information scammers are targeting.
"""

import re
import logging
from typing import Dict, List, Set
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ExtractedEntity:
    """Represents an extracted entity"""
    entity_type: str
    value: str
    confidence: float
    context: str = ""
    risk_level: str = "LOW"


class EntityExtractor:
    """Extracts entities and sensitive information from text"""

    def __init__(self):
        """Initialize entity extractor"""
        logger.info("EntityExtractor initialized")

    def extract_entities(self, text: str) -> Dict:
        """
        Extract entities and sensitive information.
        
        Args:
            text: Transcribed call text
            
        Returns:
            Dict with extracted entities
        """
        
        # Extract various entity types
        phone_numbers = self._extract_phone_numbers(text)
        account_numbers = self._extract_account_numbers(text)
        names = self._extract_names(text)
        financial_info = self._extract_financial_info(text)
        commands = self._extract_suspicious_commands(text)
        
        # Calculate risk from extracted information
        extraction_risk = self._calculate_extraction_risk(
            phone_numbers, account_numbers, financial_info, commands
        )
        
        analysis = {
            "phone_numbers": phone_numbers,
            "account_numbers": account_numbers,
            "names": names,
            "financial_info": financial_info,
            "suspicious_commands": commands,
            "information_extraction_risk": extraction_risk,
            "total_sensitive_items": len(phone_numbers) + len(account_numbers) + len(financial_info),
            "severity": self._assess_severity(phone_numbers, account_numbers, financial_info),
        }
        
        logger.info(f"Entity extraction completed: {len(phone_numbers)} phones, {len(account_numbers)} accounts")
        return analysis

    def _extract_phone_numbers(self, text: str) -> List[Dict]:
        """Extract phone numbers from text"""
        phone_patterns = [
            r'(?:\+?91[-.\s]?)?[6-9]\d{9}',  # Indian 10-digit
            r'(?:\+1)?[-.\s]?\(?[2-9]\d{2}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format
            r'(?:\+\d{1,3})?[-.\s]?\d{1,14}',  # International format
        ]
        
        phone_numbers = []
        for pattern in phone_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                number = match.group()
                context = text[max(0, match.start()-50):min(len(text), match.end()+50)]
                
                phone_numbers.append({
                    "value": number,
                    "context": context.strip(),
                    "risk_level": "CRITICAL",  # Phone number extraction is always critical
                    "confidence": 0.95,
                })
        
        # Remove duplicates
        seen = set()
        unique = []
        for phone in phone_numbers:
            if phone["value"] not in seen:
                seen.add(phone["value"])
                unique.append(phone)
        
        return unique

    def _extract_account_numbers(self, text: str) -> List[Dict]:
        """Extract account numbers and card numbers"""
        account_patterns = [
            r'account\s+(?:number|#|no\.?)\s*[:\-]?\s*([0-9\s]{8,20})',
            r'card\s+(?:number|#|no\.?)\s*[:\-]?\s*([0-9\s]{12,19})',
            r'(?:acc|acct)\.?\s*(?:no\.?|number|#)?\s*[:\-]?\s*([0-9\s]{8,20})',
            r'(?:card|cc)\s*[:\-]?\s*([0-9\s]{12,19})',
            r'reference\s+(?:number|#)\s*[:\-]?\s*([0-9A-Z\s]{6,20})',
        ]
        
        accounts = []
        for pattern in account_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                number = match.group(1) if match.lastindex else match.group()
                context = text[max(0, match.start()-50):min(len(text), match.end()+50)]
                
                accounts.append({
                    "value": number.strip(),
                    "context": context.strip(),
                    "risk_level": "CRITICAL",
                    "confidence": 0.85,
                })
        
        # Remove duplicates
        seen = set()
        unique = []
        for account in accounts:
            if account["value"] not in seen:
                seen.add(account["value"])
                unique.append(account)
        
        return unique

    def _extract_names(self, text: str) -> List[Dict]:
        """Extract person names and organizations"""
        # Simple pattern: capitalized words (not perfect but works for demo)
        word_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        
        names = []
        seen = set()
        
        matches = re.finditer(word_pattern, text)
        for match in matches:
            name = match.group()
            
            # Filter out common non-names
            if name not in ["The", "I", "It", "Mr", "Mrs", "Ms", "Dr", "Sir", "Madam"]:
                if name not in seen:
                    context = text[max(0, match.start()-50):min(len(text), match.end()+50)]
                    names.append({
                        "value": name,
                        "context": context.strip(),
                        "risk_level": "MEDIUM",
                        "confidence": 0.6,
                    })
                    seen.add(name)
        
        return names[:10]  # Limit to top 10

    def _extract_financial_info(self, text: str) -> List[Dict]:
        """Extract financial information (amounts, account types, etc)"""
        financial_info = []
        
        # Amount patterns (rupees, dollars, etc)
        amount_pattern = r'(?:rs|₹|\$|rupees|dollars)\s*(?:\.)?(\d+(?:,\d{3})*(?:\.\d{2})?)'
        matches = re.finditer(amount_pattern, text, re.IGNORECASE)
        for match in matches:
            amount = match.group(1)
            context = text[max(0, match.start()-50):min(len(text), match.end()+50)]
            
            financial_info.append({
                "type": "amount",
                "value": amount,
                "context": context.strip(),
                "risk_level": "HIGH",
                "confidence": 0.9,
            })
        
        # Account type patterns
        account_types = ["savings", "current", "checking", "credit", "debit", "loan"]
        for acc_type in account_types:
            pattern = r'\b' + acc_type + r'\s+(?:account|acc|a/c)?\b'
            if re.search(pattern, text, re.IGNORECASE):
                context_match = re.search(pattern, text, re.IGNORECASE)
                context = text[max(0, context_match.start()-50):min(len(text), context_match.end()+50)]
                
                financial_info.append({
                    "type": "account_type",
                    "value": acc_type,
                    "context": context.strip(),
                    "risk_level": "MEDIUM",
                    "confidence": 0.8,
                })
        
        return financial_info

    def _extract_suspicious_commands(self, text: str) -> List[Dict]:
        """Extract suspicious commands (asking user to do something harmful)"""
        suspicious_commands = {
            "share_otp": r'(?:give|share|tell|read|provide).*\botp\b',
            "confirm_details": r'(?:confirm|verify|say).*(?:password|pin|cvv|details)',
            "download_app": r'(?:download|install).*(?:app|application|software)',
            "make_payment": r'(?:transfer|send|pay).*(?:money|amount|rupees)',
            "disable_security": r'(?:disable|turn off|deactivate).*(?:2fa|security|protection)',
            "click_link": r'(?:click|open|visit).*(?:link|url|website)',
        }
        
        commands = []
        for cmd_type, pattern in suspicious_commands.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                context = text[max(0, match.start()-50):min(len(text), match.end()+50)]
                
                commands.append({
                    "type": cmd_type,
                    "value": match.group(),
                    "context": context.strip(),
                    "risk_level": "CRITICAL",
                    "confidence": 0.85,
                })
        
        return commands

    def _calculate_extraction_risk(self, phones: List, accounts: List, financial: List, commands: List) -> float:
        """Calculate risk from information extraction"""
        
        # Each type has different weight
        phone_risk = len(phones) * 15
        account_risk = len(accounts) * 20
        financial_risk = len(financial) * 10
        command_risk = len(commands) * 25
        
        total_risk = min(phone_risk + account_risk + financial_risk + command_risk, 100)
        
        return float(total_risk)

    def _assess_severity(self, phones: List, accounts: List, financial: List) -> str:
        """Assess severity of information extraction"""
        
        total_sensitive = len(phones) + len(accounts) + len(financial)
        
        if total_sensitive >= 5:
            return "CRITICAL"
        elif total_sensitive >= 3:
            return "HIGH"
        elif total_sensitive >= 1:
            return "MEDIUM"
        else:
            return "LOW"
