import os
import django
import random
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from menu.models import Category, Product
from orders.models import Order, OrderGroup, OrderItem
from payments.models import Payment
from tables.models import Table, QRSession

def clear_data():
    print("Stergem datele anterioare (exceptand userii)...")
    Payment.objects.all().delete()
    OrderItem.objects.all().delete()
    OrderGroup.objects.all().delete()
    Order.objects.all().delete()
    QRSession.objects.all().delete()
    Table.objects.all().delete()
    Product.objects.all().delete()
    Category.objects.all().delete()
    print("Datele au fost sterse!")

def seed_users():
    print("Adaugam useri noi...")
    # Add an admin if not exists
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin', role='admin')
        print("Creat admin.")
        
    waiters = ['ionut', 'maria', 'andrei', 'elena']
    for w in waiters:
        if not User.objects.filter(username=w).exists():
            user = User.objects.create_user(username=w, password='password123', role='waiter')
            print(f"Creat ospatar: {w}")

    barmans = ['alex', 'bogdan']
    for b in barmans:
        if not User.objects.filter(username=b).exists():
            user = User.objects.create_user(username=b, password='password123', role='barman')
            print(f"Creat barman: {b}")

    kitchen = ['chef_radu', 'chef_mihai']
    for k in kitchen:
        if not User.objects.filter(username=k).exists():
            user = User.objects.create_user(username=k, password='password123', role='kitchen')
            print(f"Creat bucatar: {k}")

def seed_menu():
    print("Adaugam categorii...")
    cat_pizza = Category.objects.create(name='Pizza', department='kitchen')
    cat_paste = Category.objects.create(name='Paste', department='kitchen')
    cat_desert = Category.objects.create(name='Desert', department='kitchen')
    cat_ciorbe = Category.objects.create(name='Ciorbe', department='kitchen')

    cat_cocktails = Category.objects.create(name='Cocktails', department='bar')
    cat_racoritoare = Category.objects.create(name='Racoritoare', department='bar')
    cat_cafea = Category.objects.create(name='Cafea', department='bar')
    cat_bere = Category.objects.create(name='Bere', department='bar')

    print("Adaugam produse...")
    # PIZZA
    Product.objects.create(category=cat_pizza, name='Margherita', price=Decimal('35.00'), prep_time=15)
    Product.objects.create(category=cat_pizza, name='Diavola', price=Decimal('42.00'), prep_time=15)
    Product.objects.create(category=cat_pizza, name='Quattro Formaggi', price=Decimal('45.00'), prep_time=20)
    Product.objects.create(category=cat_pizza, name='Prosciutto e Funghi', price=Decimal('40.00'), prep_time=18)
    Product.objects.create(category=cat_pizza, name='Capricciosa', price=Decimal('43.00'), prep_time=18)
    Product.objects.create(category=cat_pizza, name='Vegetariana', price=Decimal('38.00'), prep_time=15)

    # PASTE
    Product.objects.create(category=cat_paste, name='Spaghetti Carbonara', price=Decimal('38.00'), prep_time=12)
    Product.objects.create(category=cat_paste, name='Penne Milanese', price=Decimal('36.00'), prep_time=12)
    Product.objects.create(category=cat_paste, name='Penne Arrabiata', price=Decimal('34.00'), prep_time=10)
    Product.objects.create(category=cat_paste, name='Tagliatelle Bolognese', price=Decimal('40.00'), prep_time=15)
    Product.objects.create(category=cat_paste, name='Tortellini al Forno', price=Decimal('45.00'), prep_time=20)

    # DESERT
    Product.objects.create(category=cat_desert, name='Papanasi cu smantana si dulceata', price=Decimal('28.00'), prep_time=15)
    Product.objects.create(category=cat_desert, name='Tiramisu', price=Decimal('25.00'), prep_time=5)
    Product.objects.create(category=cat_desert, name='Clatite cu fineti', price=Decimal('20.00'), prep_time=10)
    Product.objects.create(category=cat_desert, name='Lava Cake', price=Decimal('30.00'), prep_time=12)
    Product.objects.create(category=cat_desert, name='Cheesecake', price=Decimal('26.00'), prep_time=5)

    # CIORBE
    Product.objects.create(category=cat_ciorbe, name='Ciorba de burta', price=Decimal('28.00'), prep_time=5)
    Product.objects.create(category=cat_ciorbe, name='Ciorba radauteana', price=Decimal('26.00'), prep_time=5)
    Product.objects.create(category=cat_ciorbe, name='Ciorba de vacuta', price=Decimal('25.00'), prep_time=5)

    # COCKTAILS
    Product.objects.create(category=cat_cocktails, name='Mojito', price=Decimal('30.00'), prep_time=5)
    Product.objects.create(category=cat_cocktails, name='Margarita', price=Decimal('32.00'), prep_time=5)
    Product.objects.create(category=cat_cocktails, name='Cuba Libre', price=Decimal('28.00'), prep_time=5)
    Product.objects.create(category=cat_cocktails, name='Pina Colada', price=Decimal('35.00'), prep_time=5)
    Product.objects.create(category=cat_cocktails, name='Aperol Spritz', price=Decimal('35.00'), prep_time=3)
    Product.objects.create(category=cat_cocktails, name='Gin Tonic', price=Decimal('32.00'), prep_time=3)

    # RACORITOARE
    Product.objects.create(category=cat_racoritoare, name='Coca Cola 330ml', price=Decimal('10.00'), prep_time=1)
    Product.objects.create(category=cat_racoritoare, name='Fanta 330ml', price=Decimal('10.00'), prep_time=1)
    Product.objects.create(category=cat_racoritoare, name='Sprite 330ml', price=Decimal('10.00'), prep_time=1)
    Product.objects.create(category=cat_racoritoare, name='Apa plata 500ml', price=Decimal('8.00'), prep_time=1)
    Product.objects.create(category=cat_racoritoare, name='Apa minerala 500ml', price=Decimal('8.00'), prep_time=1)
    Product.objects.create(category=cat_racoritoare, name='Limonada cu menta 400ml', price=Decimal('20.00'), prep_time=5)
    Product.objects.create(category=cat_racoritoare, name='Fresh de portocale 250ml', price=Decimal('18.00'), prep_time=3)

    # CAFEA
    Product.objects.create(category=cat_cafea, name='Espresso', price=Decimal('10.00'), prep_time=3)
    Product.objects.create(category=cat_cafea, name='Cappuccino', price=Decimal('14.00'), prep_time=5)
    Product.objects.create(category=cat_cafea, name='Caffe Latte', price=Decimal('16.00'), prep_time=5)
    Product.objects.create(category=cat_cafea, name='Frappe', price=Decimal('22.00'), prep_time=5)

    # BERE
    Product.objects.create(category=cat_bere, name='Ursus Premium 400ml', price=Decimal('12.00'), prep_time=1)
    Product.objects.create(category=cat_bere, name='Heineken 330ml', price=Decimal('15.00'), prep_time=1)
    Product.objects.create(category=cat_bere, name='Stella Artois 330ml', price=Decimal('15.00'), prep_time=1)
    Product.objects.create(category=cat_bere, name='Corona 330ml', price=Decimal('18.00'), prep_time=1)

def seed_tables():
    print("Adaugam mese...")
    for i in range(1, 16):
        Table.objects.create(number=i, name=f'Masa {i}')

if __name__ == '__main__':
    print("Incepem seed-ul bazei de date...")
    clear_data()
    seed_users()
    seed_menu()
    seed_tables()
    print("Baza de date a fost populata cu succes!")
