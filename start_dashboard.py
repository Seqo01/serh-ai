#!/usr/bin/env python3
"""
Dashboard Starter Script
"""
import os
import sys
import subprocess

def check_requirements():
    """Check if required packages are installed"""
    required_packages = ['flask', 'flask-cors']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstalling missing packages...")
        
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("Packages installed successfully!")
        except subprocess.CalledProcessError:
            print("Failed to install packages. Please install manually:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
    
    return True

def start_dashboard():
    """Start the dashboard"""
    print("Starting Trading Dashboard...")
    print("=" * 40)
    
    if not check_requirements():
        return
    
    print("Dashboard will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the dashboard")
    print("=" * 40)
    
    try:
        from dashboard import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
    except Exception as e:
        print(f"Error starting dashboard: {e}")

if __name__ == "__main__":
    start_dashboard()
