from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    # Product management (Admin)
    path('admin/products/', views.product_list, name='product_list'),
    path('admin/products/add/', views.product_create, name='product_create'),
    path('admin/products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('admin/products/<int:pk>/delete/', views.product_delete, name='product_delete'),

    # Shop (Customer)
    path('shop/', views.shop, name='shop'),

    # Cart & Checkout
    path('cart/', views.view_cart, name='view_cart'),
    path('product/<int:product_id>/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/item/<int:item_id>/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),

    # Orders (Customer)
    path('orders/', views.my_orders, name='my_orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),

    # Orders (Admin)
    path('admin/orders/', views.all_orders, name='all_orders'),
    path('admin/orders/<int:order_id>/status/', views.order_status_update, name='order_status_update'),

    # Invoices (Customer)
    path('invoices/', views.my_invoices, name='my_invoices'),
    path('invoices/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),

    # Invoices (Admin)
    path('admin/invoices/', views.all_invoices, name='all_invoices'),
]
