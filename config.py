"""Configuration settings for the Superteam Ireland Bot
Easily configurable without code changes for the bounty requirements"""

# Bot Configuration
BOT_TOKEN = "8396305925:AAEKoV3KJFIwlzgC_DT0xzxR8g8ejLg7hhI"
BOT_USERNAME = "@Superteam_Irish_bot"

# API Configuration - EASILY CONFIGURABLE
# Change these URLs without touching code to switch data sources
BOUNTY_FEED_URL = "https://earn.superteam.fun/api/search/ireland?bountiesLimit=50&grantsLimit=10&userRegion=Ireland%2CGlobal%2CIreland+%28NI+and+ROI%29"
EVENTS_FEED_URL = "https://luma.com/SuperteamIE?k=c"  # Luma events feed

# Scheduling Configuration - EASILY CONFIGURABLE
CHECK_INTERVAL_MINUTES = 30  # How often to check for new bounties (change this value)
RATE_LIMIT_SECONDS = 2  # Rate limiting for group messages

# Database Configuration
DB_NAME = "superteam_bot.db"

# Group Configuration
TEST_GROUP_CHAT_ID = -4910931565  # Your test group ID for bounty alerts
PRODUCTION_GROUP_CHAT_ID = None  # Set this for production group

# Bot Behavior
MAX_MESSAGE_LENGTH = 4000
BOUNTIES_PER_PAGE = 5

# University Student Onboarding Features
UNIVERSITY_MODE = True  # Enable student-focused features
CAMPUS_OUTREACH_ENABLED = True  # Enable campus outreach features

# Feed Configuration - Easy to change without code edits
FEED_CONFIG = {
    "bounty_url": BOUNTY_FEED_URL,
    "events_url": EVENTS_FEED_URL,
    "check_interval": CHECK_INTERVAL_MINUTES,
    "rate_limit": RATE_LIMIT_SECONDS
}

# Knowledge Base Configuration
FAQ_TOPICS = [
    "superteam ireland", "talent hub friday", "buildstation", "colosseum",
    "how to join", "contact", "bounties", "events", "university", "student"
]
