from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Post
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Comment
from .models import UserProfile


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
    
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture']

class PostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditor5Widget(config_name='extends'))
    
    class Meta:
        model = Post
        fields = ('title', 'content', 'image','location')  # Ensure 'image' is included here


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        
class UserCreateForm(UserCreationForm):
    profile_picture = forms.ImageField(required=False)  # Assuming UserProfile has a profile_picture field

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            UserProfile.objects.get_or_create(user=user, defaults={'profile_picture': self.cleaned_data.get('profile_picture')})
        return user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile  # Ensure this references the correct Profile model
        fields = ['bio', 'profile_picture']
        
class UserProfileForm(forms.ModelForm):  # Add this form if you need it
    class Meta:
        model = UserProfile
        fields = ['profile_picture']