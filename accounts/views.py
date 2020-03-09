from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from accounts.forms import SignUpForm
from accounts.tokens import account_activation_token


def signup_view(request):
    form = SignUpForm(request.POST)
    if form.is_valid():
        user = form.save()
        user.refresh_from_db()
        user.is_active = False
        current_site = get_current_site(request)
        subject = 'Family Tree account activation'

        message = render_to_string('activation_request.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            # method will generate a hash value with user related data
            'token': account_activation_token.make_token(user),
        })
        user.email_user(subject, message)
        return redirect('activation_sent')
    # else:
    #     form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def activation_sent_view(request):
    return render(request, 'activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    # checking if the user exists, if the token is valid.
    if user is not None and account_activation_token.check_token(user, token):
        # if valid set active true
        user.is_active = True
        # set signup_confirmation true
        # user.profile.signup_confirmation = True
        user.save()
        login(request, user)
        return redirect('/')
    else:
        return render(request, 'activation_invalid.html')
