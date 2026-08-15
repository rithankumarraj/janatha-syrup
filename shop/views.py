from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q

from .models import Category, Product, Order, OrderItem, Review, NewsletterSubscriber
from .forms import (
    CustomerRegistrationForm, LoginForm, ReviewForm,
    ContactForm, CheckoutForm, NewsletterForm
)


# ─── Home Page ────────────────────────────────────────────────────────
def home(request):
    featured_products = Product.objects.filter(featured=True, in_stock=True)[:6]
    categories = Category.objects.all()
    return render(request, 'home.html', {
        'featured_products': featured_products,
        'categories': categories,
    })


# ─── Shop / Products Listing ─────────────────────────────────────────
def shop(request):
    products = Product.objects.filter(in_stock=True)
    categories = Category.objects.all()

    # Filter by category
    category_slug = request.GET.get('category')
    active_category = None
    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=active_category)

    # Search
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # Sort
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-created_at')

    return render(request, 'shop.html', {
        'products': products,
        'categories': categories,
        'active_category': active_category,
        'query': query or '',
        'sort': sort,
    })


# ─── Product Detail ──────────────────────────────────────────────────
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.all()
    related_products = Product.objects.filter(
        category=product.category, in_stock=True
    ).exclude(id=product.id)[:4]

    review_form = ReviewForm()

    # Handle review submission
    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            # Check if user already reviewed
            if Review.objects.filter(product=product, user=request.user).exists():
                messages.warning(request, 'You have already reviewed this product.')
            else:
                review = review_form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                messages.success(request, 'Your review has been submitted!')
                return redirect('product_detail', slug=slug)

    return render(request, 'product_detail.html', {
        'product': product,
        'reviews': reviews,
        'related_products': related_products,
        'review_form': review_form,
    })


# ─── Cart ─────────────────────────────────────────────────────────────
def cart(request):
    cart_data = request.session.get('cart', {})
    cart_items = []
    total = 0

    for product_id, item in cart_data.items():
        try:
            product = Product.objects.get(id=product_id)
            quantity = item.get('quantity', 1)
            subtotal = float(product.effective_price) * quantity
            total += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal,
            })
        except Product.DoesNotExist:
            pass

    shipping = 0 if total >= 500 else 49
    grand_total = total + shipping

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total,
        'shipping': shipping,
        'grand_total': grand_total,
    })


def add_to_cart(request, product_id):
    """Add a product to the session cart."""
    product = get_object_or_404(Product, id=product_id, in_stock=True)
    cart = request.session.get('cart', {})
    product_key = str(product_id)
    quantity = int(request.POST.get('quantity', 1))

    if product_key in cart:
        cart[product_key]['quantity'] += quantity
    else:
        cart[product_key] = {'quantity': quantity}

    request.session['cart'] = cart
    request.session.modified = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_count = sum(item.get('quantity', 0) for item in cart.values())
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart!',
            'cart_count': cart_count,
        })

    messages.success(request, f'{product.name} added to cart!')
    return redirect(request.META.get('HTTP_REFERER', 'shop'))


def update_cart(request, product_id):
    """Update quantity of a cart item."""
    cart = request.session.get('cart', {})
    product_key = str(product_id)
    quantity = int(request.POST.get('quantity', 1))

    if product_key in cart:
        if quantity > 0:
            cart[product_key]['quantity'] = quantity
        else:
            del cart[product_key]

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart')


def remove_from_cart(request, product_id):
    """Remove a product from the cart."""
    cart = request.session.get('cart', {})
    product_key = str(product_id)

    if product_key in cart:
        del cart[product_key]

    request.session['cart'] = cart
    request.session.modified = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_count = sum(item.get('quantity', 0) for item in cart.values())
        return JsonResponse({'success': True, 'cart_count': cart_count})

    messages.success(request, 'Item removed from cart.')
    return redirect('cart')


# ─── Checkout ─────────────────────────────────────────────────────────
def checkout(request):
    cart_data = request.session.get('cart', {})
    if not cart_data:
        messages.warning(request, 'Your cart is empty.')
        return redirect('shop')

    # Build cart items for display
    cart_items = []
    total = 0
    for product_id, item in cart_data.items():
        try:
            product = Product.objects.get(id=product_id)
            quantity = item.get('quantity', 1)
            subtotal = float(product.effective_price) * quantity
            total += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal,
            })
        except Product.DoesNotExist:
            pass

    shipping = 0 if total >= 500 else 49
    grand_total = total + shipping

    # Pre-fill form for logged-in users
    initial_data = {}
    if request.user.is_authenticated:
        initial_data = {
            'full_name': f'{request.user.first_name} {request.user.last_name}'.strip(),
            'email': request.user.email,
        }

    form = CheckoutForm(initial=initial_data)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.total = grand_total
            if request.user.is_authenticated:
                order.user = request.user
            order.save()

            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item['product'],
                    product_name=cart_item['product'].name,
                    quantity=cart_item['quantity'],
                    price=cart_item['product'].effective_price,
                )

            # Clear cart
            request.session['cart'] = {}
            request.session.modified = True

            messages.success(request, 'Your order has been placed successfully!')
            return redirect('order_confirmation', order_number=order.order_number)

    return render(request, 'checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'total': total,
        'shipping': shipping,
        'grand_total': grand_total,
    })


def order_confirmation(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'order_confirmation.html', {'order': order})


# ─── Auth ─────────────────────────────────────────────────────────────
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = CustomerRegistrationForm()
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to Janatha Syrup, {user.first_name}!')
            return redirect('home')

    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'profile.html', {'orders': orders})


# ─── About & Contact ─────────────────────────────────────────────────
def about(request):
    return render(request, 'about.html')


def contact(request):
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
            return redirect('contact')

    return render(request, 'contact.html', {'form': form})


# ─── Newsletter ───────────────────────────────────────────────────────
@require_POST
def newsletter_subscribe(request):
    email = request.POST.get('email', '').strip()
    if email:
        obj, created = NewsletterSubscriber.objects.get_or_create(email=email)
        if created:
            msg = 'Thank you for subscribing to our newsletter!'
        else:
            msg = 'You are already subscribed.'

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': msg})
        messages.success(request, msg)

    return redirect(request.META.get('HTTP_REFERER', 'home'))
