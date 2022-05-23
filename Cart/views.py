import datetime
import json
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string

from AdayaApp.models import Product
from AdayaPharmacy import settings
from .forms import OrderForm
from .models import Cart, CartItem, Order, OrderProduct
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

# Create your views here.
from django.http import HttpResponse, JsonResponse


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


@login_required(login_url='login')
def add_cart(request, product_id):
    current_user = request.user
    qty = int(request.POST.get('qty'))
    product = Product.objects.get(id=product_id)  # get the product
    # If the user is authenticated
    if current_user.is_authenticated:

        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.get(product=product, user=current_user)

            cart_item.quantity += qty
            cart_item.save()
            messages.success(request, f'Updated {cart_item.product.product_name} \
                                quantity to {cart_item.quantity }.')



        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=qty,
                user=current_user,
            )

            cart_item.save()
            messages.success(request, f'Added {cart_item.product.product_name} \
                                           to your basket.')
        return redirect('cart')


@login_required(login_url='login')
def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        total_amount = 0
        grand_total = 0
        total_tax = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)

        for cart_item in cart_items:
            total = (cart_item.product.Rate * cart_item.quantity)
            quantity += cart_item.quantity

            if cart_item.product.gst15 is True:
                tax = (20 * total) / 100
            elif cart_item.product.gst18 is True:
                tax = (10 * total) / 100
            else:
                tax = (5 * total) / 100

            total_tax += tax
            total_amount += total

        grand_total = total_amount + total_tax
    except ObjectDoesNotExist:
        pass  # just ignore

    context = {
        'total': total_amount,
        'quantity': quantity,
        'cart_items': cart_items,
        'total_tax': total_tax,
        'grand_total': grand_total,
    }
    return render(request, 'dashboard/cart.html', context)


@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        total_amount = 0
        grand_total = 0
        total_tax = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)


        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total = (cart_item.product.Rate * cart_item.quantity)
            quantity += cart_item.quantity
            if cart_item.product.gst15 is True:
                tax = (20 * total) / 100
            elif cart_item.product.gst18 is True:
                tax = (10 * total) / 100
            else:
                tax = (5 * total) / 100

            total_tax += tax
            total_amount += total

        grand_total = total_amount + total_tax
    except ObjectDoesNotExist:
        pass  # just ignore

    context = {
        'total': total_amount,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': total_tax,
        'grand_total': grand_total,
    }
    return render(request, 'dashboard/checkout.html', context)


@login_required(login_url='login')
def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    messages.success(request,  f'Removed {cart_item.product.product_name}'
                                  ' from your Cart.')
    return redirect('cart')


@login_required(login_url='login')
def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            messages.success(request, f'Updated {cart_item.product.product_name} \
                                quantity to {cart_item.quantity }.')
        else:
            cart_item.delete()
            messages.success(request, f'Removed {cart_item.product.product_name}'
                                      ' from your Cart.')
    except:
        pass
    return redirect('cart')


@login_required(login_url='login')
def place_order(request, total=0, quantity=0, ):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('dashboard')

    tax = 0
    total_amount = 0
    grand_total = 0
    total_tax = 0
    for cart_item in cart_items:
        total = (cart_item.product.Rate * cart_item.quantity)
        quantity += cart_item.quantity
        if cart_item.product.gst15 is True:
            tax = (15 * total) / 100
        elif cart_item.product.gst18 is True:
            tax = (18 * total) / 100
        else:
            tax = (5 * total) / 100

        total_tax += tax
        total_amount += total

    grand_total = total_amount + total_tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = total_tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")  # 20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            request.session['order_number'] = data.order_number

            data.save()

            order = Order.objects.get(is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total_amount,
                'tax': total_tax,
                'grand_total': grand_total,
            }
            return render(request, 'dashboard/payments.html', context)
    else:
        return redirect('checkout')


@login_required(login_url='login')
def order_complete(request):
    order_number = request.session.get('order_number')
    print(order_number)

    order = Order.objects.get(user=request.user, order_number=order_number)

    order.is_ordered = True
    order.save()

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id

        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.Rate
        orderproduct.ordered = True
        orderproduct.save()

        orderproduct = OrderProduct.objects.get(id=orderproduct.id)

        orderproduct.save()

        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'subtotal': subtotal,

        }
        messages.info(request, 'Your Order placed Successfully')
        # Send order recieved email to customer
        mail_subject = 'Thank you for your order!'
        message = render_to_string('dashboard/order_received_email.html',

                                   {
                                       'user': request.user,
                                       'order': order,
                                       'ordered_products': ordered_products,
                                       'order_number': order.order_number,
                                        'subtotal': subtotal, }).strip()

        to_email = [request.user.email]

        msg = EmailMultiAlternatives(mail_subject, message, settings.EMAIL_HOST_USER, to_email,
                                     reply_to=[settings.EMAIL_HOST_USER])
        msg.content_subtype = 'html'
        msg.mixed_subtype = 'related'

        msg.send()
        return render(request, 'dashboard/order_comp.html', context)
    except (order.DoesNotExist):
        return redirect('dashboard')


def All_Orders(request):
    order_products = OrderProduct.objects.all()
    context = {

        'order_products': order_products,
    }
    return render(request, 'Admin_Orders.html', context)
