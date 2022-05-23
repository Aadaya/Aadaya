from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites import requests
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

# Create your views here.
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import date, timedelta

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from AdayaApp.forms import UserProfileForm, UserForm
from AdayaApp.models import Account, UserProfile, Category, Product, Notification, Contact
from Cart.models import Order, OrderProduct


def index(request):
    return render(request, 'home.html')


def reg1(request):
    userform = UserProfileForm()
    form = UserForm()
    return render(request, 'home.html', {'form': form, 'userform': userform})


def register1(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        userform = UserProfileForm(request.POST)
        if form.is_valid() and userform.is_valid():
            userform.save()
            form.save()
            messages.success(request, 'You are registered successfully.')
            return redirect('wait_for_approval')


    else:
        form = UserForm()
        userform = UserProfileForm()
    context = {
        'form': form,
        'userform': userform,

    }

    return render(request, 'home.html', context)


def register(request):
    if request.method == 'POST':

        first_name = request.POST['first_name']
        last_name = first_name
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        retailer_name = request.POST['retailer_name']
        state = request.POST['state']
        district = request.POST['district']
        landmark = request.POST['landmark']
        retailer_type = request.POST['retailer_type']
        dl_number1 = request.POST['dl_number1']
        dl_number2 = request.POST['dl_number2']

        gst = request.POST['gst']

        phone = request.POST['phone']
        dl_expiry_date = request.POST['dl_expiry_date']

        if Account.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
            return redirect('register')
        else:

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email,
                                               username=username, password=password)
            user.dl_expiry_date = dl_expiry_date
            user.save()

            user.save()
            profile = UserProfile(district=district, dl_number1=dl_number1, dl_number2=dl_number2,
                                  phone=phone, retailer_name=retailer_name,
                                  state=state, landmark=landmark, retailer_type=retailer_type,
                                  owner_name=first_name, user=user, gst=gst,
                                  dl_expiry_date=dl_expiry_date)
            profile.save()

            print('registered')
            messages.success(request, 'You are registered successfully.')
            return redirect('wait_for_approval')


    else:

        return render(request, 'home.html')


def wait_for_approval(request):
    return render(request, 'wait_for_approval.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                if date.today() > user.userprofile.dl_expiry_date:
                    print('Your Drug License expired, kindly renew it and contact us')
                    messages.success(request, 'Your Drug License expired, kindly renew it and contact us')
                    return redirect('login')
                elif user.userprofile.dl_expiry_date - date.today() < timedelta(days=30):
                    print('please update dl registration')
                    messages.success(request, 'validity only for 30 days.')

                    auth.login(request, user)
                    messages.success(request, 'You are now logged in.')
                    url = request.META.get('HTTP_REFERER')
                    try:
                        query = requests.utils.urlparse(url).query
                        # next=/cart/checkout/
                        params = dict(x.split('=') for x in query.split('&'))
                        if 'next' in params:
                            nextPage = params['next']
                            return redirect(nextPage)
                    except:
                        return redirect('dashboard')
                    # Redirect to a success page.
            else:
                messages.error(request, 'Invalid login credentials')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'home.html')

@login_required(login_url='login')
def dashboard(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    order_count = orders.count()

    context = {
        'products': paged_products,
        'product_count': product_count,
        'orders': orders,
        'order_count': order_count,
    }
    return render(request, 'dashboard/index.html', context)


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')

@login_required(login_url='login')
def notification(request):
    noti = Notification.objects.all().order_by('date')
    noti_count=noti.count()
    context = {
        'noti': noti,
        'ncount':noti_count
    }
    return render(request, 'dashboard/notification.html', context)

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        user = Account.objects.get(username__exact=request.user.username)
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, 'Password updated successfully')
                return redirect('change_password')
            else:
                messages.error(request, 'please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'password does not match')
            return redirect('change_password')

    return render(request, 'dashboard/chnagepasswd.html')

@login_required(login_url='login')
def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(
                Q(category__category_name__icontains=keyword) | Q(drug_code__icontains=keyword)
                | Q(product_name__icontains=keyword) | Q(batch__icontains=keyword))
            product_count = products.count()
        else:
            messages.error(
                request, "You didn't enter any search criteria.")


    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request, 'dashboard/search_result.html', context)


@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    order_count = orders.count()
    context = {'orders': orders,
               'order_count': order_count}
    return render(request, 'dashboard/orders.html', context)


@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)

    order = Order.objects.get(order_number=order_id)

    tot = 0
    grand_total = 0
    tax = 0
    tot += order.order_total
    total = 0

    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity
        total = i.product_price * i.quantity
        print(total)

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
        'tot': tot,
        'total': total

    }
    return render(request, 'dashboard/order_details.html', context)

@login_required(login_url='login')
def terms(request):
    return render(request, 'dashboard/termasandconditions.html')


def contact_us(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']
        contact = Contact(name=name, email=email, subject=subject, message=message)
        contact.save()
        messages.success(request, 'Your message has been sent. Thank you!')
        return redirect('index')
    else:
        return render(request, 'home.html')


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')
    return render(request, 'home.html')


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'resetPassword.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')
