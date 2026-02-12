

import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('adminpanel', '0009_alter_notification_send_datetime'),
        ('location', '0003_alter_area_city'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OfferDiscount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=200)),
                ('discount_percentage', models.DecimalField(decimal_places=2, max_digits=5)),
                ('offer_code', models.CharField(max_length=20, unique=True)),
                ('valid_from', models.DateField()),
                ('valid_to', models.DateField()),
                ('isactive', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_paid', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('remaining_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('payment_date', models.DateTimeField(auto_now_add=True)),
                ('method', models.CharField(choices=[('WALLET', 'Wallet'), ('COD', 'Cash On Delivery'), ('UPI', 'UPI')], max_length=20)),
                ('status', models.CharField(choices=[('PAID', 'Paid'), ('PARTIAL', 'Partial'), ('PENDING', 'Pending'), ('FAILED', 'Failed')], max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='FoodItemOfferDiscount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('applied_date', models.DateField()),
                ('expiry_date', models.DateField()),
                ('is_active', models.BooleanField(default=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='adminpanel.fooditemcategory')),
                ('food_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminpanel.fooditem')),
                ('offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.offerdiscount')),
            ],
        ),
        migrations.CreateModel(
            name='CategoryOfferDiscount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('applied_date', models.DateField()),
                ('expiry_date', models.DateField()),
                ('is_active', models.BooleanField(default=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminpanel.fooditemcategory')),
                ('offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.offerdiscount')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('total_qty', models.PositiveIntegerField()),
                ('dis_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('delivery_address', models.TextField()),
                ('order_status', models.CharField(choices=[('PLACED', 'Placed'), ('CONFIRMED', 'Confirmed'), ('CANCELLED', 'Cancelled'), ('DELIVERED', 'Delivered')], default='PLACED', max_length=20)),
                ('area', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.area')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty', models.PositiveIntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('food_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminpanel.fooditem')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_details', to='orders.order')),
            ],
        ),
        migrations.CreateModel(
            name='SubCategoryOfferDiscount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('applied_date', models.DateField()),
                ('expiry_date', models.DateField()),
                ('is_active', models.BooleanField(default=True)),
                ('offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.offerdiscount')),
                ('subcategory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminpanel.fooditemsubcategory')),
            ],
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WalletTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('txn_type', models.CharField(choices=[('CREDIT', 'Credit'), ('DEBIT', 'Debit')], max_length=10)),
                ('description', models.CharField(max_length=255)),
                ('txn_date', models.DateTimeField(auto_now_add=True)),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='orders.wallet')),
            ],
        ),
        migrations.CreateModel(
            name='OrderHasPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('transaction_no', models.CharField(blank=True, max_length=100, null=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.order')),
                ('payment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.payment')),
                ('wallet_transaction', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='orders.wallettransaction')),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('food_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminpanel.fooditem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'food_item')},
            },
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_date', models.DateTimeField(auto_now_add=True)),
                ('food_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminpanel.fooditem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'food_item')},
            },
        ),
    ]
