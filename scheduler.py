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
        """Send daily currency update to all users and configured channels"""
        try:
            settings = await db.get_settings()
            selected_currencies = settings.get('selected_currencies', 'USD').split(',')
            selected_currencies = [curr.strip() for curr in selected_currencies if curr.strip()]
            channels = settings.get('channels', '').split(',')
            
            if not selected_currencies:
                print("No currencies selected for update")
                return
            
            # Get all users
            users = await db.get_all_users()
            
            # Collect all currency data
            currency_messages = []
            for currency_code in selected_currencies:
                currency_data = await currency_api.get_currency_by_code(currency_code)
                
                if not currency_data:
                    print(f"Failed to fetch currency data for {currency_code}")
                    continue
                
                # Format individual currency info with flag
                from handlers import format_currency_with_flag
                currency_info = format_currency_with_flag(currency_data)
                
                currency_messages.append(currency_info)
            
            if not currency_messages:
                print("No currency data available to send")
                return
            
            # Combine all currencies into one message
            message = f"""📊 **Valyuta kurslari yangilanishi**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{''.join(currency_messages)}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 **Sana:** {datetime.now().strftime('%d.%m.%Y')}
📊 **O'zbekiston Respublikasi Markaziy Banki**"""
            
            # Send to all users
            for user in users:
                try:
                    await self.bot.send_message(
                        chat_id=user['user_id'],
                        text=message,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    print(f"Currency update sent to user {user['user_id']}")
                except Exception as e:
                    print(f"Failed to send to user {user['user_id']}: {e}")
            
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
                        print(f"Currency update sent to channel {channel}")
                    except Exception as e:
                        print(f"Failed to send to channel {channel}: {e}")
                        
        except Exception as e:
            print(f"Error in send_currency_update: {e}")

    async def update_schedule(self):
        """Update the scheduled job based on current settings"""
        try:
            # Remove existing job
            if self.scheduler.get_job('currency_update'):
                self.scheduler.remove_job('currency_update')
                print("Removed existing currency update job")
            
            # Get current settings
            settings = await db.get_settings()
            send_time = settings.get('send_time', '09:00')
            print(f"Setting up schedule for time: {send_time}")
            
            # Parse time
            hour, minute = map(int, send_time.split(':'))
            print(f"Parsed time - Hour: {hour}, Minute: {minute}")
            
            # Add new job
            self.scheduler.add_job(
                self.send_currency_update,
                CronTrigger(hour=hour, minute=minute),
                id='currency_update',
                replace_existing=True
            )
            
            print(f"Currency update scheduled for {send_time} daily")
            
            # List all jobs to verify
            jobs = self.scheduler.get_jobs()
            print(f"Current jobs: {[job.id for job in jobs]}")
            
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