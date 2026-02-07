from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib import messages
from .models import TelegramUser, PollResponse
from .forms import RegisterForm
import uuid

@login_required
def dashboard(request):
    try:
        telegram_user = request.user.telegram_user
        if not telegram_user.chat_id:
            return redirect('connect_telegram')
            
        responses = PollResponse.objects.filter(telegram_user=telegram_user)
        
        # Aggregate data for charts
        data = responses.values('activity').annotate(count=Count('activity'))
        
        # Map activity codes to names
        activity_map = dict(PollResponse.ACTIVITY_CHOICES)
        chart_labels = []
        chart_data = []
        
        for entry in data:
            label = activity_map.get(entry['activity'], 'Unknown')
            chart_labels.append(label)
            chart_data.append(entry['count'])
            
        context = {
            'chart_labels': chart_labels,
            'chart_data': chart_data,
            'recent_responses': responses.order_by('-timestamp')[:10]
        }
        return render(request, 'core/dashboard.html', context)
        
    except TelegramUser.DoesNotExist:
        # Should have been created at register, but just in case
        return redirect('connect_telegram')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create TelegramUser with a verification token
            token = str(uuid.uuid4())
            TelegramUser.objects.create(user=user, verification_token=token)
            
            login(request, user)
            return redirect('connect_telegram')
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form})

@login_required
def connect_telegram(request):
    try:
        telegram_user = request.user.telegram_user
    except TelegramUser.DoesNotExist:
        # Create if not exists (handling edge cases)
        token = str(uuid.uuid4())
        telegram_user = TelegramUser.objects.create(user=request.user, verification_token=token)
    

        
    # Generate Bot Link
    # Replace 'antirot_Bot' with actual bot username if dynamic
    bot_username = "antirot_Bot" 
    deep_link = f"https://t.me/{bot_username}?start={telegram_user.verification_token}"
    
    return render(request, 'core/connect_telegram.html', {'deep_link': deep_link})

@login_required
def check_connection_status(request):
    from django.http import JsonResponse
    try:
        telegram_user = request.user.telegram_user
        if telegram_user.chat_id:
            return JsonResponse({'connected': True})
    except TelegramUser.DoesNotExist:
        pass
    return JsonResponse({'connected': False})
