#!/usr/bin/env python3
"""
Setup script for Superteam Ireland Bot
"""

import subprocess
import sys
import os

def main():
    """Setup the bot environment"""
    print("🚀 Setting up Superteam Ireland Bot...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Install requirements
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        sys.exit(1)
    
    # Check if config is set up
    try:
        from config import BOT_TOKEN
        if BOT_TOKEN and BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
            print("✅ Bot token configured")
        else:
            print("⚠️  Please set your BOT_TOKEN in config.py")
    except ImportError:
        print("❌ config.py not found")
        sys.exit(1)
    
    print("\n🎉 Setup complete!")
    print("📋 To run the bot: python run_bot.py")
    print("📋 To run scheduler: python scheduler.py")
    print("📋 Bot handle: @Superteam_Irish_bot")

if __name__ == "__main__":
    main()
