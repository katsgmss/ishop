from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.crypto import get_random_string
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from .models import Category, Item, Order
from django.db.models import Q
from .forms import UserRegistrationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django import forms


def item(request, item_id):
    item_details = Item.objects.get(id=item_id)
    return render(request, 'catalogue/item.html', { 'single': item_details})

def category_list(request):
    items = Item.objects.all()
    query = request.GET.get('q', '')
    if query:
        items = items.filter(name__icontains=query) 
    return render(request, 'catalogue/category_list.html', {'items': items, 'query': query})

def search_items(request):
    query = request.GET.get('q', '')
    categories = Category.objects.all()
    items = Item.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(category_name__icontains=query))
    return render(request, 'catalogue/search_results.html', {'items': items, 'query': query, 'categories': categories})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'catalogue/register.html', {'form': form})

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(user=request.user, data=request.POST)
        
        if 'update_profile' in request.POST and form.is_valid():  # Check for profile update submission
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('profile')

        if 'change_password' in request.POST and password_form.is_valid():  # Check for password change submission
            password_form.save()
            update_session_auth_hash(request, password_form.user)
            messages.success(request, 'Your password has been updated.')
            return redirect('profile')

    else:
        form = UserUpdateForm(instance=request.user)
        password_form = PasswordChangeForm(user=request.user)

    orders = Order.objects.filter(name=request.user.username)

    return render(request, 'catalogue/profile.html', {
        'form': form,
        'orders': orders,
        'password_form': password_form
    })


def add_to_cart(request, item_id):
    item = Item.objects.get(id=item_id)
    cart = request.session.get('cart', {})
    item_id_str = str(item_id)
    item_price = float(item.price)

    if item_id_str in cart:
        cart[item_id_str]['quantity'] += 1
    else:
        cart[item_id_str] = {
            'name': item.name,
            'price': item_price,
            'quantity': 1
        }

    request.session['cart'] = cart
    return redirect('cart')

def view_cart(request):
    cart = request.session.get('cart', {})
    for item_id, item in cart.items():
        item['total_price'] = item['price'] * item['quantity']

    total = sum(item['total_price'] for item in cart.values())

    return render(request, 'catalogue/cart.html', {'cart': cart, 'total': total})

def fetch_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for item_id, item in cart.items():
        item_obj = Item.objects.get(id=item_id)
        item['total_price'] = item['price'] * item['quantity']
        cart_items.append(item)
        total += item['total_price']

    return JsonResponse({'cart_items': cart_items, 'total': total})
    
def remove_from_cart(request, item_id):
    cart = request.session.get('cart', {})

    if item_id in cart:
        del cart[item_id]

    request.session['cart'] = cart
    return redirect('cart')

def clear_cart(request):
    request.session['cart'] = {}
    return redirect('cart')

def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart')
    for item_id, item in cart.items():
        item['total_price'] = item['price'] * item['quantity']
    total = sum(item['total_price'] for item in cart.values())
    return render(request, 'catalogue/checkout.html', {'cart': cart, 'total': total})


@login_required
def place_order(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart')

    total_price = sum(item['price'] * item['quantity'] for item in cart.values())

    description = f"Order placed by {request.user.username}. Items: "
    for item_id, item in cart.items():
        description += f"{item['quantity']} x {item['name']} (at ${item['price']:.2f} each), "

    description = description.rstrip(", ")

    order_id = get_random_string(8).upper()
    order = Order.objects.create(
        orderID=order_id,
        name=request.user.username,
        description=description,
        total_price=total_price 
    )
    request.session['cart'] = {}

    return render(request, 'catalogue/order_confirmation.html', {
        'cart': cart,
        'total': total_price,
        'user': request.user.username,
        'order_id': order_id
    })