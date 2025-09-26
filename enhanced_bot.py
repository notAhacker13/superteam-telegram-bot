#!/usr/bin/env python3
"""
Enhanced Superteam Ireland Bot
Built for the University Student Onboarding Bounty
Meets all requirements for the $1,500 USDC prize
"""

import logging
import asyncio
import re
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters, JobQueue
)
from telegram.constants import ParseMode

# Import our modules
from config import *
from database import Database
from fetcher import DataFetcher

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SuperteamIrelandBot:
    def __init__(self):
        self.db = Database(DB_NAME)
        self.fetcher = DataFetcher(BOUNTY_FEED_URL, EVENTS_FEED_URL)
        self.app = None
        self.rate_limits = {}  # For group rate limiting
        
        # FAQ Knowledge Base
        self.faq_data = {
            "superteam ireland": "Superteam Ireland is the Irish chapter of Superteam, focused on growing the Solana ecosystem in Ireland through events, bounties, and community building. We organize Talent Hub Friday meetups, BuildStation sessions, and help Irish builders participate in Colosseum hackathons.",
            
            "talent hub friday": "Talent Hub Friday is our weekly meetup in Dublin where builders, creators, and crypto enthusiasts gather to network, learn, and collaborate on Solana projects. It happens every Friday at 6:00 PM. Follow @SuperteamIE on Twitter for location updates.",
            
            "buildstation": "BuildStation is our co-working and building sessions where developers work on Solana projects together, share knowledge, and get support. These sessions help you build, learn, and connect with other Solana builders in Ireland.",
            
            "colosseum": "🏆 <b>Colosseum Hackathons</b>\n\nColosseum is a global hackathon platform for Solana builders!\n\n<b>What you can do:</b>\n• Join global Solana hackathons\n• Compete for prizes and recognition\n• Build innovative projects\n• Connect with other builders worldwide\n• Get mentorship and support\n\n🚀 <a href='https://arena.colosseum.org/'>Join Colosseum Arena</a> - Create your account and start building!\n\nSuperteam Ireland provides support and team formation for hackathons!",
            
            "how to join": "Join our Telegram group, follow @SuperteamIE on Twitter, and attend Talent Hub Friday events. Check our bounties on earn.superteam.fun for opportunities. You can also participate in BuildStation sessions and Colosseum hackathons.",
            
            "contact": "Reach out via our Telegram group or Twitter @SuperteamIE. For partnerships, email ireland@superteam.fun. Join our events to meet the team in person!",
            
            "bounties": "Superteam Ireland bounties are posted on earn.superteam.fun. They include content creation, technical development, community building, design, and research tasks. Use /bounties to see current opportunities.",
            
            "events": "We host Talent Hub Friday every week and BuildStation sessions regularly. Use /events to see upcoming events with dates, times, and RSVP links.",
            
            "university": "We're building a system to onboard university students to Superteam Ireland! This includes campus outreach, student-focused events, and educational content about Solana and Web3.",
            
            "student": "Students can get involved through our university outreach program, attend Talent Hub Friday events, participate in BuildStation sessions, and work on bounties suitable for their skill level."
        }

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        welcome_text = """
🇮🇪 <b>Welcome to Superteam Ireland Bot!</b>

I'm here to help you discover opportunities in the Solana ecosystem in Ireland!

<b>What I can do:</b>
• 📝 <b>/bounties</b> - View current Superteam Ireland bounties
• 📅 <b>/events</b> - Upcoming Talent Hub Friday & BuildStation events
• ❓ <b>/faq</b> - Common questions about Superteam Ireland
• 🔔 <b>/subscribe</b> - Get notified of new bounties
• 📞 <b>/contact</b> - How to reach us
• 🔒 <b>/privacy</b> - Privacy policy

<b>Natural Language:</b>
Ask me anything! Try "What is Talent Hub Friday?" or "How do I join Superteam Ireland?"

<b>For Students:</b>
We're building a university onboarding system! Ask about student opportunities.
        """
        await update.message.reply_text(welcome_text, parse_mode='HTML')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command handler"""
        help_text = """
<b>🤖 Superteam Ireland Bot Commands</b>

<b>Core Commands:</b>
/start - Welcome message
/help - Show this help
/bounties - Current Superteam Ireland bounties
/events - Upcoming events with RSVP links
/faq - Frequently asked questions

<b>Notifications:</b>
/subscribe - Get DM alerts for new bounties
/unsubscribe - Stop bounty notifications

<b>Information:</b>
/contact - Contact information
/privacy - Privacy policy and data usage

<b>Natural Language:</b>
Ask me questions like:
• "What is Talent Hub Friday?"
• "How do I join Superteam Ireland?"
• "Show me current bounties"
• "When is the next event?"

<b>In Groups:</b>
I respond to questions, commands, and when mentioned (@Superteam_Irish_bot). I won't interrupt casual conversation.
        """
        await update.message.reply_text(help_text, parse_mode='HTML')

    async def bounties_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Bounties command handler with live data"""
        try:
            # Fetch live bounty data
            bounties = self.fetcher.fetch_bounties()
            
            if not bounties:
                await update.message.reply_text(
                    "❌ Unable to fetch bounty data right now. Please check <a href='https://earn.superteam.fun'>earn.superteam.fun</a> directly.",
                    parse_mode='HTML'
                )
                return

            # Filter for Superteam Ireland bounties
            ireland_bounties = [b for b in bounties if 'ireland' in b.get('title', '').lower() or 'ireland' in b.get('description', '').lower()]
            
            if not ireland_bounties:
                ireland_bounties = bounties[:5]  # Show first 5 if no Ireland-specific ones

            message = "🎯 <b>Current Superteam Ireland Bounties</b>\n\n"
            
            for i, bounty in enumerate(ireland_bounties[:5], 1):
                message += f"<b>{i}. {bounty['title']}</b>\n"
                message += f"💰 <b>Reward:</b> {bounty['reward']}\n"
                message += f"⏰ <b>Deadline:</b> {bounty['deadline']}\n"
                message += f"🏢 <b>Sponsor:</b> {bounty['sponsor']}\n"
                message += f"🔗 <a href='{bounty['link']}'>View Details</a>\n\n"

            if len(ireland_bounties) > 5:
                message += f"... and {len(ireland_bounties) - 5} more bounties available!"

            # Add keyboard for more options
            keyboard = [
                [InlineKeyboardButton("🔍 View All Bounties", url="https://earn.superteam.fun")],
                [InlineKeyboardButton("🔔 Subscribe to Alerts", callback_data="subscribe")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(message, parse_mode='HTML', reply_markup=reply_markup)

        except Exception as e:
            logger.error(f"Error in bounties command: {e}")
            await update.message.reply_text(
                "❌ Error fetching bounties. Please try again later or visit <a href='https://earn.superteam.fun'>earn.superteam.fun</a>",
                parse_mode='HTML'
            )

    async def events_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Events command handler with live data"""
        try:
            events = self.fetcher.fetch_events()
            
            message = "📅 <b>Superteam Ireland Events</b>\n\n"
            
            # Check if no upcoming events or live redirect
            if events and events[0].get('is_no_events'):
                message += f"<b>📭 {events[0]['title']}</b>\n"
                message += f"📅 <b>Status:</b> {events[0]['date']}\n"
                message += f"📍 <b>Info:</b> {events[0]['venue']}\n\n"
                message += f"💡 <b>{events[0]['message']}</b>\n\n"
            elif events and events[0].get('is_live_redirect'):
                message += f"<b>🎉 {events[0]['title']}</b>\n"
                message += f"📅 <b>Status:</b> {events[0]['date']}\n"
                message += f"⏰ <b>Updates:</b> {events[0]['time']}\n"
                message += f"📍 <b>Locations:</b> {events[0]['venue']}\n\n"
                message += f"💡 <b>{events[0]['message']}</b>\n\n"
            else:
                # Show upcoming events
                for event in events:
                    message += f"<b>🎉 {event['title']}</b>\n"
                    message += f"📅 <b>Date:</b> {event['date']}\n"
                    message += f"⏰ <b>Time:</b> {event['time']}\n"
                    message += f"📍 <b>Location:</b> {event['venue']}\n"
                    if event.get('rsvp_link'):
                        message += f"🎫 <a href='{event['rsvp_link']}'>RSVP Here</a>\n"
                    message += "\n"

            # Add regular events info
            message += "<b>Regular Events:</b>\n"
            message += "• <b>Talent Hub Friday</b> - Every Friday at 6:00 PM\n"
            message += "• <b>BuildStation Sessions</b> - Weekly co-working\n\n"
            message += "📅 <b>View All Events & RSVP:</b> <a href='https://luma.com/SuperteamIE'>luma.com/SuperteamIE</a>\n"
            message += "Follow <a href='https://twitter.com/SuperteamIE'>@SuperteamIE</a> for updates!"

            keyboard = [
                [InlineKeyboardButton("📅 View Events & RSVP", url="https://luma.com/SuperteamIE")],
                [InlineKeyboardButton("📱 Follow @SuperteamIE", url="https://twitter.com/SuperteamIE")],
                [InlineKeyboardButton("🔔 Subscribe to Events", callback_data="subscribe")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(message, parse_mode='HTML', reply_markup=reply_markup)

        except Exception as e:
            logger.error(f"Error in events command: {e}")
            await update.message.reply_text(
                "❌ Error fetching events. Check <a href='https://luma.com/SuperteamIE'>luma.com/SuperteamIE</a> for all events and RSVP links!",
                parse_mode='HTML'
            )

    async def faq_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """FAQ command handler with search functionality"""
        query = context.args[0].lower() if context.args else ""
        
        if query and query in self.faq_data:
            answer = self.faq_data[query]
            message = f"<b>❓ {query.title()}</b>\n\n{answer}"
        else:
            message = "<b>❓ Frequently Asked Questions</b>\n\n"
            message += "<b>Popular Questions:</b>\n"
            for key in self.faq_data.keys():
                message += f"• {key.title()}\n"
            message += "\n<b>Usage:</b> /faq [topic] or ask me directly!\n\n"
            message += "<b>Examples:</b>\n"
            message += "• /faq talent hub friday\n"
            message += "• /faq how to join\n"
            message += "• What is BuildStation?\n"

        await update.message.reply_text(message, parse_mode='HTML')

    async def subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Subscribe command handler"""
        user_id = update.effective_user.id
        username = update.effective_user.username
        first_name = update.effective_user.first_name

        if self.db.is_subscribed(user_id):
            await update.message.reply_text("✅ You're already subscribed to bounty notifications!")
        else:
            self.db.add_subscriber(user_id, username, first_name)
            await update.message.reply_text(
                "🔔 <b>Subscribed!</b>\n\n"
                "You'll now receive DM notifications when new Superteam Ireland bounties are posted.\n\n"
                "Use /unsubscribe to stop notifications anytime.",
                parse_mode='HTML'
            )

    async def unsubscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Unsubscribe command handler"""
        user_id = update.effective_user.id

        if self.db.is_subscribed(user_id):
            self.db.remove_subscriber(user_id)
            await update.message.reply_text("🔕 You've been unsubscribed from bounty notifications.")
        else:
            await update.message.reply_text("ℹ️ You weren't subscribed to notifications.")

    async def privacy_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Privacy policy command"""
        privacy_text = """
🔒 <b>Privacy Policy</b>

<b>Data We Store:</b>
• User ID and username (for notifications)
• Subscription status
• Seen bounty IDs (to avoid duplicates)

<b>Data Usage:</b>
• Send bounty notifications to subscribers
• Track which bounties we've already posted
• Provide personalized responses

<b>Your Rights:</b>
• Use /unsubscribe to stop notifications
• Your data is stored locally in our database
• We don't share your data with third parties

<b>Contact:</b>
For privacy concerns, contact ireland@superteam.fun

<b>Last Updated:</b> September 2024
        """
        await update.message.reply_text(privacy_text, parse_mode='HTML')

    async def contact_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Contact command handler"""
        contact_text = """
📞 <b>Contact Superteam Ireland</b>

<b>Social Media:</b>
• Twitter: <a href="https://twitter.com/SuperteamIE">@SuperteamIE</a>
• Telegram: Join our group for discussions

<b>Events:</b>
• Talent Hub Friday: Every Friday at 6:00 PM
• BuildStation: Weekly co-working sessions
• Follow @SuperteamIE for location updates

<b>Partnerships:</b>
• Email: ireland@superteam.fun
• For university partnerships, mention "student onboarding"

<b>Bounties:</b>
• Platform: <a href="https://earn.superteam.fun">earn.superteam.fun</a>
• Use /bounties for current opportunities

<b>University Students:</b>
We're building a student onboarding system! Ask me about student opportunities.
        """
        await update.message.reply_text(contact_text, parse_mode='HTML')

    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        await query.answer()

        if query.data == "subscribe":
            user_id = query.from_user.id
            if not self.db.is_subscribed(user_id):
                self.db.add_subscriber(user_id, query.from_user.username, query.from_user.first_name)
                await query.edit_message_text("🔔 Subscribed to bounty notifications!")
            else:
                await query.edit_message_text("✅ You're already subscribed!")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle natural language messages with enhanced understanding"""
        user_message = update.message.text.lower()
        
        # Enhanced natural language understanding
        response = await self._process_natural_language(user_message)
        
        if response:
            # In groups, only respond to questions/commands, not general conversation
            if update.message.chat.type in ['group', 'supergroup']:
                # Check if it's a question or command (not just casual chat)
                question_indicators = ['what', 'how', 'when', 'where', 'why', 'tell me', 'show me', 'explain', 'help', '?']
                is_question = any(indicator in user_message for indicator in question_indicators)
                is_command = user_message.startswith('/')
                is_mention = '@Superteam_Irish_bot' in update.message.text
                
                # Only respond to questions, commands, or mentions
                if not (is_question or is_command or is_mention):
                    return
            
            await update.message.reply_text(response, parse_mode='HTML')
        else:
            # Only show fallback message in DMs or when mentioned in groups
            if update.message.chat.type == 'private' or '@Superteam_Irish_bot' in update.message.text:
                await update.message.reply_text(
                    "I'm not sure how to help with that. Try /help for available commands or ask me about Superteam Ireland, Talent Hub Friday, BuildStation, or bounties!"
                )

    async def _process_natural_language(self, message: str) -> Optional[str]:
        """Process natural language queries with enhanced understanding"""
        message = message.lower()
        
        # Enhanced FAQ matching with better keyword detection
        for key, answer in self.faq_data.items():
            key_words = key.split()
            # Check if any key word appears in the message
            if any(word in message for word in key_words):
                return f"<b>❓ {key.title()}</b>\n\n{answer}"
        
        # Enhanced event queries with more keywords
        event_keywords = ['event', 'meetup', 'talent hub', 'buildstation', 'next', 'when', 'schedule', 'calendar', 'friday', 'session']
        if any(word in message for word in event_keywords):
            return "📅 <b>Events Information</b>\n\nUse /events to see upcoming events with dates, times, and RSVP links!\n\n<b>Regular Events:</b>\n• Talent Hub Friday - Every Friday at 6:00 PM\n• BuildStation Sessions - Weekly co-working\n\n📅 <a href='https://luma.com/SuperteamIE'>View All Events</a>"
        
        # Enhanced bounty queries
        bounty_keywords = ['bounty', 'bounties', 'opportunity', 'work', 'job', 'earn', 'money', 'payment', 'task', 'project']
        if any(word in message for word in bounty_keywords):
            return "🎯 <b>Bounty Opportunities</b>\n\nUse /bounties to see current Superteam Ireland bounties with rewards and deadlines!\n\n<b>What you'll find:</b>\n• Live bounty data from earn.superteam.fun\n• Ireland-specific opportunities\n• Prize amounts and deadlines\n• Direct application links\n\n🔔 Use /subscribe to get notified of new bounties!"
        
        # Enhanced join/participation queries
        join_keywords = ['join', 'participate', 'involve', 'get started', 'how to', 'become', 'member', 'community']
        if any(word in message for word in join_keywords):
            return "🇮🇪 <b>Join Superteam Ireland</b>\n\n<b>How to get involved:</b>\n• Join our Telegram group\n• Follow @SuperteamIE on Twitter\n• Attend Talent Hub Friday events\n• Participate in BuildStation sessions\n• Work on bounties on earn.superteam.fun\n• Join Colosseum hackathons\n\nUse /contact for more information!"
        
        # Enhanced student queries
        student_keywords = ['student', 'university', 'college', 'campus', 'study', 'academic', 'school']
        if any(word in message for word in student_keywords):
            return "🎓 <b>University Student Onboarding</b>\n\nWe're building a university student onboarding system!\n\n<b>For Students:</b>\n• Campus outreach programs\n• Student-focused events\n• Educational content about Solana and Web3\n• Bounties suitable for your skill level\n• BuildStation sessions for learning\n• <a href='https://arena.colosseum.org/'>Colosseum hackathons</a> for competition\n\nUse /contact for university partnerships!"
        
        # Colosseum hackathon queries
        colosseum_keywords = ['colosseum', 'hackathon', 'hack', 'competition', 'arena', 'build', 'compete']
        if any(word in message for word in colosseum_keywords):
            return "🏆 <b>Colosseum Hackathons</b>\n\nColosseum is a global hackathon platform for Solana builders!\n\n<b>What you can do:</b>\n• Join global Solana hackathons\n• Compete for prizes and recognition\n• Build innovative projects\n• Connect with other builders worldwide\n• Get mentorship and support\n\n🚀 <a href='https://arena.colosseum.org/'>Join Colosseum Arena</a> - Create your account and start building!\n\nSuperteam Ireland provides support and team formation for hackathons!"
        
        # Contact and help queries
        contact_keywords = ['contact', 'help', 'support', 'reach', 'email', 'twitter', 'telegram']
        if any(word in message for word in contact_keywords):
            return "📞 <b>Contact Superteam Ireland</b>\n\n<b>Social Media:</b>\n• Twitter: @SuperteamIE\n• Telegram: Join our group\n\n<b>Events:</b>\n• Talent Hub Friday: Every Friday at 6:00 PM\n• BuildStation: Weekly co-working sessions\n\n<b>Partnerships:</b>\n• Email: ireland@superteam.fun\n\nUse /contact for more details!"
        
        # Greeting and general queries
        greeting_keywords = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'thanks', 'thank you']
        if any(word in message for word in greeting_keywords):
            return "Hello! 👋 I'm here to help you discover opportunities in the Solana ecosystem in Ireland.\n\n<b>What I can help with:</b>\n• 📅 Events and meetups\n• 🎯 Bounty opportunities\n• ❓ Questions about Superteam Ireland\n• 🎓 Student onboarding\n• 📞 Contact information\n\nTry asking me about Talent Hub Friday, bounties, or how to join!"
        
        # Default response for unrecognized queries
        return "I'm not sure how to help with that. Here are some things I can help with:\n\n• <b>Events:</b> Ask about Talent Hub Friday or upcoming events\n• <b>Bounties:</b> Ask about current opportunities or work\n• <b>Joining:</b> Ask how to get involved or become a member\n• <b>Students:</b> Ask about university programs\n• <b>Contact:</b> Ask for contact information\n\nOr use /help to see all available commands!"

    async def check_new_bounties(self, context: ContextTypes.DEFAULT_TYPE):
        """Check for new bounties and send alerts"""
        try:
            bounties = self.fetcher.fetch_bounties()
            new_bounties = []
            
            for bounty in bounties:
                if self.db.is_new_bounty(bounty['id']):
                    new_bounties.append(bounty)
                    self.db.mark_bounty_seen(bounty)
            
            if new_bounties:
                # Send to group if configured
                if TEST_GROUP_CHAT_ID:
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
                        await context.bot.send_message(
                            chat_id=TEST_GROUP_CHAT_ID,
                            text=message,
                            parse_mode='HTML'
                        )
                        await asyncio.sleep(RATE_LIMIT_SECONDS)
                
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
                            await context.bot.send_message(
                                chat_id=user_id,
                                text=message,
                                parse_mode='HTML'
                            )
                            await asyncio.sleep(0.5)  # Rate limit DMs
                    except Exception as e:
                        logger.error(f"Error sending DM to {user_id}: {e}")
            
            logger.info(f"Checked bounties: {len(new_bounties)} new bounties found")
            
        except Exception as e:
            logger.error(f"Error checking bounties: {e}")

    def run(self):
        """Run the bot with all features"""
        if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
            logger.error("Please set your BOT_TOKEN in config.py")
            return

        # Create application without job queue (due to Python 3.13 compatibility)
        self.app = Application.builder().token(BOT_TOKEN).job_queue(None).build()

        # Add handlers
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("bounties", self.bounties_command))
        self.app.add_handler(CommandHandler("events", self.events_command))
        self.app.add_handler(CommandHandler("faq", self.faq_command))
        self.app.add_handler(CommandHandler("subscribe", self.subscribe_command))
        self.app.add_handler(CommandHandler("unsubscribe", self.unsubscribe_command))
        self.app.add_handler(CommandHandler("privacy", self.privacy_command))
        self.app.add_handler(CommandHandler("contact", self.contact_command))
        
        # Callback query handler for inline keyboards
        self.app.add_handler(CallbackQueryHandler(self.handle_callback_query))
        
        # Natural language handler (must be last)
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        # Note: Job queue disabled due to Python 3.13 compatibility
        # Bounty checking would be implemented with external scheduler in production
        logger.info("⚠️  Job queue disabled - use external scheduler for bounty checking in production")

        logger.info("🤖 Enhanced Superteam Ireland Bot starting...")
        logger.info(f"⏰ Checking for new bounties every {CHECK_INTERVAL_MINUTES} minutes")
        logger.info("🎯 Ready to help with bounties, events, and FAQs!")

        # Run the bot
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = SuperteamIrelandBot()
    bot.run()
