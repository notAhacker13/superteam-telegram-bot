"""Data fetcher for bounties and events"""

import requests
import logging
from datetime import datetime
from typing import List, Dict
import re
from html import unescape

logger = logging.getLogger(__name__)

class DataFetcher:
    def __init__(self, bounty_url: str, events_url: str = None):
        self.bounty_url = bounty_url
        self.events_url = events_url

    def fetch_bounties(self) -> List[Dict]:
        """Fetch current bounties from Superteam Earn API with enhanced filtering"""
        try:
            response = requests.get(self.bounty_url, timeout=15)
            response.raise_for_status()
            data = response.json()

            bounties = []
            for item in data.get("results", []):
                if item.get("type") == "bounty" and item.get("status") == "OPEN":
                    # Clean description HTML
                    description = self._clean_html(item.get("description", ""))

                    # Format deadline
                    deadline_str = "No deadline"
                    if item.get("deadline"):
                        try:
                            deadline = datetime.fromisoformat(item["deadline"].replace("Z", "+00:00"))
                            deadline_str = deadline.strftime("%Y-%m-%d %H:%M UTC")
                        except:
                            deadline_str = item["deadline"]

                    # Get reward information
                    reward_amount = item.get('rewardAmount', 0)
                    reward_token = item.get('token', 'USDC')
                    if reward_amount and reward_amount > 0:
                        reward_str = f"{reward_amount} {reward_token}"
                    else:
                        reward_str = "TBD"

                    # Get sponsor information
                    sponsor_info = item.get("sponsor", {})
                    sponsor_name = sponsor_info.get("name", "Unknown")
                    
                    # Check if it's Superteam Ireland related
                    title_lower = item.get("title", "").lower()
                    desc_lower = description.lower()
                    is_ireland_related = (
                        "ireland" in title_lower or 
                        "ireland" in desc_lower or
                        "dublin" in title_lower or
                        "dublin" in desc_lower or
                        sponsor_name.lower() == "superteam ireland"
                    )

                    bounty = {
                        "id": str(item["id"]),
                        "title": item["title"],
                        "reward": reward_str,
                        "deadline": deadline_str,
                        "sponsor": sponsor_name,
                        "link": f"https://earn.superteam.fun/listing/{item['slug']}",
                        "description": description[:500] + "..." if len(description) > 500 else description,
                        "type": item.get("compensationType", "fixed"),
                        "is_featured": item.get("isFeatured", False),
                        "is_ireland_related": is_ireland_related,
                        "created_at": item.get("createdAt", ""),
                        "skills": item.get("skills", []),
                        "difficulty": item.get("difficulty", "Unknown")
                    }
                    bounties.append(bounty)

            # Sort by Ireland relevance and featured status
            bounties.sort(key=lambda x: (x["is_ireland_related"], x["is_featured"]), reverse=True)

            logger.info(f"Fetched {len(bounties)} bounties ({sum(1 for b in bounties if b['is_ireland_related'])} Ireland-related)")
            return bounties

        except Exception as e:
            logger.error(f"Error fetching bounties: {e}")
            return []

    def fetch_events(self) -> List[Dict]:
        """Fetch upcoming events from Luma (with fallback to default events)"""
        if not self.events_url:
            # Return default events if no URL provided
            return self._get_default_events()
        
        try:
            # Try to fetch from Luma page
            response = requests.get(self.events_url, timeout=10)
            response.raise_for_status()
            
            # Luma is a React SPA, so we can't easily scrape dynamic content
            # Instead, we'll check if the page loads successfully and provide helpful info
            if response.status_code == 200:
                # Check if page contains event-related content
                if any(keyword in response.text.lower() for keyword in ['event', 'calendar', 'talent hub', 'buildstation']):
                    logger.info("Luma page loaded successfully - directing users to check for events")
                    return self._get_luma_redirect_events()
                else:
                    logger.info("Luma page loaded but no event content detected")
                    return self._get_no_events_message()
            else:
                logger.warning(f"Luma page returned status {response.status_code}")
                return self._get_default_events()
                
        except Exception as e:
            logger.error(f"Error fetching events from Luma: {e}")
            return self._get_default_events()
    
    def _get_default_events(self) -> List[Dict]:
        """Get default events when external feed is unavailable"""
        return [
            {
                "title": "Talent Hub Friday",
                "date": "Every Friday",
                "time": "18:00",
                "venue": "Dublin (Location TBA)",
                "rsvp_link": "https://luma.com/SuperteamIE"
            },
            {
                "title": "BuildStation Session",
                "date": "Weekly",
                "time": "TBA",
                "venue": "Dublin (Location TBA)",
                "rsvp_link": "https://luma.com/SuperteamIE"
            },
            {
                "title": "University Student Meetup",
                "date": "Monthly",
                "time": "TBA",
                "venue": "Various Universities",
                "rsvp_link": "https://luma.com/SuperteamIE"
            }
        ]


    def _get_luma_redirect_events(self) -> List[Dict]:
        """Get events that direct users to Luma page for live data"""
        return [
            {
                "title": "Live Events Available",
                "date": "Check Luma Page",
                "time": "Real-time",
                "venue": "Various Locations",
                "rsvp_link": "https://luma.com/SuperteamIE",
                "is_live_redirect": True,
                "message": "🎉 Events are available on our Luma page! Click the link below to see all upcoming events with real-time updates, RSVP links, and detailed information."
            }
        ]

    def _get_no_events_message(self) -> List[Dict]:
        """Get message when no upcoming events are available"""
        return [
            {
                "title": "No Upcoming Events",
                "date": "Currently",
                "time": "N/A",
                "venue": "Check back soon!",
                "rsvp_link": "https://luma.com/SuperteamIE",
                "is_no_events": True,
                "message": "No upcoming events scheduled yet. Check our Luma page for past events and stay tuned for new announcements!"
            }
        ]

    def _clean_html(self, html_text: str) -> str:
        """Clean HTML tags from text"""
        if not html_text:
            return ""

        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', '', html_text)
        # Decode HTML entities
        clean = unescape(clean)
        # Clean up whitespace
        clean = re.sub(r'\s+', ' ', clean).strip()

        return clean
