#!/usr/bin/env python3
"""
External Scheduler for Superteam Ireland Bot
Handles bounty checking and notifications when job queue is disabled
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from config import CHECK_INTERVAL_MINUTES
from database import Database
from fetcher import DataFetcher
from telegram import Bot

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class BountyScheduler:
    def __init__(self, bot_token: str, group_chat_id: str = None):
        self.bot_token = bot_token
        self.group_chat_id = group_chat_id
        self.db = Database("superteam_bot.db")
        self.fetcher = DataFetcher(
            "https://earn.superteam.fun/api/search/ireland?bountiesLimit=50&grantsLimit=10&userRegion=Ireland%2CGlobal%2CIreland+%28NI+and+ROI%29",
            "https://luma.com/SuperteamIE?k=c&period=past"
        )
        self.bot = Bot(token=bot_token)

    async def check_and_notify_bounties(self):
        """Check for new bounties and send notifications"""
        try:
            logger.info("🔍 Checking for new bounties...")
            bounties = self.fetcher.fetch_bounties()
            new_bounties = []
            
            for bounty in bounties:
                if self.db.is_new_bounty(bounty['id']):
                    new_bounties.append(bounty)
                    self.db.mark_bounty_seen(bounty)
            
            if new_bounties:
                logger.info(f"🎯 Found {len(new_bounties)} new bounties!")
                
                # Send to group if configured
                if self.group_chat_id:
                    for bounty in new_bounties:
                        message = f"""
🎯 <b>New Superteam Ireland Bounty!</b>

<b>{bounty['title']}</b>
💰 <b>Reward:</b> {bounty['reward']}
⏰ <b>Deadline:</b> {bounty['deadline']}
🏢 <b>Sponsor:</b> {bounty['sponsor']}

{bounty['description'][:200]}...

🔗 <a href="{bounty['link']}">Apply Now</a>
                        """
                        await self.bot.send_message(
                            chat_id=self.group_chat_id,
                            text=message,
                            parse_mode='HTML'
                        )
                        await asyncio.sleep(2)  # Rate limiting
                
                # Send DMs to subscribers
                subscribers = self.db.get_active_subscribers()
                for user_id in subscribers:
                    try:
                        for bounty in new_bounties:
                            message = f"""
🔔 <b>New Bounty Alert!</b>

<b>{bounty['title']}</b>
💰 <b>Reward:</b> {bounty['reward']}
⏰ <b>Deadline:</b> {bounty['deadline']}

🔗 <a href="{bounty['link']}">View Details</a>
                            """
                            await self.bot.send_message(
                                chat_id=user_id,
                                text=message,
                                parse_mode='HTML'
                            )
                            await asyncio.sleep(0.5)  # Rate limit DMs
                    except Exception as e:
                        logger.error(f"Error sending DM to {user_id}: {e}")
            else:
                logger.info("ℹ️  No new bounties found")
            
        except Exception as e:
            logger.error(f"Error checking bounties: {e}")

    async def run_scheduler(self):
        """Run the scheduler continuously"""
        logger.info(f"⏰ Starting bounty scheduler (checking every {CHECK_INTERVAL_MINUTES} minutes)")
        
        while True:
            try:
                await self.check_and_notify_bounties()
                await asyncio.sleep(CHECK_INTERVAL_MINUTES * 60)  # Convert to seconds
            except KeyboardInterrupt:
                logger.info("Scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    # Set your bot token and group chat ID here
    BOT_TOKEN = "8396305925:AAEKoV3KJFIwlzgC_DT0xzxR8g8ejLg7hhI"
    GROUP_CHAT_ID = None  # Set this to your test group ID (e.g., -1001234567890)
    
    # You can also import from config
    try:
        from config import TEST_GROUP_CHAT_ID
        if TEST_GROUP_CHAT_ID:
            GROUP_CHAT_ID = TEST_GROUP_CHAT_ID
            print(f"Using group chat ID from config: {GROUP_CHAT_ID}")
    except ImportError:
        pass
    
    if not GROUP_CHAT_ID:
        print("⚠️  Please set GROUP_CHAT_ID in this file or config.py")
        print("   Run 'python get_group_id.py' to get your group ID")
        exit(1)
    
    scheduler = BountyScheduler(BOT_TOKEN, GROUP_CHAT_ID)
    asyncio.run(scheduler.run_scheduler())
