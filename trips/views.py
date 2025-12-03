from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from .models import Trip, Booking, ChatMessage, UserProfile
from .forms import ContactForm
from .locations import KENYA_LOCATIONS
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.core.mail import send_mail
from django.conf import settings

# Home page
def home(request):
    return render(request, "index.html")

# Trips landing page (after login)
@login_required
def trips(request):
    # Get filter parameter from URL (upcoming, success, cancelled, all)
    status_filter = request.GET.get('status', 'all')
    
    if status_filter == 'all':
        trip_list = Trip.objects.all()
    else:
        trip_list = Trip.objects.filter(status=status_filter)
    
    return render(request, "destinations.html", {
        "trips": trip_list,
        "status_filter": status_filter
    })

# Trip detail page
@login_required
def trip_details(request, id):
    trip = get_object_or_404(Trip, id=id)
    return render(request, "trip_details.html", {"trip": trip})

# Book a trip
@login_required
def book_trip(request, id):
    trip = get_object_or_404(Trip, id=id)
    Booking.objects.create(user=request.user, trip=trip)
    return redirect("trips")

# Contact us page
def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the message to database
            contact_message = form.save()
            
            # Send email to admin
            subject = f"New Contact Message: {contact_message.subject}"
            message_body = f"""
You have received a new contact message from Central Adventures website.

From: {contact_message.name}
Email: {contact_message.email}
Subject: {contact_message.subject}

Message:
{contact_message.message}

---
This message was sent via the contact form on the Central Adventures website.
"""
            
            try:
                send_mail(
                    subject=subject,
                    message=message_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.EMAIL_HOST_USER],
                    fail_silently=False
                )
                messages.success(request, 'Thank you! Your message has been sent successfully.')
            except Exception as e:
                print(f"Email sending failed: {e}")
                messages.warning(request, 'Your message has been saved, but email notification failed.')
            
            # Clear form after successful submission
            form = ContactForm()
    else:
        form = ContactForm()
    # Use the `contacts.html` template for the contact page
    return render(request, 'contacts.html', {'form': form})

# Group chat page
@login_required
def chat_room(request):
    # If you have a dedicated chat template create `chat.html` in templates;
    # fall back to the notification demo for now if it's present.
    try:
        return render(request, "chat.html")
    except Exception:
        return render(request, "notification-demo.html")

# Simple views to render the static frontend templates that live under
# `trips/templates/` so they are reachable via URL routes.
def login_page(request):
    # Handle login POST - accept username or email
    if request.method == 'POST':
        identifier = request.POST.get('email')
        password = request.POST.get('password')

        user = None
        # Try by username first
        try:
            user = User.objects.get(username=identifier)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=identifier)
            except User.DoesNotExist:
                user = None

        if user is None:
            messages.error(request, 'User not found.')
            return render(request, 'login.html')

        user_auth = authenticate(request, username=user.username, password=password)
        if user_auth is not None:
            login(request, user_auth)
            messages.success(request, 'Logged in successfully.')
            return redirect('trips')
        else:
            messages.error(request, 'Invalid credentials.')
            return render(request, 'login.html')

    return render(request, "login.html")

def signup_page(request):
    # Handle signup form POST to create a User and UserProfile
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm = request.POST.get('confirmPassword')
        first_name = request.POST.get('firstName', '')
        last_name = request.POST.get('lastName', '')
        age = request.POST.get('age')
        county = request.POST.get('county', '')
        constituency = request.POST.get('constituency', '')
        bio = request.POST.get('bio', '')
        contact_info = request.POST.get('contactInfo', '')

        if not username or not email or not password:
            messages.error(request, 'Username, email and password are required.')
            return render(request, 'signup.html')

        if password != confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'signup.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # Create profile
        profile = UserProfile.objects.create(
            user=user,
            age=int(age) if age else None,
            county=county,
            constituency=constituency,
            bio=bio,
            contact_info=contact_info
        )

        # Optionally authenticate and login the new user
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, 'Account created and logged in.')
            return redirect('trips')

        return redirect('login')

    return render(request, "signup.html")

def gallery_page(request):
    return render(request, "gallery.html")

def edit_profile_page(request):
    if not request.user.is_authenticated:
        return redirect('login')

    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Update user fields
        username = request.POST.get('username')
        first_name = request.POST.get('firstName', '')
        last_name = request.POST.get('lastName', '')
        email = request.POST.get('email', '')

        if username and username != request.user.username:
            if User.objects.filter(username=username).exclude(pk=request.user.pk).exists():
                messages.error(request, 'Username already taken.')
                return redirect('edit_profile')
            request.user.username = username

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()

        # Update profile fields
        age = request.POST.get('age')
        county = request.POST.get('county', '')
        constituency = request.POST.get('constituency', '')
        bio = request.POST.get('bio', '')
        contact_info = request.POST.get('contactInfo', '')
        profile.age = int(age) if age else None
        profile.county = county
        profile.constituency = constituency
        profile.bio = bio
        profile.contact_info = contact_info

        # Handle uploaded profile picture with basic validation
        uploaded_image = request.FILES.get('profile_picture')
        if uploaded_image:
            # Basic server-side validation: limit size and ensure image content type
            max_bytes = 2 * 1024 * 1024  # 2 MB
            content_type = uploaded_image.content_type
            if uploaded_image.size > max_bytes:
                messages.error(request, 'Image too large. Maximum size is 2MB.')
                return redirect('edit_profile')
            if not content_type.startswith('image/'):
                messages.error(request, 'Invalid file type. Please upload an image.')
                return redirect('edit_profile')

            profile.profile_picture = uploaded_image
        profile.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('edit_profile')

    # GET - prefill form
    context = {
        'user': request.user,
        'profile': profile,
    }
    return render(request, "edit-profile.html", context)

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('home')

def destinations_page(request):
    return render(request, "destinations.html")

def notification_demo(request):
    return render(request, "notification-demo.html")
from django.utils import timezone
from .models import Booking

def remove_unpaid_bookings():
    now = timezone.now()
    unpaid_bookings = Booking.objects.filter(deposit_paid=False, pay_later_deadline__lt=now)
    for booking in unpaid_bookings:
        booking.delete()


# API endpoints for location data
def api_counties(request):
    """Return list of all Kenyan counties."""
    counties = sorted(KENYA_LOCATIONS.keys())
    return JsonResponse({'counties': counties})


def api_constituencies(request):
    """Return constituencies for a given county."""
    county = request.GET.get('county', '')
    if county and county in KENYA_LOCATIONS:
        constituencies = KENYA_LOCATIONS[county]
        return JsonResponse({'constituencies': constituencies})
    return JsonResponse({'constituencies': [], 'error': 'County not found'}, status=400)
