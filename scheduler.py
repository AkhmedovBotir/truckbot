import asyncio
from datetime import datetime, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot
from telegram.constants import ParseMode

from database import db
from currency_api import currency_api
from config import BOT_TOKEN

class CurrencyScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.bot = Bot(token=BOT_TOKEN)

    async def send_currency_update(self):
        """Send daily currency update to configured channels"""
        try:
            settings = await db.get_settings()
            currency_code = settings.get('currency', 'USD')
            template = settings.get('template', '')
            channels = settings.get('channels', '').split(',')
            
            # Get currency data
            currency_data = await currency_api.get_currency_by_code(currency_code)
            
            if not currency_data:
                print(f"Failed to fetch currency data for {currency_code}")
                return
            
            # Format message
            message = currency_api.format_currency_info(currency_data, template)
            
            # Send to all configured channels
            for channel in channels:
                channel = channel.strip()
                if channel:
                    try:
                        await self.bot.send_message(
                            chat_id=channel,
                            text=message,
                            parse_mode=ParseMode.MARKDOWN
                        )
                        print(f"Currency update sent to {channel}")
                    except Exception as e:
                        print(f"Failed to send to {channel}: {e}")
                        
        except Exception as e:
            print(f"Error in send_currency_update: {e}")

    async def update_schedule(self):
        """Update the scheduled job based on current settings"""
        try:
            # Remove existing job
            if self.scheduler.get_job('currency_update'):
                self.scheduler.remove_job('currency_update')
            
            # Get current settings
            settings = await db.get_settings()
            send_time = settings.get('send_time', '09:00')
            
            # Parse time
            hour, minute = map(int, send_time.split(':'))
            
            # Add new job
            self.scheduler.add_job(
                self.send_currency_update,
                CronTrigger(hour=hour, minute=minute),
                id='currency_update',
                replace_existing=True
            )
            
            print(f"Currency update scheduled for {send_time} daily")
            
        except Exception as e:
            print(f"Error updating schedule: {e}")

    def start(self):
        """Start the scheduler"""
        self.scheduler.start()
        print("Scheduler started")

    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        print("Scheduler stopped")

# Global scheduler instance
scheduler = CurrencyScheduler()