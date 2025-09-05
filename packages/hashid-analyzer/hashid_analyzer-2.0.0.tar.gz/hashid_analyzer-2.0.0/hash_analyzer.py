#!/usr/bin/env python3
"""
Comprehensive Hash and Token Analyzer
Version: 2.0

A professional tool for identifying and analyzing hash formats, tokens, and encoded data.
Designed for penetration testers, red team operators, security researchers, and developers.

Supported formats:
- Hash algorithms (MD5, SHA variants, bcrypt, scrypt, PBKDF2, etc.)
- Authentication tokens (JWT, API keys, session tokens)
- Cryptocurrency addresses (Bitcoin, Ethereum, etc.)
- Encoding formats (Base64, URL encoding, hex, etc.)
- Windows/Unix password hashes (NTLM, LM, crypt formats)
- Custom pattern analysis and entropy detection

Usage:
    python hash_analyzer.py <hash_or_token>
    python hash_analyzer.py --file <file_with_hashes>
    python hash_analyzer.py --interactive
    python hash_analyzer.py --persistent
    python hash_analyzer.py -p --quick
"""

import hashlib
import base64
import binascii
import itertools
import string
import math
import json
import csv
import time
import requests
import argparse
import re
import urllib.parse
import html
import logging
import sys
import os
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import warnings
warnings.filterwarnings('ignore', category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

try:
    import bcrypt
except ImportError:
    bcrypt = None

try:
    import jwt as jwt_lib
except ImportError:
    jwt_lib = None

class HashTokenAnalyzer:
    """
    Comprehensive analyzer for hashes, tokens, and encoded data.
    Enhanced with Blackploit HashID detection patterns.
    """
    
    # Extensive hash format database (inspired by HashID/Blackploit)
    HASH_ALGORITHMS = {
        # CRC and Checksums
        "102020": "ADLER-32", "102040": "CRC-32", "102060": "CRC-32B", 
        "101020": "CRC-16", "101040": "CRC-16-CCITT", "101060": "FCS-16",
        "102080": "XOR-32", "103040": "GHash-32-3", "103020": "GHash-32-5",
        
        # Unix and System Hashes
        "104020": "DES(Unix)", "107060": "MD5(Unix)", "108020": "MD5(APR)",
        "120020": "SHA-256(Unix)", "116040": "SAM(LM:NTLM)",
        
        # MD Family
        "106060": "MD2", "106120": "MD2(HMAC)", "106040": "MD4", "106100": "MD4(HMAC)",
        "106020": "MD5", "106080": "MD5(HMAC)", "106029": "NTLM", "106027": "RAdmin v2.x",
        "105060": "MD5(Half)", "105040": "MD5(Middle)", "105020": "MySQL(Old)",
        "106025": "Domain Cached Credentials", "106140": "MD5(HMAC-Wordpress)",
        
        # SHA Family
        "109020": "SHA-1", "109140": "SHA-1(HMAC)", "114020": "SHA-224", "114060": "SHA-224(HMAC)",
        "115020": "SHA-256", "115120": "SHA-256(HMAC)", "119020": "SHA-384", "119040": "SHA-384(HMAC)",
        "122020": "SHA-512", "122060": "SHA-512(HMAC)",
        
        # Application Specific
        "107040": "MD5(phpBB3)", "107020": "MD5(Wordpress)", "113020": "SHA-1(Django)",
        "117020": "SHA-256(Django)", "121020": "SHA-384(Django)", "112020": "MD5(Joomla)",
        "116020": "MD5(Joomla v2)", "109040": "MySQL5(SHA-1)", "109060": "MySQL 160bit",
        
        # Exotic Hashes
        "115060": "GOST R 34.11-94", "109100": "Haval-160", "109200": "Haval-160(HMAC)",
        "110040": "Haval-192", "110080": "Haval-192(HMAC)", "114040": "Haval-224",
        "114080": "Haval-224(HMAC)", "115040": "Haval-256", "115140": "Haval-256(HMAC)",
        "106160": "Haval-128", "106165": "Haval-128(HMAC)",
        
        # RIPEMD Family
        "106180": "RipeMD-128", "106185": "RipeMD-128(HMAC)", "109120": "RipeMD-160",
        "109180": "RipeMD-160(HMAC)", "115080": "RipeMD-256", "115160": "RipeMD-256(HMAC)",
        "118020": "RipeMD-320", "118040": "RipeMD-320(HMAC)",
        
        # Tiger Family
        "106220": "Tiger-128", "106225": "Tiger-128(HMAC)", "109080": "Tiger-160",
        "109160": "Tiger-160(HMAC)", "110020": "Tiger-192", "110060": "Tiger-192(HMAC)",
        
        # SNEFRU Family
        "106200": "SNEFRU-128", "106205": "SNEFRU-128(HMAC)",
        "115100": "SNEFRU-256", "115180": "SNEFRU-256(HMAC)",
        
        # Whirlpool
        "122040": "Whirlpool", "122080": "Whirlpool(HMAC)",
        
        # Game/Application Specific
        "107080": "Lineage II C4", "109220": "SHA-1(MaNGOS)", "109240": "SHA-1(MaNGOS2)",
        
        # Salted/Complex Variants
        "106240": "md5($pass.$salt)", "106280": "md5($salt.$pass)",
        "106500": "md5(md5($pass))", "109480": "sha1(sha1($pass))",
        "115200": "SHA-256(md5($pass))", "115220": "SHA-256(sha1($pass))"
    }
    
    def __init__(self, target_input: str, verbose: bool = True):
        self.original_input = target_input.strip()
        self.target_input = target_input.strip()
        self.verbose = verbose
        self.results = {
            'original_input': self.original_input,
            'input_length': len(self.original_input),
            'detected_formats': [],
            'hash_analysis': {},
            'token_analysis': {},
            'encoding_analysis': {},
            'crypto_analysis': {},
            'pattern_analysis': {},
            'entropy': None,
            'character_distribution': {},
            'cracking_attempts': {},
            'online_lookups': {},
            'recommendations': []
        }
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO if verbose else logging.WARNING,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def _print(self, message: str, level: str = "INFO") -> None:
        """Print message if verbose mode is enabled."""
        if self.verbose:
            prefix = {
                "INFO": "[*]",
                "SUCCESS": "[+]",
                "WARNING": "[!]", 
                "ERROR": "[-]",
                "CRITICAL": "[!!!]"
            }.get(level, "[*]")
            print(f"{prefix} {message}")
    
    def identify_hash_formats(self) -> None:
        """Identify potential hash formats based on length and character patterns."""
        self._print(f"Analyzing input: {self.target_input[:50]}{'...' if len(self.target_input) > 50 else ''}")
        self._print(f"Input length: {len(self.target_input)} characters")
        
        # Comprehensive hash format detection
        hash_formats = {
            # Standard hashes
            16: ["MD2", "MD4 (half)"],
            32: ["MD5", "MD4", "NTLM", "LM (half)"],
            40: ["SHA-1", "MySQL 4.1+", "Tiger"],
            48: ["Tiger2"],
            56: ["SHA-224", "SHA3-224"],
            64: ["SHA-256", "SHA3-256", "BLAKE2s", "CRC64"],
            80: ["RipeMD-320"],
            96: ["SHA-384", "SHA3-384"],
            128: ["SHA-512", "SHA3-512", "BLAKE2b", "Whirlpool"],
            # Variable length formats
            60: ["bcrypt"],
            120: ["SHA-384 (with salt)"],
            # Common base64 lengths
            22: ["MD5 (base64, no padding)"],
            24: ["MD5 (base64)"],
            28: ["SHA-1 (base64, no padding)"],
            32: ["SHA-1 (base64, padded)"],
            44: ["SHA-256 (base64, no padding)"],
            88: ["SHA-512 (base64, no padding)"]
        }
        
        length = len(self.target_input)
        detected_formats = []
        
        # Check exact length matches
        if length in hash_formats:
            detected_formats.extend(hash_formats[length])
            
        # Enhanced pattern-based detection
        self._detect_hash_patterns(detected_formats)
        self._detect_blackploit_patterns(detected_formats)  # New comprehensive detection
        self._detect_token_patterns(detected_formats)
        self._detect_encoding_patterns(detected_formats)
        self._detect_crypto_patterns(detected_formats)
        
        self.results['detected_formats'] = list(set(detected_formats))
        
        if detected_formats:
            self._print(f"Detected potential formats: {', '.join(detected_formats[:5])}{'...' if len(detected_formats) > 5 else ''}")
        else:
            self._print("No standard formats detected - proceeding with advanced analysis", "WARNING")
            
    def _detect_hash_patterns(self, detected_formats: List[str]) -> None:
        """Detect hash-specific patterns."""
        input_str = self.target_input
        
        # Hexadecimal check
        if re.match(r'^[a-fA-F0-9]+$', input_str):
            self.results['character_distribution']['hex_valid'] = True
            if len(input_str) % 2 == 0:
                detected_formats.append("Hexadecimal encoded data")
        
        # bcrypt pattern
        if re.match(r'^\$2[ayb]?\$[0-9]{2}\$[A-Za-z0-9./]{53}$', input_str):
            detected_formats.append("bcrypt")
            
        # scrypt pattern  
        if re.match(r'^\$scrypt\$', input_str):
            detected_formats.append("scrypt")
            
        # PBKDF2 pattern
        if re.match(r'^\$pbkdf2\$', input_str) or re.match(r'^pbkdf2:', input_str):
            detected_formats.append("PBKDF2")
            
        # Unix crypt patterns
        if re.match(r'^\$[156]\$', input_str):
            crypt_types = {'1': 'MD5 crypt', '5': 'SHA-256 crypt', '6': 'SHA-512 crypt'}
            crypt_type = crypt_types.get(input_str[1], 'Unknown crypt')
            detected_formats.append(crypt_type)
            
        # Windows NTLM/LM patterns
        if len(input_str) == 32 and re.match(r'^[a-fA-F0-9]{32}$', input_str):
            detected_formats.extend(["NTLM", "LM (possible)"])
            
        # MySQL password hashes
        if input_str.startswith('*') and len(input_str) == 41:
            detected_formats.append("MySQL 4.1+ password hash")
            
        # PostgreSQL md5 hash
        if input_str.startswith('md5') and len(input_str) == 35:
            detected_formats.append("PostgreSQL MD5")
            
    def _detect_blackploit_patterns(self, detected_formats: List[str]) -> None:
        """Enhanced pattern detection based on Blackploit HashID methodology."""
        input_str = self.target_input
        length = len(input_str)
        
        # Store detected algorithm IDs for ranking
        detected_ids = []
        
        # CRC and Checksum Detection (4-8 characters)
        if length == 4:
            if input_str.isalnum() and not input_str.isalpha() and not input_str.isdigit():
                detected_ids.extend(["101020", "101040", "101060"])  # CRC-16 variants
        elif length == 8:
            if input_str.isalnum() and not input_str.isalpha():
                detected_ids.extend(["102020", "102040", "102060", "102080"])  # 32-bit checksums
            elif input_str.isdigit():
                detected_ids.extend(["103020", "103040"])  # GHash variants
                
        # Unix DES (13 characters)
        elif length == 13 and not input_str.isdigit() and not input_str.isalpha():
            detected_ids.append("104020")  # DES(Unix)
            
        # MD5 variants (16 characters)
        elif length == 16 and input_str.isalnum() and not input_str.isalpha():
            detected_ids.extend(["105060", "105040", "105020"])  # MD5 halves, MySQL old
            
        # Standard hash lengths (32 characters - most common)
        elif length == 32:
            if input_str.isalnum() and not input_str.isalpha():
                detected_ids.extend([
                    "106020",  # MD5 (most likely)
                    "106040",  # MD4 
                    "106029",  # NTLM
                    "106025",  # Domain Cached Credentials
                    "106160",  # Haval-128
                    "106060",  # MD2
                    "106180",  # RipeMD-128
                    "106200",  # SNEFRU-128
                    "106220"   # Tiger-128
                ])
                # Add salted variants
                detected_ids.extend([
                    "106240", "106280", "106500", "106240"  # Various salted MD5
                ])
                
        # Special 32-char patterns
        elif length == 33 and input_str.startswith('*'):
            detected_ids.append("109060")  # MySQL 160bit
            
        # Application-specific MD5 variants (34+ characters with prefixes)
        elif input_str.startswith('$H$') and length == 34:
            detected_ids.append("107040")  # MD5(phpBB3)
        elif input_str.startswith('$P$') and length == 34:
            detected_ids.append("107020")  # MD5(Wordpress)
        elif input_str.startswith('$1$') and length > 30:
            detected_ids.append("107060")  # MD5(Unix)
        elif input_str.startswith('$apr1$') and length > 35:
            detected_ids.append("108020")  # MD5(APR)
        elif input_str.startswith('$6$') and length > 90:
            detected_ids.append("120020")  # SHA-256(Unix)
            
        # SHA-1 and 160-bit hashes (40 characters)
        elif length == 40:
            if input_str.isalnum() and not input_str.isalpha():
                detected_ids.extend([
                    "109020",  # SHA-1 (most likely)
                    "109040",  # MySQL5
                    "109100",  # Haval-160
                    "109120",  # RipeMD-160
                    "109080"   # Tiger-160
                ])
                # Add salted SHA-1 variants
                detected_ids.extend([
                    "109260", "109280", "109480", "109500"
                ])
                
        # Tiger-192 and Haval-192 (48 characters)
        elif length == 48:
            if input_str.isalnum() and not input_str.isalpha():
                detected_ids.extend(["110020", "110040"])  # Tiger-192, Haval-192
                
        # Joomla hashes (with colon separator)
        elif ':' in input_str and length > 40:
            if input_str.index(':') == 32:  # MD5:salt format
                detected_ids.extend(["112020", "116020"])  # Joomla variants
                
        # Django framework hashes
        elif input_str.startswith('sha1$') and length > 45:
            detected_ids.append("113020")  # SHA-1(Django)
        elif input_str.startswith('sha256$') and length > 70:
            detected_ids.append("117020")  # SHA-256(Django)  
        elif input_str.startswith('sha384$') and length > 100:
            detected_ids.append("121020")  # SHA-384(Django)
            
        # SHA-224 (56 characters)
        elif length == 56:
            if input_str.isalnum() and not input_str.isalpha():
                detected_ids.extend(["114020", "114040"])  # SHA-224, Haval-224
                
        # SHA-256 and 256-bit hashes (64 characters)
        elif length == 64:
            if input_str.isalnum() and not input_str.isalpha():
                detected_ids.extend([
                    "115020",  # SHA-256 (most likely)
                    "115040",  # Haval-256
                    "115060",  # GOST R 34.11-94
                    "115080",  # RipeMD-256
                    "115100",  # SNEFRU-256
                    "115200",  # SHA-256(md5($pass))
                    "115220"   # SHA-256(sha1($pass))
                ])
                
        # RipeMD-320 (80 characters)
        elif length == 80:
            if input_str.isalnum() and not input_str.isalpha():
                detected_ids.append("118020")  # RipeMD-320
                
        # SHA-384 (96 characters)
        elif length == 96:
            if input_str.isalnum() and not input_str.isalpha():
                detected_ids.append("119020")  # SHA-384
                
        # SHA-512 and Whirlpool (128 characters)
        elif length == 128:
            if input_str.isalnum() and not input_str.isalpha():
                detected_ids.extend(["122020", "122040"])  # SHA-512, Whirlpool
                
        # Special case: Lineage II C4 (with 0x prefix)
        elif input_str.startswith('0x') and length == 34:
            detected_ids.append("107080")  # Lineage II C4
            
        # SAM format (LM:NTLM)
        elif ':' in input_str and length == 65 and input_str.index(':') == 32:
            if input_str.upper() == input_str:  # Usually uppercase
                detected_ids.append("116040")  # SAM
                
        # Convert algorithm IDs to human-readable names and add to detected formats
        for alg_id in detected_ids[:10]:  # Limit to top 10 matches
            if alg_id in self.HASH_ALGORITHMS:
                algorithm_name = self.HASH_ALGORITHMS[alg_id]
                if algorithm_name not in detected_formats:
                    detected_formats.append(algorithm_name)
                    
        # Store algorithm confidence ranking
        self.results['blackploit_analysis'] = {
            'detected_algorithm_ids': detected_ids[:5],  # Top 5 matches
            'confidence_ranking': [self.HASH_ALGORITHMS.get(aid, f"Unknown-{aid}") 
                                 for aid in detected_ids[:5]]
        }
            
    def _detect_token_patterns(self, detected_formats: List[str]) -> None:
        """Detect various token patterns."""
        input_str = self.target_input
        
        # JWT pattern (3 base64 parts separated by dots)
        if re.match(r'^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]*$', input_str):
            detected_formats.append("JWT (JSON Web Token)")
            
        # API Key patterns
        api_patterns = {
            r'^sk-[A-Za-z0-9]{48}$': 'OpenAI API Key',
            r'^xoxb-[0-9]+-[0-9]+-[A-Za-z0-9]+$': 'Slack Bot Token',
            r'^xoxp-[0-9]+-[0-9]+-[0-9]+-[A-Za-z0-9]+$': 'Slack User Token',
            r'^github_pat_[A-Za-z0-9_]{82}$': 'GitHub Personal Access Token',
            r'^ghp_[A-Za-z0-9]{36}$': 'GitHub Personal Access Token (Classic)',
            r'^ghs_[A-Za-z0-9]{36}$': 'GitHub App Token',
            r'^AKIA[0-9A-Z]{16}$': 'AWS Access Key ID',
            r'^ya29\.[A-Za-z0-9_-]+$': 'Google OAuth2 Access Token',
            r'^[A-Za-z0-9]{64}$': 'Generic 64-char API Key',
            r'^[A-Za-z0-9]{40}$': 'Generic 40-char API Key (GitHub/GitLab style)',
        }
        
        for pattern, description in api_patterns.items():
            if re.match(pattern, input_str):
                detected_formats.append(description)
                
        # Session tokens and cookies
        if len(input_str) >= 16 and re.match(r'^[A-Za-z0-9+/=]+$', input_str):
            try:
                decoded = base64.b64decode(input_str + '==', validate=True)
                if len(decoded) > 8:
                    detected_formats.append("Base64 encoded session token")
            except:
                pass
                
    def _detect_encoding_patterns(self, detected_formats: List[str]) -> None:
        """Detect various encoding patterns."""
        input_str = self.target_input
        
        # Base64 pattern
        if re.match(r'^[A-Za-z0-9+/]*={0,2}$', input_str) and len(input_str) % 4 == 0:
            detected_formats.append("Base64 encoded")
            
        # Base64 URL-safe pattern
        if re.match(r'^[A-Za-z0-9_-]*$', input_str):
            detected_formats.append("Base64 URL-safe encoded")
            
        # URL encoded pattern
        if '%' in input_str and re.search(r'%[0-9A-Fa-f]{2}', input_str):
            detected_formats.append("URL encoded")
            
        # HTML entity pattern
        if '&' in input_str and ';' in input_str:
            if re.search(r'&[a-zA-Z][a-zA-Z0-9]*;|&#[0-9]+;|&#x[0-9A-Fa-f]+;', input_str):
                detected_formats.append("HTML entity encoded")
                
        # Unicode escape pattern
        if re.search(r'\\u[0-9A-Fa-f]{4}', input_str):
            detected_formats.append("Unicode escaped")
            
    def _detect_crypto_patterns(self, detected_formats: List[str]) -> None:
        """Detect cryptocurrency address patterns."""
        input_str = self.target_input
        
        crypto_patterns = {
            r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$': 'Bitcoin Address (P2PKH/P2SH)',
            r'^bc1[a-z0-9]{39,59}$': 'Bitcoin Address (Bech32)',
            r'^0x[a-fA-F0-9]{40}$': 'Ethereum Address',
            r'^[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}$': 'Litecoin Address',
            r'^D{1}[5-9A-HJ-NP-U]{1}[1-9A-HJ-NP-Za-km-z]{32}$': 'Dogecoin Address',
            r'^r[a-zA-Z0-9]{24,34}$': 'Ripple Address',
            r'^[A-Z2-7]{58}$': 'Monero Address',
        }
        
        for pattern, description in crypto_patterns.items():
            if re.match(pattern, input_str):
                detected_formats.append(description)
                
    def analyze_jwt_token(self) -> Dict[str, Any]:
        """Analyze JWT tokens in detail."""
        if 'JWT' not in ' '.join(self.results['detected_formats']):
            return {}
            
        try:
            parts = self.target_input.split('.')
            if len(parts) != 3:
                return {'error': 'Invalid JWT format'}
                
            header_data, payload_data, signature = parts
            
            # Decode header and payload
            def safe_b64decode(data):
                # Add padding if needed
                padding = 4 - (len(data) % 4)
                if padding != 4:
                    data += '=' * padding
                return base64.urlsafe_b64decode(data)
                
            try:
                header = json.loads(safe_b64decode(header_data))
                payload = json.loads(safe_b64decode(payload_data))
                
                jwt_analysis = {
                    'header': header,
                    'payload': payload,
                    'signature': signature,
                    'algorithm': header.get('alg', 'Unknown'),
                    'token_type': header.get('typ', 'Unknown'),
                    'key_id': header.get('kid', 'Not specified'),
                }
                
                # Check for security issues
                security_issues = []
                if header.get('alg') == 'none':
                    security_issues.append("CRITICAL: 'none' algorithm - no signature verification")
                if header.get('alg') in ['HS256', 'HS384', 'HS512'] and not signature:
                    security_issues.append("WARNING: HMAC algorithm with empty signature")
                    
                # Check expiration
                if 'exp' in payload:
                    exp_time = datetime.fromtimestamp(payload['exp'])
                    if exp_time < datetime.now():
                        security_issues.append(f"WARNING: Token expired on {exp_time}")
                    else:
                        jwt_analysis['expires'] = exp_time.isoformat()
                        
                jwt_analysis['security_issues'] = security_issues
                
                self._print(f"JWT Analysis - Algorithm: {jwt_analysis['algorithm']}, Type: {jwt_analysis['token_type']}")
                if security_issues:
                    for issue in security_issues:
                        self._print(issue, "WARNING" if "WARNING" in issue else "CRITICAL")
                        
                return jwt_analysis
                
            except json.JSONDecodeError:
                return {'error': 'Failed to decode JWT payload'}
            except Exception as e:
                return {'error': f'JWT analysis failed: {str(e)}'}
                
        except Exception as e:
            return {'error': f'JWT parsing failed: {str(e)}'}

    def comprehensive_encoding_analysis(self) -> Dict[str, Any]:
        """Perform comprehensive encoding analysis."""
        analysis = {}
        input_str = self.target_input
        
        # Base64 variants
        base64_variants = {
            'standard': lambda x: base64.b64decode(x + '=' * (4 - len(x) % 4)),
            'urlsafe': lambda x: base64.urlsafe_b64decode(x + '=' * (4 - len(x) % 4)),
        }
        
        for variant, decoder in base64_variants.items():
            try:
                decoded = decoder(input_str)
                if all(32 <= b <= 126 for b in decoded):  # Printable ASCII
                    analysis[f'base64_{variant}'] = decoded.decode('ascii')
                    self._print(f"Base64 {variant} decode: {decoded.decode('ascii')[:50]}{'...' if len(decoded) > 50 else ''}")
            except:
                pass
                
        # Hex decoding
        try:
            if len(input_str) % 2 == 0 and re.match(r'^[a-fA-F0-9]+$', input_str):
                hex_decoded = bytes.fromhex(input_str)
                if all(32 <= b <= 126 for b in hex_decoded):  # Printable ASCII
                    analysis['hex_decode'] = hex_decoded.decode('ascii')
                    self._print(f"Hex decode: {hex_decoded.decode('ascii')[:50]}{'...' if len(hex_decoded) > 50 else ''}")
        except:
            pass
            
        # URL decoding
        try:
            url_decoded = urllib.parse.unquote(input_str)
            if url_decoded != input_str:
                analysis['url_decode'] = url_decoded
                self._print(f"URL decode: {url_decoded[:50]}{'...' if len(url_decoded) > 50 else ''}")
        except:
            pass
            
        # HTML entity decoding
        try:
            html_decoded = html.unescape(input_str)
            if html_decoded != input_str:
                analysis['html_decode'] = html_decoded
                self._print(f"HTML decode: {html_decoded[:50]}{'...' if len(html_decoded) > 50 else ''}")
        except:
            pass
            
        # XOR analysis (single-byte keys)
        if re.match(r'^[a-fA-F0-9]+$', input_str) and len(input_str) % 2 == 0:
            try:
                hex_bytes = bytes.fromhex(input_str)
                for key in range(1, 256):
                    xored = bytes(b ^ key for b in hex_bytes)
                    if all(32 <= b <= 126 for b in xored):  # Printable ASCII
                        decoded_str = xored.decode('ascii')
                        if len(decoded_str) > 4 and self._is_meaningful_text(decoded_str):
                            analysis[f'xor_key_{key:02x}'] = decoded_str
                            self._print(f"XOR key 0x{key:02x}: {decoded_str[:50]}{'...' if len(decoded_str) > 50 else ''}")
                            break  # Only show first meaningful result
            except:
                pass
                
        return analysis
    
    def _is_meaningful_text(self, text: str) -> bool:
        """Check if text appears to be meaningful using improved heuristics."""
        if len(text) < 3:
            return False
            
        # Check for reasonable character distribution
        alpha_count = sum(1 for c in text if c.isalpha())
        digit_count = sum(1 for c in text if c.isdigit())
        space_count = sum(1 for c in text if c.isspace())
        punct_count = sum(1 for c in text if c in '.,!?;:-_()[]{}"\'')
        
        total_meaningful = alpha_count + digit_count + space_count + punct_count
        
        # At least 70% should be meaningful characters
        if total_meaningful / len(text) < 0.7:
            return False
            
        # Should have some alphabetic characters
        if alpha_count / len(text) < 0.3:
            return False
            
        # Check for common English patterns (basic)
        common_patterns = ['the', 'and', 'ing', 'ion', 'er', 'ed', 'es', 'ly']
        text_lower = text.lower()
        pattern_matches = sum(1 for pattern in common_patterns if pattern in text_lower)
        
        return pattern_matches > 0 or len(text) > 20

    def _is_potential_flag(self, text: str) -> bool:
        """Check if text matches common flag patterns (CTF, bug bounty, etc.)."""
        text_lower = text.lower()
        flag_patterns = [
            text_lower.startswith('flag{'),
            text_lower.startswith('ctf{'),
            text_lower.startswith('htb{'),  # HackTheBox
            text_lower.startswith('thm{'),  # TryHackMe
            '{' in text and '}' in text and len(text) > 10,
            'flag' in text_lower and any(c in text for c in '{}[]()'),
            text_lower.startswith('key:'),
            text_lower.startswith('password:'),
        ]
        return any(flag_patterns)

    def hash_cracking_attempts(self) -> Optional[str]:
        """Attempt to crack hash using various methods."""
        # Only attempt cracking for recognized hash formats
        potential_hashes = [f for f in self.results['detected_formats'] 
                          if any(h in f.lower() for h in ['md5', 'sha1', 'sha256', 'ntlm'])]
        
        if not potential_hashes:
            return None
            
        self._print("Attempting hash cracking...")
        
        # Enhanced wordlist
        common_passwords = [
            # Common passwords
            'password', 'admin', 'root', 'user', 'test', 'guest', 'administrator',
            '123456', 'password123', 'admin123', 'qwerty', 'letmein', 'welcome',
            # Security-related
            'pentest', 'security', 'hash', 'crack', 'decrypt', 'hacker', 'exploit',
            # System defaults
            'changeme', 'default', 'secret', 'private', 'public', 'system',
            # Years
            '2024', '2023', '2022', '2021', '2020',
            # Common phrases
            'hello', 'world', 'testing', 'sample', 'demo', 'example'
        ]
        
        # Test common passwords with multiple algorithms
        for password in common_passwords:
            if self._test_multiple_hash_algorithms(password):
                return password
                
        # Quick numeric test (0-9999)
        self._print("Testing numeric sequences...")
        for i in range(10000):
            test_val = str(i).zfill(4)
            if self._test_multiple_hash_algorithms(test_val):
                self._print(f"Numeric password found: {test_val}", "CRITICAL")
                return test_val
                
        # Date patterns (recent years only for performance)
        self._print("Testing recent date patterns...")
        for year in range(2020, 2025):
            for month in range(1, 13):
                date_formats = [str(year), f"{year}{month:02d}"]
                for date_format in date_formats:
                    if self._test_multiple_hash_algorithms(date_format):
                        self._print(f"Date password found: {date_format}", "CRITICAL")
                        return date_format
                        
        return None
    
    def _test_multiple_hash_algorithms(self, plaintext: str) -> bool:
        """Test plaintext against multiple hash algorithms."""
        algorithms = {
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha256': hashlib.sha256,
            'sha224': hashlib.sha224,
            'sha384': hashlib.sha384,
            'sha512': hashlib.sha512,
        }
        
        target_lower = self.target_input.lower()
        
        for alg_name, alg_func in algorithms.items():
            try:
                hash_result = alg_func(plaintext.encode('utf-8')).hexdigest().lower()
                if hash_result == target_lower:
                    self.results['cracking_attempts'][alg_name] = plaintext
                    self._print(f"Password found using {alg_name.upper()}: '{plaintext}'", "CRITICAL")
                    return True
                    
                # Test with common salt patterns
                for salt in ['', 'salt', '123', plaintext[::-1]]:
                    salted_hash = alg_func((salt + plaintext).encode('utf-8')).hexdigest().lower()
                    if salted_hash == target_lower:
                        self.results['cracking_attempts'][f'{alg_name}_salted'] = f'{salt}:{plaintext}'
                        self._print(f"Salted password found using {alg_name.upper()} (salt: '{salt}'): '{plaintext}'", "CRITICAL")
                        return True
            except:
                continue
                
        # Test NTLM if applicable
        if len(target_lower) == 32:
            try:
                ntlm_hash = hashlib.new('md4', plaintext.encode('utf-16le')).hexdigest().lower()
                if ntlm_hash == target_lower:
                    self.results['cracking_attempts']['ntlm'] = plaintext
                    self._print(f"NTLM password found: '{plaintext}'", "CRITICAL")
                    return True
            except:
                pass
                
        return False

    def online_hash_lookup(self) -> Dict[str, str]:
        """Attempt online hash database lookups with enhanced services."""
        self._print("Attempting online hash lookups...")
        
        # Only lookup if it looks like a hash
        if not any(f for f in self.results['detected_formats'] 
                  if any(h in f.lower() for h in ['md5', 'sha', 'hash'])):
            return {}
        
        lookup_results = {}
        target_hash = self.target_input.lower()
        
        # Enhanced service list with error handling
        services = [
            {
                'name': 'HashKiller',
                'url': f'https://hashkiller.io/api/search/{target_hash}',
                'headers': {'User-Agent': 'HashAnalyzer/2.0'}
            }
        ]
        
        for service in services:
            try:
                self._print(f"Checking {service['name']}...")
                response = requests.get(
                    service['url'], 
                    headers=service.get('headers', {}),
                    timeout=15,
                    verify=False
                )
                
                if response.status_code == 200:
                    result = response.text.strip()
                    if result and 'not found' not in result.lower() and len(result) > 0:
                        lookup_results[service['name']] = result
                        self._print(f"{service['name']}: {result[:50]}{'...' if len(result) > 50 else ''}", "SUCCESS")
                        
                        if self._is_potential_flag(result):
                            self._print(f"Potential flag found: {result}", "CRITICAL")
                    else:
                        self._print(f"{service['name']}: No match found")
                else:
                    self._print(f"{service['name']}: Service returned {response.status_code}", "WARNING")
                    
            except requests.exceptions.Timeout:
                self._print(f"{service['name']}: Request timeout", "WARNING")
            except Exception as e:
                self._print(f"{service['name']}: Error - {str(e)[:50]}", "ERROR")
                
        # Provide manual lookup suggestions
        self._print("\nManual lookup resources:")
        manual_resources = [
            f"CrackStation: https://crackstation.net/",
            f"MD5 Online: https://md5.gromweb.com/",
            f"Hashes.com: https://hashes.com/decrypt/hash",
            f"OnlineHashCrack: https://www.onlinehashcrack.com/"
        ]
        
        for resource in manual_resources:
            self._print(f"  {resource}")
            
        self.results['online_lookups'] = lookup_results
        return lookup_results

    def comprehensive_analysis(self) -> None:
        """Run complete analysis suite."""
        self._print("=" * 70)
        self._print("COMPREHENSIVE HASH AND TOKEN ANALYSIS")
        self._print("=" * 70)
        
        # Core analysis steps
        self.identify_hash_formats()
        self._calculate_entropy()
        self._character_frequency_analysis()
        
        # Specialized analysis based on detected formats
        if 'JWT' in ' '.join(self.results['detected_formats']):
            self.results['token_analysis']['jwt'] = self.analyze_jwt_token()
            
        self.results['encoding_analysis'] = self.comprehensive_encoding_analysis()
        
        # Hash cracking (only for suspected hashes)
        cracked = self.hash_cracking_attempts()
        if cracked:
            self.results['cracking_attempts']['found'] = cracked
            
        # Online lookups
        self.online_hash_lookup()
        
        # Advanced pattern analysis
        self._advanced_pattern_analysis()
        
        # Generate recommendations
        self._generate_recommendations()
        
        # Summary
        self._print("\n" + "=" * 70)
        self._print("ANALYSIS SUMMARY")
        self._print("=" * 70)
        self._print_summary()
    
    def _calculate_entropy(self) -> None:
        """Calculate Shannon entropy with enhanced analysis."""
        def shannon_entropy(data: str) -> float:
            if not data:
                return 0.0
            entropy = 0.0
            for x in set(data):
                p_x = data.count(x) / len(data)
                entropy -= p_x * math.log2(p_x)
            return entropy
            
        entropy = shannon_entropy(self.target_input)
        self.results['entropy'] = entropy
        
        self._print(f"Shannon entropy: {entropy:.3f} bits")
        
        # Enhanced entropy analysis
        if entropy < 2.5:
            self._print("Very low entropy - likely structured data or weak hash", "WARNING")
        elif entropy < 3.5:
            self._print("Low entropy - possible pattern or repeated data", "WARNING")
        elif entropy > 4.5:
            self._print("High entropy - likely cryptographic hash or random data", "SUCCESS")
        else:
            self._print("Moderate entropy - further analysis recommended")
            
    def _character_frequency_analysis(self) -> None:
        """Enhanced character frequency analysis."""
        char_freq = Counter(self.target_input.lower())
        self.results['character_distribution'] = dict(char_freq)
        
        if self.verbose:
            self._print("Character frequency analysis:")
            
            # Analyze by character type
            digits = sum(count for char, count in char_freq.items() if char.isdigit())
            alpha = sum(count for char, count in char_freq.items() if char.isalpha())
            symbols = sum(count for char, count in char_freq.items() if not char.isalnum())
            
            total = len(self.target_input)
            self._print(f"  Digits: {digits}/{total} ({digits/total*100:.1f}%)")
            self._print(f"  Letters: {alpha}/{total} ({alpha/total*100:.1f}%)")
            self._print(f"  Symbols: {symbols}/{total} ({symbols/total*100:.1f}%)")
            
            # Check for unusual distributions
            if char_freq.most_common(1)[0][1] > total * 0.2:
                most_common = char_freq.most_common(1)[0]
                self._print(f"High frequency character '{most_common[0]}': {most_common[1]} times", "WARNING")
                
    def _advanced_pattern_analysis(self) -> None:
        """Advanced pattern detection and analysis."""
        patterns = {}
        input_str = self.target_input
        
        # Repeating substring analysis
        for length in range(2, min(10, len(input_str) // 2)):
            for i in range(len(input_str) - length + 1):
                substring = input_str[i:i+length]
                if input_str.count(substring) > 1:
                    patterns[f'repeat_{length}char'] = patterns.get(f'repeat_{length}char', []) or []
                    patterns[f'repeat_{length}char'].append(substring)
                    
        # Structure analysis
        structure_patterns = {
            'has_periods': '.' in input_str,
            'has_dashes': '-' in input_str,
            'has_underscores': '_' in input_str,
            'has_colons': ':' in input_str,
            'has_brackets': any(c in input_str for c in '()[]{}')}
        
        patterns.update(structure_patterns)
        self.results['pattern_analysis'] = patterns
        
        # Report significant patterns
        if any(structure_patterns.values()):
            self._print("Structural patterns detected - possibly encoded data or token format")
            
    def _generate_recommendations(self) -> None:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        # Based on detected formats
        formats = self.results['detected_formats']
        
        if any('JWT' in f for f in formats):
            recommendations.append("Analyze JWT token for security vulnerabilities (weak algorithms, missing signature)")
            
        if any('API' in f or 'Token' in f for f in formats):
            recommendations.append("Check if API token is still valid and what permissions it grants")
            
        if any('bcrypt' in f.lower() for f in formats):
            recommendations.append("bcrypt detected - use specialized tools like hashcat for cracking")
            
        if any('bitcoin' in f.lower() or 'ethereum' in f.lower() for f in formats):
            recommendations.append("Cryptocurrency address detected - check blockchain explorers for transaction history")
            
        if self.results['entropy'] < 3.0:
            recommendations.append("Low entropy suggests weak randomness - try pattern-based attacks")
            
        if any('base64' in f.lower() for f in formats):
            recommendations.append("Base64 encoding detected - check for nested encoding layers")
            
        # General recommendations
        recommendations.extend([
            "Cross-reference with other discovered data in your assessment",
            "Check for similar patterns in configuration files or databases",
            "Consider the context where this hash/token was found",
            "Try different wordlists specific to the target organization/application"
        ])
        
        self.results['recommendations'] = recommendations
        
    def _print_summary(self) -> None:
        """Print analysis summary."""
        # Detected formats
        if self.results['detected_formats']:
            self._print(f"Detected formats: {', '.join(self.results['detected_formats'][:3])}{'...' if len(self.results['detected_formats']) > 3 else ''}")
            
        # Enhanced Blackploit analysis results
        if self.results.get('blackploit_analysis', {}).get('confidence_ranking'):
            self._print("\nBlackploit-style confidence ranking:")
            ranking = self.results['blackploit_analysis']['confidence_ranking']
            if len(ranking) >= 2:
                self._print(f"  Most likely: {ranking[0]}")
                self._print(f"  Alternative: {ranking[1]}")
            if len(ranking) > 2:
                others = ', '.join(ranking[2:])
                self._print(f"  Less likely: {others}")
            
        # Key findings
        key_findings = []
        
        if self.results.get('cracking_attempts'):
            key_findings.append("PASSWORD/PLAINTEXT FOUND")
            
        if self.results.get('token_analysis', {}).get('jwt', {}).get('security_issues'):
            key_findings.append("JWT SECURITY ISSUES DETECTED")
            
        if self.results.get('encoding_analysis'):
            key_findings.append(f"{len(self.results['encoding_analysis'])} encoding methods successful")
            
        if key_findings:
            self._print("Key findings: " + ', '.join(key_findings), "CRITICAL")
        else:
            self._print("No immediate vulnerabilities or plaintext found")
            
        # Recommendations
        if self.results['recommendations']:
            self._print("\nTop recommendations:")
            for i, rec in enumerate(self.results['recommendations'][:3], 1):
                self._print(f"  {i}. {rec}")
                
    def export_results(self, format_type: str = 'json', filename: str = None) -> str:
        """Export analysis results to file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if not filename:
            filename = f"hash_analysis_{timestamp}.{format_type}"
            
        try:
            if format_type == 'json':
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
                    
            elif format_type == 'csv':
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Category', 'Subcategory', 'Value'])
                    
                    def write_nested(data, category=''):
                        for key, value in data.items():
                            if isinstance(value, dict):
                                write_nested(value, f"{category}.{key}" if category else key)
                            elif isinstance(value, list):
                                writer.writerow([category, key, '; '.join(map(str, value))])
                            else:
                                writer.writerow([category, key, str(value)])
                                
                    write_nested(self.results)
                    
            elif format_type == 'txt':
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Hash/Token Analysis Report\n")
                    f.write(f"Generated: {datetime.now().isoformat()}\n")
                    f.write(f"Target: {self.original_input}\n")
                    f.write(f"{'='*50}\n\n")
                    
                    for category, data in self.results.items():
                        f.write(f"{category.upper()}:\n")
                        if isinstance(data, dict):
                            for key, value in data.items():
                                f.write(f"  {key}: {value}\n")
                        elif isinstance(data, list):
                            for item in data:
                                f.write(f"  - {item}\n")
                        else:
                            f.write(f"  {data}\n")
                        f.write("\n")
                        
            self._print(f"Results exported to: {filename}", "SUCCESS")
            return filename
            
        except Exception as e:
            self._print(f"Export failed: {e}", "ERROR")
            return ""

def analyze_from_file(filepath: str) -> List[Dict[str, Any]]:
    """Analyze multiple hashes/tokens from a file."""
    results = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    print(f"\n{'='*50}")
                    print(f"Analyzing line {line_num}: {line[:50]}{'...' if len(line) > 50 else ''}")
                    print('='*50)
                    
                    analyzer = HashTokenAnalyzer(line)
                    analyzer.comprehensive_analysis()
                    results.append({
                        'line': line_num,
                        'input': line,
                        'results': analyzer.results
                    })
        return results
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return []

def persistent_mode(quick_mode=False, verbose=True):
    """Run in persistent mode for continuous hash/token analysis."""
    session_history = []
    analysis_count = 0
    
    if not quick_mode:
        print_banner()
    
    print("\n" + "="*60)
    print("PERSISTENT HASH/TOKEN ANALYZER - v2.0")
    print("="*60)
    print("Enter hash/token followed by ENTER to analyze.")
    print("Commands: 'help', 'history', 'clear', 'stats', 'quit'")
    print("Tip: Use Ctrl+C or 'quit' to exit\n")
    
    start_time = time.time()
    
    while True:
        try:
            # Enhanced prompt with analysis count
            prompt = f"[{analysis_count}] hash/token > "
            user_input = input(prompt).strip()
            
            # Handle empty input
            if not user_input:
                continue
                
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print(f"\nSession Statistics:")
                print(f"  Total analyses: {analysis_count}")
                print(f"  Session time: {time.time() - start_time:.1f} seconds")
                print("Goodbye!")
                break
                
            elif user_input.lower() == 'help':
                print("\nAvailable Commands:")
                print("  <hash/token>     - Analyze the provided hash or token")
                print("  help            - Show this help message")
                print("  history         - Show analysis history")
                print("  clear           - Clear the screen")
                print("  stats           - Show session statistics")
                print("  quit/exit/q     - Exit the program")
                print("\nFeatures:")
                print("  - Supports all hash formats (MD5, SHA, NTLM, etc.)")
                print("  - JWT token analysis")
                print("  - Cryptocurrency addresses")
                print("  - Online hash lookups")
                print("  - Automatic encoding detection\n")
                continue
                
            elif user_input.lower() == 'history':
                if not session_history:
                    print("No analysis history available.\n")
                else:
                    print("\nAnalysis History:")
                    for i, (timestamp, input_hash, detected) in enumerate(session_history[-10:], 1):
                        short_hash = input_hash[:30] + "..." if len(input_hash) > 30 else input_hash
                        formats = detected[:2] if detected else ['Unknown']
                        print(f"  {i}. [{timestamp}] {short_hash} -> {', '.join(formats)}")
                    if len(session_history) > 10:
                        print(f"  ... ({len(session_history) - 10} more entries)")
                    print()
                continue
                
            elif user_input.lower() == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
                print("Screen cleared. Session continues...\n")
                continue
                
            elif user_input.lower() == 'stats':
                print(f"\nSession Statistics:")
                print(f"  Total analyses: {analysis_count}")
                print(f"  Session time: {time.time() - start_time:.1f} seconds")
                print(f"  History entries: {len(session_history)}")
                
                if session_history:
                    format_counts = {}
                    for _, _, formats in session_history:
                        for fmt in formats:
                            format_counts[fmt] = format_counts.get(fmt, 0) + 1
                    
                    if format_counts:
                        print("  Most common formats:")
                        for fmt, count in sorted(format_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                            print(f"    {fmt}: {count}")
                print()
                continue
            
            # Analyze the input
            analysis_count += 1
            print(f"\n{'='*50}")
            print(f"Analysis #{analysis_count}: {user_input[:30]}{'...' if len(user_input) > 30 else ''}")
            print('='*50)
            
            analyzer = HashTokenAnalyzer(user_input, verbose=verbose)
            
            if quick_mode:
                analyzer.identify_hash_formats()
                analyzer._calculate_entropy()
                if 'JWT' in ' '.join(analyzer.results['detected_formats']):
                    analyzer.results['token_analysis']['jwt'] = analyzer.analyze_jwt_token()
            else:
                analyzer.comprehensive_analysis()
            
            # Store in history
            timestamp = datetime.now().strftime('%H:%M:%S')
            detected_formats = analyzer.results.get('detected_formats', [])
            session_history.append((timestamp, user_input, detected_formats))
            
            # Quick result summary for persistent mode
            if detected_formats:
                print(f"\n[QUICK SUMMARY] Detected: {', '.join(detected_formats[:3])}{'...' if len(detected_formats) > 3 else ''}")
            
            if analyzer.results.get('cracking_attempts'):
                print("[CRITICAL] Password/plaintext found in cracking attempts!")
                
            print(f"\n{'='*50}\n")
            
        except KeyboardInterrupt:
            print(f"\n\nSession Statistics:")
            print(f"  Total analyses: {analysis_count}")
            print(f"  Session time: {time.time() - start_time:.1f} seconds")
            print("\nGoodbye!")
            break
        except Exception as e:
            # Handle cases where user_input might not be defined
            input_display = user_input[:30] + '...' if 'user_input' in locals() and len(user_input) > 30 else (user_input if 'user_input' in locals() else 'input')
            print(f"Error analyzing '{input_display}': {e}\n")

def interactive_mode():
    """Run in interactive mode for multiple analyses."""
    print("Interactive Hash/Token Analyzer")
    print("Enter 'quit' or 'exit' to stop, 'help' for commands\n")
    
    while True:
        try:
            user_input = input("Enter hash/token to analyze: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            elif user_input.lower() == 'help':
                print("Commands:")
                print("  <hash/token> - Analyze the input")
                print("  help - Show this help")
                print("  quit/exit/q - Exit the program")
                continue
            elif not user_input:
                continue
                
            print(f"\n{'='*60}")
            analyzer = HashTokenAnalyzer(user_input)
            analyzer.comprehensive_analysis()
            print('='*60)
            
            # Ask if user wants to export results
            export = input("\nExport results? (json/csv/txt/n): ").strip().lower()
            if export in ['json', 'csv', 'txt']:
                filename = analyzer.export_results(export)
                if filename:
                    print(f"Results saved to {filename}")
                    
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

def print_banner():
    """Print professional banner."""
    banner = r'''
   #########################################################################
   #     __  __                     __           ______    _____           #
   #    /\ \/\ \                   /\ \         /\__  _\  /\  _ `\         #
   #    \ \ \_\ \     __      ____ \ \ \___     \/_/\ \/  \ \ \/\ \        #
   #     \ \  _  \  /'__`\   / ,__\ \ \  _ `\      \ \ \   \ \ \ \ \       #
   #      \ \ \ \ \/\ \_\ \_/\__, `\ \ \ \ \ \      \_\ \__ \ \ \_\ \      #
   #       \ \_\ \_\ \___ \_\/\____/  \ \_\ \_\     /\_____\ \ \____/      #
   #        \/_/\/_/\/__/\/_/\/___/    \/_/\/_/     \/_____/  \/___/  v2.0 #
   #                                                             by xp     #
   #                                  Hash Identifier                      #
   #########################################################################
    '''
    print(banner)

def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive Hash and Token Analyzer v2.0",
        epilog="Examples:\n"
               "  python hash_analyzer.py 5d41402abc4b2a76b9719d911017c592\n"
               "  python hash_analyzer.py eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiYWRtaW4ifQ.abc123\n"
               "  python hash_analyzer.py --file hashes.txt\n"
               "  python hash_analyzer.py --interactive\n"
               "  python hash_analyzer.py --persistent\n"
               "  python hash_analyzer.py -p --quick\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'target', 
        nargs='?', 
        help='Hash, token, or encoded data to analyze'
    )
    parser.add_argument(
        '--file', '-f',
        help='Analyze hashes/tokens from a file (one per line)'
    )
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode'
    )
    parser.add_argument(
        '--export', '-e',
        choices=['json', 'csv', 'txt'],
        help='Export results to file'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output filename (default: auto-generated)'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress verbose output'
    )
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Skip time-intensive operations (brute force, online lookups)'
    )
    parser.add_argument(
        '--persistent', '-p',
        action='store_true',
        help='Run in persistent mode (keeps running for multiple analyses)'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='Hash Token Analyzer v2.0'
    )
    
    args = parser.parse_args()
    
    # Handle different modes
    if args.persistent:
        persistent_mode(quick_mode=args.quick, verbose=not args.quiet)
        return
        
    if args.interactive:
        interactive_mode()
        return
        
    if args.file:
        results = analyze_from_file(args.file)
        if args.export and results:
            # Export combined results
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = args.output or f"batch_analysis_{timestamp}.{args.export}"
            
            try:
                if args.export == 'json':
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
                print(f"Batch results exported to: {filename}")
            except Exception as e:
                print(f"Export failed: {e}")
        return
        
    if not args.target:
        parser.print_help()
        return
    
    # Check if user wants persistent mode after single analysis
    if args.persistent:
        # Analyze the provided hash first, then enter persistent mode
        if not args.quiet:
            print_banner()
        print(f"\nAnalyzing provided hash: {args.target[:50]}{'...' if len(args.target) > 50 else ''}")
        print("="*60)
        
        analyzer = HashTokenAnalyzer(args.target, verbose=not args.quiet)
        if args.quick:
            analyzer.identify_hash_formats()
            analyzer._calculate_entropy()
            if 'JWT' in ' '.join(analyzer.results['detected_formats']):
                analyzer.results['token_analysis']['jwt'] = analyzer.analyze_jwt_token()
        else:
            analyzer.comprehensive_analysis()
        
        print("\nEntering persistent mode for additional analyses...")
        time.sleep(1)
        persistent_mode(quick_mode=args.quick, verbose=not args.quiet)
        return
        
    # Single analysis mode
    if not args.quiet:
        print_banner()
    else:
        print(f"Hash/Token Analyzer v2.0 - Target: {args.target[:50]}{'...' if len(args.target) > 50 else ''}")
    
    analyzer = HashTokenAnalyzer(args.target, verbose=not args.quiet)
    
    if args.quick:
        analyzer._print("Quick analysis mode - skipping intensive operations", "INFO")
        analyzer.identify_hash_formats()
        analyzer._calculate_entropy()
        analyzer._character_frequency_analysis()
        analyzer.results['encoding_analysis'] = analyzer.comprehensive_encoding_analysis()
        if 'JWT' in ' '.join(analyzer.results['detected_formats']):
            analyzer.results['token_analysis']['jwt'] = analyzer.analyze_jwt_token()
    else:
        analyzer.comprehensive_analysis()
    
    if args.export:
        filename = analyzer.export_results(args.export, args.output)
        
    if not args.quiet:
        print("\nAnalysis complete! Use --export to save detailed results.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        logging.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)