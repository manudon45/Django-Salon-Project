from django.test import TestCase
from django.contrib.auth.models import User
from .models import Product, Order, OrderItem, Invoice
from glambookapp.models import UserProfile


class ProductTestCase(TestCase):
    """Test Product model"""
    def setUp(self):
        self.product = Product.objects.create(
            name='Test Product',
            price=25.00,
            quantity_in_stock=10
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.price, 25.00)
        self.assertTrue(self.product.is_active)

    def test_product_str(self):
        self.assertEqual(str(self.product), 'Test Product')


class OrderTestCase(TestCase):
    """Test Order model"""
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            role='customer'
        )
        self.product = Product.objects.create(
            name='Test Product',
            price=25.00,
            quantity_in_stock=10
        )
        self.order = Order.objects.create(
            customer=self.user,
            status='pending'
        )

    def test_order_creation(self):
        self.assertEqual(self.order.customer, self.user)
        self.assertEqual(self.order.status, 'pending')
        self.assertEqual(self.order.total_amount, 0)

    def test_order_calculate_total(self):
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price_at_purchase=25.00
        )
        self.order.calculate_total()
        self.assertEqual(self.order.total_amount, 50.00)


class OrderItemTestCase(TestCase):
    """Test OrderItem model"""
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.product = Product.objects.create(
            name='Test Product',
            price=25.00,
            quantity_in_stock=10
        )
        self.order = Order.objects.create(
            customer=self.user,
            status='pending'
        )
        self.item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=3,
            price_at_purchase=25.00
        )

    def test_order_item_total(self):
        self.assertEqual(self.item.get_total_price(), 75.00)


class InvoiceTestCase(TestCase):
    """Test Invoice model"""
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.order = Order.objects.create(
            customer=self.user,
            total_amount=100.00
        )
        self.invoice = Invoice.objects.create(
            order=self.order,
            amount_due=100.00
        )

    def test_invoice_creation(self):
        self.assertEqual(self.invoice.order, self.order)
        self.assertEqual(self.invoice.amount_due, 100.00)
        self.assertTrue(self.invoice.invoice_number.startswith('INV-'))

    def test_invoice_number_generation(self):
        self.assertIsNotNone(self.invoice.invoice_number)
        # Create second order and invoice to test numbering
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@test.com',
            password='testpass123'
        )
        order2 = Order.objects.create(
            customer=user2,
            total_amount=50.00
        )
        invoice2 = Invoice.objects.create(
            order=order2,
            amount_due=50.00
        )
        self.assertNotEqual(self.invoice.invoice_number, invoice2.invoice_number)
