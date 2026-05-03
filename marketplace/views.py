from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Order, OrderItem, Invoice
from .forms import ProductForm, AddToCartForm

## just testing if my name is coming or not asdasd
def admin_required(view_func):
    """Decorator to check if user is admin"""
    def wrapper(request, *args, **kwargs):
        profile = getattr(request.user, 'profile', None)
        if not profile or profile.role != 'admin':
            messages.error(request, 'Access denied. Admin only.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return login_required(wrapper)


# ============ PRODUCT VIEWS (Admin) ============

@admin_required
def product_list(request):
    """Admin view to list all products"""
    products = Product.objects.all()
    return render(request, 'marketplace/admin/product_list.html', {'products': products})


@admin_required
def product_create(request):
    """Admin view to create a new product"""
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully!')
            return redirect('marketplace:product_list')
    else:
        form = ProductForm()
    return render(request, 'marketplace/admin/product_form.html', {
        'form': form,
        'action': 'Add',
        'title': 'Add New Product'
    })


@admin_required
def product_edit(request, pk):
    """Admin view to edit a product"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('marketplace:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'marketplace/admin/product_form.html', {
        'form': form,
        'action': 'Edit',
        'product': product,
        'title': f'Edit Product: {product.name}'
    })


@admin_required
def product_delete(request, pk):
    """Admin view to delete a product"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('marketplace:product_list')
    return render(request, 'marketplace/admin/product_confirm_delete.html', {'product': product})


# ============ PRODUCT VIEWS (Customer) ============

@login_required
def shop(request):
    """Customer view to browse and shop for products"""
    products = Product.objects.filter(is_active=True)
    return render(request, 'marketplace/customer/shop.html', {'products': products})


# ============ ORDER & CART VIEWS ============

@login_required
def add_to_cart(request, product_id):
    """Add product to cart (create/update order)"""
    product = get_object_or_404(Product, pk=product_id, is_active=True)

    if request.method == 'POST':
        form = AddToCartForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']

            # Get or create pending order for user
            order, created = Order.objects.get_or_create(
                customer=request.user,
                status='pending'
            )

            # Check if product already in order
            try:
                order_item = order.items.get(product=product)
                order_item.quantity += quantity
                order_item.save()
                messages.success(request, f'Updated {product.name} quantity in cart!')
            except OrderItem.DoesNotExist:
                order_item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price_at_purchase=product.price
                )
                messages.success(request, f'Added {product.name} to cart!')

            order.calculate_total()
            return redirect('marketplace:view_cart')
    else:
        form = AddToCartForm()

    return render(request, 'marketplace/customer/add_to_cart.html', {
        'product': product,
        'form': form
    })


@login_required
def view_cart(request):
    """View pending order (cart)"""
    try:
        order = Order.objects.get(customer=request.user, status='pending')
    except Order.DoesNotExist:
        order = None

    return render(request, 'marketplace/customer/cart.html', {'order': order})


@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    order_item = get_object_or_404(OrderItem, pk=item_id)
    order = order_item.order

    if order.customer != request.user:
        messages.error(request, 'Access denied!')
        return redirect('marketplace:view_cart')

    product_name = order_item.product.name
    order_item.delete()
    messages.success(request, f'Removed {product_name} from cart!')

    # Delete order if no items left
    if not order.items.exists():
        order.delete()
        return redirect('marketplace:shop')

    order.calculate_total()
    return redirect('marketplace:view_cart')


@login_required
def checkout(request):
    """Checkout and confirm order"""
    try:
        order = Order.objects.get(customer=request.user, status='pending')
    except Order.DoesNotExist:
        messages.error(request, 'Your cart is empty!')
        return redirect('marketplace:shop')

    if request.method == 'POST':
        # Mark order as confirmed and create invoice
        order.status = 'confirmed'
        order.save()

        # Create invoice for the order
        invoice = Invoice.objects.create(
            order=order,
            amount_due=order.total_amount,
            status='issued'
        )

        messages.success(request, 'Order placed successfully!')
        return redirect('marketplace:order_detail', order_id=order.id)

    return render(request, 'marketplace/customer/checkout.html', {'order': order})


# ============ ORDER VIEWS ============

@login_required
def my_orders(request):
    """View customer's orders"""
    orders = Order.objects.filter(customer=request.user).exclude(status='pending')
    return render(request, 'marketplace/customer/my_orders.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """View order details"""
    order = get_object_or_404(Order, pk=order_id)

    if order.customer != request.user:
        messages.error(request, 'Access denied!')
        return redirect('marketplace:my_orders')

    return render(request, 'marketplace/customer/order_detail.html', {'order': order})


@admin_required
def all_orders(request):
    """Admin view of all orders"""
    orders = Order.objects.select_related('customer').exclude(status='pending')
    return render(request, 'marketplace/admin/all_orders.html', {'orders': orders})


@admin_required
def order_status_update(request, order_id):
    """Admin view to update order status"""
    order = get_object_or_404(Order, pk=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order._meta.get_field('status').choices):
            order.status = new_status
            order.save()
            messages.success(request, f'Order status updated to {new_status}!')
            return redirect('marketplace:all_orders')

    return render(request, 'marketplace/admin/order_status_update.html', {'order': order})


# ============ INVOICE VIEWS ============

@login_required
def my_invoices(request):
    """View customer's invoices"""
    invoices = Invoice.objects.filter(order__customer=request.user)
    return render(request, 'marketplace/customer/my_invoices.html', {'invoices': invoices})


@login_required
def invoice_detail(request, invoice_id):
    """View invoice details"""
    invoice = get_object_or_404(Invoice, pk=invoice_id)

    if invoice.order.customer != request.user:
        messages.error(request, 'Access denied!')
        return redirect('marketplace:my_invoices')

    return render(request, 'marketplace/customer/invoice_detail.html', {'invoice': invoice})


@admin_required
def all_invoices(request):
    """Admin view of all invoices"""
    invoices = Invoice.objects.select_related('order', 'order__customer').order_by('-issued_date')
    return render(request, 'marketplace/admin/all_invoices.html', {'invoices': invoices})
