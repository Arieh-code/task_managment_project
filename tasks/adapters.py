# tasks/adapters.py

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_email, user_username
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import get_user_model

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    
    def pre_social_login(self, request, sociallogin):
        """Skip signup form if user with the same email exists, log them in directly."""
        
        # Retrieve email from social account
        email = sociallogin.account.extra_data.get('email')
        
        # Check if the user exists
        if email and self.get_user_by_email(email):
            # User exists: Log in directly
            sociallogin.connect(request, self.get_user_by_email(email))
            return

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form=form)
        
        # Check if first and last name are missing
        if not user.first_name or not user.last_name:
            # Redirect to the custom username setup page
            return redirect(reverse('setup_username'))
        
        # Optionally, create a username by combining first and last names
        if not user.username:
            user.username = f"{user.first_name}_{user.last_name}".lower()
            user.save()

        return user
    
    def get_user_by_email(self, email):
        """Utility to get the user by email if they already exist."""
        
        User = get_user_model()
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None
