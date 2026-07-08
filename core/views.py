from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Project, ContactMessage, Profile


def ensure_profile(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile

def home(request):
    projects = Project.objects.filter(is_home=True).order_by('-created_at')
    return render(request, 'home/ambuj.html', {'projects': projects})

def about(request):
    return render(request, 'home/about.html')

def blog(request):
    projects = Project.objects.filter(is_blog=True).order_by('-created_at')
    return render(request, 'home/blog.html', {'projects': projects})

def contact(request):
    success = False
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                message=message
            )
            success = True
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
                return JsonResponse({'status': 'success', 'message': 'Your message has been sent. We will get back to you shortly.'})
            messages.success(request, "Your message has been sent. We will get back to you shortly.")
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
                return JsonResponse({'status': 'error', 'message': 'All fields are required.'}, status=400)
            messages.error(request, "All fields are required.")

    return render(request, 'home/contact.html', {'success': success})

def admin_login(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')

    error_message = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            error_message = "Invalid username or password"

    return render(request, 'admin/login.html', {'error': error_message})

def admin_logout(request):
    logout(request)
    return redirect('admin_login')

@login_required(login_url='admin_login')
def admin_dashboard(request):
    profile = ensure_profile(request.user)

    # Stats
    new_messages_count = ContactMessage.objects.filter(is_read=False).count()
    blog_cards_count = Project.objects.filter(is_blog=True).count()
    home_projects_count = Project.objects.filter(is_home=True).count()

    # Lists
    contact_messages = ContactMessage.objects.all().order_by('-created_at')
    blog_projects = Project.objects.filter(is_blog=True).order_by('-created_at')
    home_projects = Project.objects.filter(is_home=True).order_by('-created_at')
    all_projects = Project.objects.all().order_by('-created_at')

    # Get active tab from GET query params
    active_tab = request.GET.get('tab', 'dashboard')

    context = {
        'profile': profile,
        'new_messages_count': new_messages_count,
        'blog_cards_count': blog_cards_count,
        'home_projects_count': home_projects_count,
        'messages': contact_messages,
        'blog_projects': blog_projects,
        'home_projects': home_projects,
        'all_projects': all_projects,
        'active_tab': active_tab,
    }
    return render(request, 'admin/admin.html', context)

@login_required(login_url='admin_login')
def add_project(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        domain = request.POST.get('domain', '').strip()
        url = request.POST.get('url', '').strip()
        description = request.POST.get('description', '').strip()
        tags = request.POST.get('tags', '').strip()
        status = request.POST.get('status', 'live').strip()
        
        # Determine target
        target = request.POST.get('target', 'home')  # 'home', 'blog', or 'both'
        is_home = target in ['home', 'both']
        is_blog = target in ['blog', 'both']

        if title and domain and description:
            Project.objects.create(
                title=title,
                domain=domain,
                url=url if url else None,
                description=description,
                tags=tags,
                status=status,
                is_home=is_home,
                is_blog=is_blog
            )
            messages.success(request, "✅ Project added successfully!")
        else:
            messages.error(request, "Please fill out all required fields.")

    return redirect(f"{redirect('admin_dashboard').url}?tab={request.POST.get('tab_redirect', 'dashboard')}")

@login_required(login_url='admin_login')
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.title = request.POST.get('title', '').strip()
        project.domain = request.POST.get('domain', '').strip()
        project.url = request.POST.get('url', '').strip() or None
        project.description = request.POST.get('description', '').strip()
        project.tags = request.POST.get('tags', '').strip()
        project.status = request.POST.get('status', 'live').strip()
        
        target = request.POST.get('target', 'home')
        project.is_home = target in ['home', 'both']
        project.is_blog = target in ['blog', 'both']
        
        project.save()
        messages.success(request, "✅ Project updated successfully!")

    return redirect(f"{redirect('admin_dashboard').url}?tab={request.POST.get('tab_redirect', 'dashboard')}")

@login_required(login_url='admin_login')
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project.delete()
    messages.success(request, "🗑️ Project deleted successfully!")
    return redirect(f"{redirect('admin_dashboard').url}?tab={request.GET.get('tab_redirect', 'dashboard')}")

@login_required(login_url='admin_login')
def mark_message_read(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.is_read = True
    msg.save()
    messages.success(request, "✅ Message marked as read!")
    return redirect(f"{redirect('admin_dashboard').url}?tab=messages")

@login_required(login_url='admin_login')
def delete_message(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.delete()
    messages.success(request, "🗑️ Message deleted successfully!")
    return redirect(f"{redirect('admin_dashboard').url}?tab=messages")

@login_required(login_url='admin_login')
def update_profile(request):
    profile = ensure_profile(request.user)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        profile_photo = request.FILES.get('profile_photo')

        updated = False
        if profile_photo:
            profile.photo = profile_photo
            profile.save()
            updated = True

        if username and username != request.user.username:
            if get_user_model().objects.filter(username=username).exclude(pk=request.user.pk).exists():
                messages.error(request, "That username is already taken.")
            else:
                request.user.username = username
                request.user.save(update_fields=['username'])
                updated = True

        if new_password:
            request.user.set_password(new_password)
            request.user.save()
            login(request, request.user)
            updated = True

        if updated:
            messages.success(request, "Profile updated successfully.")

    return redirect(f"{redirect('admin_dashboard').url}?tab=profile")
