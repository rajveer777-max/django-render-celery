# auth_app/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views # Import Django's built-in views
from . import views # We'll create our custom views soon

app_name = 'auth_app'

urlpatterns = [
    # URL to display the combined login/signup page (using our custom view)
    path('account/', views.account_view, name='account'),

    # URL to handle the actual login form submission (using Django's built-in LoginView)
    # It processes the POST request and redirects to LOGIN_REDIRECT_URL on success
    path('login/', auth_views.LoginView.as_view(template_name='auth_app/account.html'), name='login'),

    # URL to handle the signup form submission (using our custom view)
    path('signup/', views.signup_view, name='signup'),

    # URL to handle logout (using Django's built-in LogoutView)
    # It logs the user out and redirects to LOGOUT_REDIRECT_URL
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # You might add password reset URLs here later using auth_views
    # path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    # ... etc.
]