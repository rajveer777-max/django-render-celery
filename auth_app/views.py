# auth_app/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.urls import reverse

def account_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    # *** Use 'form' for the login form key ***
    login_form = AuthenticationForm()
    signup_form = UserCreationForm()
    context = {
        'form': login_form,  # Changed key from 'login_form' to 'form'
        'signup_form': signup_form,
    }
    return render(request, 'auth_app/account.html', context)

def signup_view(request):
    if request.method == 'POST':
        # Use a different local variable name to avoid confusion with context key
        signup_form_instance = UserCreationForm(request.POST)
        if signup_form_instance.is_valid():
            user = signup_form_instance.save()
            login(request, user)
            return redirect('core:dashboard')
        else:
            # When signup fails, render account.html again
            # *** Use 'form' for the login form key ***
            login_form_instance = AuthenticationForm() # Fresh login form
            context = {
                'form': login_form_instance, # Changed key from 'login_form' to 'form'
                'signup_form': signup_form_instance, # Pass back the invalid signup form
                'show_signup': True # Optional flag
            }
            return render(request, 'auth_app/account.html', context)
    else:
        return redirect('auth:account')