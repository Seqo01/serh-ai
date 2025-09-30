#!/usr/bin/env python3
"""
Setup script for Recall Trading Agent
"""
import os
import shutil

def setup_environment():
    """Setup environment file"""
    
    print("Project Setup")
    print("=" * 20)
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("WARNING: .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if response != 'y':
            print("Setup cancelled.")
            return
    
    # Copy env.example to .env
    if os.path.exists('env.example'):
        shutil.copy('env.example', '.env')
        print("SUCCESS: Created .env file from template")
    else:
        print("ERROR: env.example file not found!")
        return
    
    print("\nNext steps:")
    print("1. Edit .env file and add your API keys")
    print("2. Run: python trading_agent.py")
    
    print("\nIMPORTANT:")
    print("- Keep your API keys secure")

if __name__ == "__main__":
    setup_environment()
