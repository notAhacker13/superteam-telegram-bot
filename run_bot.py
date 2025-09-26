#!/usr/bin/env python3
"""
Superteam Ireland Bot Runner
Simple script to start the enhanced bot
"""

import sys
import logging
from enhanced_bot import SuperteamIrelandBot

def main():
    """Main entry point"""
    try:
        print("🤖 Starting Superteam Ireland Bot...")
        print("📋 Bot Handle: @Superteam_Irish_bot")
        print("🎯 Features: Bounties, Events, FAQ, Notifications")
        print("🇮🇪 Built for University Student Onboarding")
        print("-" * 50)
        
        bot = SuperteamIrelandBot()
        bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
