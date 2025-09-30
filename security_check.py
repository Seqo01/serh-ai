#!/usr/bin/env python3
"""
Security check script to ensure no sensitive data is committed
"""
import os
import re

def check_for_secrets():
    """Check for potential secrets in the codebase"""
    
    print("Security Check...")
    print("=" * 20)
    
    # Files to check
    files_to_check = [
        'config.py',
        'recall_api.py',
        'portfolio_manager.py',
        'trading_agent.py',
        'trading_strategy.py'
    ]
    
    # Patterns that might indicate secrets
    secret_patterns = [
        r'pk_live_[a-zA-Z0-9_]{20,}',  # Live API keys (actual keys, not variable names)
        r'pk_test_[a-zA-Z0-9_]{20,}',  # Test API keys (actual keys, not variable names)
        r'["\'][a-zA-Z0-9_]{20,}["\']',  # Long strings in quotes that might be keys
        r'api[_-]?key["\']?\s*[:=]\s*["\'][a-zA-Z0-9_]{20,}["\']',  # API key assignments with actual keys
    ]
    
    # Patterns to ignore (false positives)
    ignore_patterns = [
        r'os\.getenv\(',  # Environment variable calls
        r'def\s+\w+',     # Function definitions
        r'class\s+\w+',   # Class definitions
        r'#.*',           # Comments
        r'0x[a-fA-F0-9]+', # Token addresses (these are public)
    ]
    
    issues_found = False
    
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            continue
            
        print(f"\nChecking {file_path}...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for i, line in enumerate(content.split('\n'), 1):
                # Skip lines that match ignore patterns
                should_ignore = False
                for ignore_pattern in ignore_patterns:
                    if re.search(ignore_pattern, line, re.IGNORECASE):
                        should_ignore = True
                        break
                
                if should_ignore:
                    continue
                
                # Check for secret patterns
                for pattern in secret_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        print(f"  WARNING: Line {i}: Potential secret found")
                        print(f"     {line.strip()}")
                        issues_found = True
                        break
                        
        except Exception as e:
            print(f"  ERROR: Error reading {file_path}: {e}")
    
    # Check for .env file
    print(f"\nChecking for .env file...")
    if os.path.exists('.env'):
        print("  WARNING: .env file exists - make sure it's in .gitignore")
    else:
        print("  OK: No .env file found")
    
    # Check .gitignore
    print(f"\nChecking .gitignore...")
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
        
        if '.env' in gitignore_content:
            print("  OK: .env is in .gitignore")
        else:
            print("  ERROR: .env is NOT in .gitignore!")
            issues_found = True
    else:
        print("  ERROR: No .gitignore file found!")
        issues_found = True
    
    print("\n" + "=" * 50)
    if issues_found:
        print("ERROR: Security issues found! Please review before committing.")
    else:
        print("SUCCESS: Security check passed! Safe to commit.")
    
    return not issues_found

if __name__ == "__main__":
    check_for_secrets()
