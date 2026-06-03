"""
Session-based authentication views for the template frontend.

JWT token blacklisting lives under /auth/api/logout/ for API clients only.
"""

import logging

from django.contrib import messages
from django.contrib.auth import login, logout as django_logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

from portfolio.models import ResearcherProfile

from .forms import SessionLoginForm, SessionRegistrationForm
from .models import AuditLog

logger = logging.getLogger("django.security")


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def _user_agent(request):
    return request.META.get("HTTP_USER_AGENT", "")


@require_http_methods(["GET", "POST"])
def session_login(request):
    """Log in with username/password and establish a Django session."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = SessionLoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        ip = _client_ip(request)
        AuditLog.objects.create(
            user=user,
            event_type="login",
            description=f"Session login from {ip}",
            ip_address=ip,
            user_agent=_user_agent(request),
        )
        logger.info("User %s logged in via session from %s", user.username, ip)
        next_url = request.GET.get("next") or reverse("dashboard")
        return redirect(next_url)

    return render(request, "auth/login.html", {"form": form})


@require_http_methods(["GET", "POST"])
def session_register(request):
    """Create an account and log the user in with a session."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = SessionRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                user = form.save()
                ResearcherProfile.objects.get_or_create(
                    user=user,
                    defaults={"orcid_id": None},
                )
                login(request, user)
                ip = _client_ip(request)
                AuditLog.objects.create(
                    user=user,
                    event_type="registration",
                    description=f"Session registration for {user.username} from {ip}",
                    ip_address=ip,
                    user_agent=_user_agent(request),
                )
        except IntegrityError:
            logger.exception("Registration failed due to database integrity error")
            messages.error(
                request,
                "We could not complete registration. If you already have an account, try signing in.",
            )
            return render(request, "auth/register.html", {"form": form})

        messages.success(request, "Your account was created successfully.")
        return redirect("dashboard")

    return render(request, "auth/register.html", {"form": form})


@login_required
@require_POST
def standard_logout(request):
    """End the Django session (no JWT blacklist required)."""
    user = request.user
    username = user.username
    ip = _client_ip(request)
    django_logout(request)
    AuditLog.objects.create(
        user=None,
        event_type="logout",
        description=f"Session logout for {username} from {ip}",
        ip_address=ip,
        user_agent=_user_agent(request),
    )
    logger.info("User %s logged out via session from %s", username, ip)
    messages.info(request, "You have been signed out.")
    return redirect("auth_service:login")
