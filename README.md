# Anti-Brainrot Activity Tracker

A personal productivity tool that integrates with Telegram to track where your time actually goes.

The concept is simple: instead of manually logging time, a Telegram bot prompts you every hour to select what you've been doing. The web dashboard then visualizes this data, categorizing activities into "Productive", "Leisure", or "Brain Rot" (mindless scrolling/consumption) and provides insights relative to previous time periods.

## Features

- **Telegram Bot specific:** Doesn't require a constantly running separate process for the bot; it's integrated into the Django management commands.
- **Deep Linking:** One-click connection between your web account and Telegram account.
- **Activity Categories:**
    - **Brain Rot:** Short-form content, doomscrolling, etc.
    - **Productive:** Upskilling, work, hobbies.
    - **Leisure:** Movies, series, socializing.
- **Dashboard:** Visualizes time distribution with Chart.js and provides comparative insights (e.g., "You spent 15% less time on reels this week compared to last").

## Local Setup

### Prerequisites

- Python 3.8+
- A standardized Telegram Bot Token (get one from @BotFather)

### Installation

1.  Clone the repo:
    ```bash
    git clone https://github.com/abhigeddam/antibrainrot.git
    cd antibrainrot
    ```

2.  Environment setup:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

3.  Configuration:
    Create a `.env` file in the root directory:
    ```ini
    TELEGRAM_BOT_TOKEN=your_token_here
    DJANGO_SECRET_KEY=your_secret_key
    DEBUG=True
    ```

4.  Database:
    ```bash
    python manage.py migrate
    ```

5.  Run it:
    ```bash
    python manage.py runserver
    ```

## Usage

1.  Register an account on the web interface (`localhost:8000`).
2.  Follow the flow to connect your Telegram account.
3.  The bot will start sending hourly prompts.
4.  Check the dashboard to see your stats.
