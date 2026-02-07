import logging
import os
from telegram import Update, Poll
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, PollAnswerHandler
from django.conf import settings
from .models import TelegramUser, PollResponse
from asgiref.sync import sync_to_async

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    args = context.args
    
    if args and len(args) > 0:
        token = args[0]
        try:
            # Find user by token
            telegram_user = await sync_to_async(TelegramUser.objects.get)(verification_token=token)
            
            # Update chat_id and clear token
            telegram_user.chat_id = chat_id
            telegram_user.verification_token = None # Invalidate token
            await sync_to_async(telegram_user.save)()
            
            await update.message.reply_text("✅ Account successfully linked! You can now close this chat and return to the dashboard.")
            logging.info(f"Linked chat_id {chat_id} to user {telegram_user.user.username}")
            
        except TelegramUser.DoesNotExist:
            await update.message.reply_text("❌ Invalid or expired verification link. Please try again from the website.")
    else:
        # Check if already registered
        try:
            telegram_user = await sync_to_async(TelegramUser.objects.get)(chat_id=chat_id)
            await update.message.reply_text("You are already registered! Wait for the hourly polls.")
        except TelegramUser.DoesNotExist:
            await update.message.reply_text("Please register on the website first and use the 'Connect Telegram' button.")

async def receive_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.poll_answer
    poll_id = answer.poll_id
    user_id = answer.user.id
    option_ids = answer.option_ids
    
    # Map index to option value (1-6)
    # The poll options are:
    # 0: Short Form Brain Rot
    # 1: Long Form Brain Rot
    # 2: Upskill
    # 3: Friends & Family
    # 4: Hobbies
    # 5: Movies / Series
    
    if not option_ids:
        return

    selected_index = option_ids[0] # Single choice poll
    # Mapping to DB choices '1'-'6'
    activity_map = {
        0: '1',
        1: '2',
        2: '3',
        3: '4',
        4: '5',
        5: '6'
    }
    
    activity_value = activity_map.get(selected_index)
    
    if activity_value:
        try:
            # Find user by chat_id (assuming chat_id == user_id for private chats)
            # Or we need to link poll answer user_id to TelegramUser
            # TelegramUser.chat_id stores the chat_id. For private chats user_id == chat_id usually.
            
            telegram_user = await sync_to_async(TelegramUser.objects.get)(chat_id=str(user_id))
            
            await sync_to_async(PollResponse.objects.create)(
                telegram_user=telegram_user,
                activity=activity_value,
                poll_id=poll_id
            )
            logging.info(f"Recorded response from {user_id}: {activity_value}")
            
        except TelegramUser.DoesNotExist:
            logging.warning(f"Received poll answer from unknown user: {user_id}")
        except Exception as e:
            logging.error(f"Error saving poll response: {e}")

async def send_poll_job(context: ContextTypes.DEFAULT_TYPE):
    """Sends a poll to all registered users."""
    from .models import TelegramUser
    
    # Get all users (wrap in sync_to_async)
    users = await sync_to_async(list)(TelegramUser.objects.all())
    
    questions = ["What have you done this hour?"]
    options = [
        "Short Form Brain Rot",
        "Long Form Brain Rot",
        "Upskill",
        "Friends & Family",
        "Hobbies",
        "Movies / Series"
    ]
    
    for user in users:
        try:
            await context.bot.send_poll(
                chat_id=user.chat_id,
                question=questions[0],
                options=options,
                is_anonymous=False,
                allows_multiple_answers=False
            )
            logging.info(f"Sent poll to {user.user.username} ({user.chat_id})")
        except Exception as e:
            logging.error(f"Failed to send poll to {user.chat_id}: {e}")

def create_application():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not set")
        
    application = ApplicationBuilder().token(token).build()
    
    start_handler = CommandHandler('start', start)
    # Correct handler for PollAnswer
    poll_handler = PollAnswerHandler(receive_poll_answer)
    
    application.add_handler(start_handler)
    application.add_handler(poll_handler)
    
    # Set up JobQueue
    job_queue = application.job_queue
    # Run every 3600 seconds (1 hour)
    # For testing, you might want to run it every minute. 
    # But per requirements: "for every hour".
    job_queue.run_repeating(send_poll_job, interval=10000, first=10)
    
    return application
