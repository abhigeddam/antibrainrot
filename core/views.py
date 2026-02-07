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
            
        # Time Filter
        time_range = request.GET.get('range', 'week') # Default to week
        from django.utils import timezone
        import datetime
        
        now = timezone.now()
        responses = PollResponse.objects.filter(telegram_user=telegram_user)
        
        if time_range == 'day':
            delta = datetime.timedelta(days=1)
            responses = responses.filter(timestamp__date=now.date())
        elif time_range == 'week':
            delta = datetime.timedelta(days=7)
            responses = responses.filter(timestamp__gte=now - delta)
        elif time_range == 'month':
            delta = datetime.timedelta(days=30)
            responses = responses.filter(timestamp__gte=now - delta)
        elif time_range == 'year':
            delta = datetime.timedelta(days=365)
            responses = responses.filter(timestamp__gte=now - delta)
        
        # Calculate Previous Period Stats
        previous_start = now - (delta * 2)
        previous_end = now - delta
        
        prev_responses = PollResponse.objects.filter(
            telegram_user=telegram_user,
            timestamp__gte=previous_start,
            timestamp__lt=previous_end
        )

        def get_stats(queryset):
            brain_rot = ['1', '2']
            productive = ['3', '4', '5']
            
            br_count = 0
            prod_count = 0
            neu_count = 0
            
            counts = queryset.values('activity').annotate(count=Count('activity'))
            for entry in counts:
                code = entry['activity']
                val = entry['count']
                if code in brain_rot: br_count += val
                elif code in productive: prod_count += val
                else: neu_count += val
            
            return br_count, prod_count, neu_count

        # Current Stats
        brain_rot_count, productive_count, neutral_count = get_stats(responses)
        
        # Previous Stats
        prev_br, prev_prod, prev_neu = get_stats(prev_responses)
        
        # Calculate Deltas
        def calc_delta(current, previous):
            if previous == 0:
                return 100 if current > 0 else 0
            return round(((current - previous) / previous) * 100, 1)

        br_delta = calc_delta(brain_rot_count, prev_br)
        prod_delta = calc_delta(productive_count, prev_prod)

        # Chart Data Preparation
        activity_map = dict(PollResponse.ACTIVITY_CHOICES)
        chart_labels = []
        chart_data = []
        
        # Re-query for specific chart data to ensure order/labels
        data = responses.values('activity').annotate(count=Count('activity'))
        for entry in data:
            chart_labels.append(activity_map.get(entry['activity'], 'Unknown'))
            chart_data.append(entry['count'])
        
        # Insights
        total_hours = brain_rot_count + productive_count + neutral_count
        brain_rot_percentage = round((brain_rot_count / total_hours * 100), 1) if total_hours > 0 else 0
        productive_percentage = round((productive_count / total_hours * 100), 1) if total_hours > 0 else 0
        neutral_percentage = round((neutral_count / total_hours * 100), 1) if total_hours > 0 else 0
        
        context = {
            'chart_labels': chart_labels,
            'chart_data': chart_data,
            'recent_responses': responses.order_by('-timestamp')[:10],
            'time_range': time_range,
            'insights': {
                'brain_rot_count': brain_rot_count,
                'productive_count': productive_count,
                'neutral_count': neutral_count,
                'brain_rot_percentage': brain_rot_percentage,
                'productive_percentage': productive_percentage,
                'neutral_percentage': neutral_percentage,
                'total_hours': total_hours,
                'br_delta': br_delta,
                'prod_delta': prod_delta,
                'neu_delta': calc_delta(neutral_count, prev_neu),
                'br_delta_abs': abs(br_delta),
                'prod_delta_abs': abs(prod_delta),
                'neu_delta_abs': abs(calc_delta(neutral_count, prev_neu)),
            }
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
