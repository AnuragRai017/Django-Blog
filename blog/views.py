from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.db.models import Q
from .forms import SignUpForm, ProfileUpdateForm, PostForm, CommentForm, UserProfileForm
from .models import Profile, Post, Comment
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib import messages
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from .models import Post, PostView

User = get_user_model()

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    extra_context = {'auth_page': True}

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_active:
            messages.error(self.request, 'Your account is inactive. Please check your email to activate your account.')
            return redirect('login')
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    extra_context = {'auth_page': True}

class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    extra_context = {'auth_page': True}

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'
    extra_context = {'auth_page': True}

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    extra_context = {'auth_page': True}

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'
    extra_context = {'auth_page': True}

def index(request):
    if not request.user.is_authenticated:
        return redirect('login')
    posts = Post.objects.all()
    return render(request, 'blog/index.html', {'posts': posts})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account till it is confirmed
            user.save()
            Profile.objects.create(user=user)
            send_verification_email(request, user)
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'blog/signup.html', {'form': form, 'auth_page': True})

def send_verification_email(request, user):
    current_site = get_current_site(request)
    subject = 'Activate Your Account'
    message = render_to_string('blog/account_activation_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    })
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('index')
    else:
        return render(request, 'blog/account_activation_invalid.html')

def account_activation_sent(request):
    return render(request, 'blog/account_activation_sent.html')

@login_required
def search(request):
    query = request.GET.get('q')
    if query:
        posts = Post.objects.filter(Q(title__icontains=query) | Q(content__icontains=query))
    else:
        posts = Post.objects.all()
    return render(request, 'blog/search_results.html', {'posts': posts, 'query': query})

@login_required
def profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=profile)

    user_posts = Post.objects.filter(author=request.user)
    return render(request, 'blog/profile.html', {'form': form, 'posts': user_posts, 'profile': profile})

@login_required
def delete_profile(request):
    user = request.user
    user.delete()
    return redirect('index')

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    else:
        form = PostForm()
    return render(request, 'blog/create_post.html', {'form': form})

@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        return redirect('index')
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/edit_post.html', {'form': form})

@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        return redirect('index')
    if request.method == 'POST':
        post.delete()
        return redirect('index')
    return render(request, 'blog/delete_post.html', {'post': post})

@login_required
def all_posts(request):
    posts = Post.objects.all()
    return render(request, 'blog/all_posts.html', {'posts': posts})

@login_required
def stats(request):
    user = request.user
    posts = Post.objects.filter(author=user)
    return render(request, 'blog/stats.html', {'posts': posts})

@login_required
def comments(request):
    user = request.user
    comments = Comment.objects.filter(post__author=user)
    return render(request, 'blog/comments.html', {'comments': comments})

@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)

    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key

    if request.user.is_authenticated:
        view, created = PostView.objects.get_or_create(post=post, user=request.user)
    else:
        view, created = PostView.objects.get_or_create(post=post, session_id=session_id)

    if created:
        post.views += 1
        post.save()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        comment_form = CommentForm()

    comments = post.comments.all()
    viewers = post.post_views.filter(user__isnull=False).select_related('user')
    
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comment_form': comment_form,
        'comments': comments,
        'viewers': viewers
    })

@login_required
def user_comments(request):
    comments = Comment.objects.filter(author=request.user)
    return render(request, 'blog/comments.html', {'comments': comments})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to profile page after updating
    else:
        form = UserProfileForm(instance=request.user.profile)
    return render(request, 'blog/edit_profile.html', {'form': form})
