from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.db import models

from .forms import RegistrationForm
from .models import Account
from ..carts.models import Cart, CartItem
from ..carts.views import _cart_id

#verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():

            user = Account.objects.create_user(
                first_name = form.cleaned_data['first_name'],
                last_name = form.cleaned_data['last_name'],
                username = form.cleaned_data['username'],
                email = form.cleaned_data['email'],
                password = form.cleaned_data['password'],
            )

            user.phone_number = form.cleaned_data['phone_number']
            user.save()

            # user activation
            current_site = get_current_site(request)
            mail_subject = f'Account activation on {current_site}'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            to_email = form.cleaned_data['email']
            send_email = EmailMessage(mail_subject, message, to=[to_email,])
            send_email.send()
            return redirect('/accounts/login/?command=verification&email=' + form.cleaned_data['email'])           
    else:
        form = RegistrationForm

    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email = email, password = password)

        if user is not None:
            try:
                cart  = Cart.objects.get(cart_id=_cart_id(request))
                cart_items = CartItem.objects.filter(cart=cart)  # Find elements with the given cart

                for cart_item in cart_items:
                    if cart_item.variations.exists():
                        # Find items with the same name as user
                        variations_cart_items = CartItem.objects.filter(variations__in=cart_item.variations.all(), user=user)

                        if variations_cart_items.exists():
                            variations_cart_items.update(quantity=models.F('quantity') + 1)
                            cart_item.delete()
                        else:
                            cart_item.user = user
                            cart_item.save()
                    else:
                        cart_items_without_variations = CartItem.objects.filter(product=cart_item.product, user=user)
                        
                        if cart_items_without_variations.exists():
                            cart_items_without_variations.update(quantity=models.F('quantity') + 1)
                            cart_item.delete()
                        else:
                            cart_item.user = user
                            cart_item.save()               
            except:
                pass

            auth.login(request, user)
            messages.success(request, 'You are logged in.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials.')
            return redirect('login')
        
    return render(request, 'accounts/login.html')


@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated!')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')


@login_required(login_url = 'login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # reset password send email
            current_site = get_current_site(request)
            mail_subject = f'Reset your password on {current_site}'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email,])
            send_email.send()

            messages.success(request, 'A verification link for reset password has been sent to your email adress.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist.')
            return redirect('forgotPassword')

    return render(request, 'accounts/forgotPassword.html')


def resetPasswordValidate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account._default_manager.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match!')
            return redirect('resetPassword') 
        
    return render(request, 'accounts/resetPassword.html')