from .models import Product


def cart_context(request):
    """Make cart data available in all templates."""
    cart = request.session.get('cart', {})
    cart_count = sum(item.get('quantity', 0) for item in cart.values())
    cart_total = 0

    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            price = float(product.effective_price)
            cart_total += price * item.get('quantity', 0)
        except Product.DoesNotExist:
            pass

    return {
        'cart_count': cart_count,
        'cart_total': cart_total,
    }
