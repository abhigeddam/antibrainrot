from django.core.management.base import BaseCommand
from core.bot import create_application
import asyncio

class Command(BaseCommand):
    help = 'Runs the Telegram Bot'

    def handle(self, *args, **options):
        application = create_application()
        self.stdout.write(self.style.SUCCESS('Starting bot polling...'))
        application.run_polling()
