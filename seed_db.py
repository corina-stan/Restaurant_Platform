import os
import django
import random
import urllib.request
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

from accounts.models import User
from menu.models import Category, Product, Ingredient, StockReceipt, PurchaseInvoice, RecipeItem, Supplier
from orders.models import Order, OrderGroup, OrderItem, OperationLog
from payments.models import Payment
from tables.models import Table, QRSession

def clear_data():
    print("Stergem datele anterioare (exceptand userii)...")
    OperationLog.objects.all().delete()
    Payment.objects.all().delete()
    OrderItem.objects.all().delete()
    OrderGroup.objects.all().delete()
    Order.objects.all().delete()
    QRSession.objects.all().delete()
    Table.objects.all().delete()
    
    # Curatam retetele si stocurile pentru a evita ProtectedError pe ingrediente
    RecipeItem.objects.all().delete()
    StockReceipt.objects.all().delete()
    PurchaseInvoice.objects.all().delete()
    Ingredient.objects.all().delete()
    Supplier.objects.all().delete()
    
    Product.objects.all().delete()
    Category.objects.all().delete()
    print("Datele au fost sterse!")

def seed_users():
    print("Adaugam useri noi...")
    # Add an admin if not exists
    if not User.objects.filter(username='cori').exists():
        User.objects.create_user('cori', 'admin@example.com', 'cori', role='admin')
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

LOCAL_GENERATED_IMAGES = {
    'Papanasi cu smantana si dulceata': 'papanasi_1782635701220.png',
    'Ciorba de burta': 'ciorba_de_burta_1782635715229.png',
    'Ciorba radauteana': 'ciorba_radauteana_1782635728708.png',
    'Ciorba de vacuta': 'ciorba_de_vacuta_1782635745600.png',
    'Clatite cu fineti': 'clatite_cu_fineti_1782635760819.png',
    'Cheesecake': 'cheesecake_1782635772898.png',
    'Fanta 330ml': 'fanta_1782635787600.png',
    'Sprite 330ml': 'sprite_1782635800852.png',
    'Apa minerala 500ml': 'apa_minerala_1782635817566.png',
    'Fresh de portocale 250ml': 'fresh_portocale_1782635830406.png',
    'Tiramisu': 'tiramisu_1782635846036.png',
    'Lava Cake': 'lava_cake_1782635858736.png',
    'Ursus Premium 400ml': 'bere_ursus_1782636562532.png',
    'Heineken 330ml': 'bere_heineken_1782636579595.png',
    'Stella Artois 330ml': 'bere_stella_1782636596274.png',
    'Corona 330ml': 'bere_corona_1782636610484.png',
    'Margherita': 'pizza_margherita_1782636624592.png',
    'Mojito': 'cocktail_mojito_1782669572600.png',
    'Margarita': 'cocktail_margarita_1782669587044.png',
    'Cuba Libre': 'cocktail_cuba_libre_1782669600661.png',
    'Pina Colada': 'cocktail_pina_colada_1782669612557.png',
    'Aperol Spritz': 'cocktail_aperol_spritz_1782669625472.png',
    'Gin Tonic': 'cocktail_gin_tonic_1782669641120.png',
    'Diavola': 'pizza_diavola_1782669886242.png',
    'Quattro Formaggi': 'pizza_quattro_formaggi_1782669898858.png',
    'Prosciutto e Funghi': 'pizza_prosciutto_funghi_1782669910856.png',
    'Capricciosa': 'pizza_capricciosa_1782669923729.png',
    'Vegetariana': 'pizza_vegetariana_1782669936827.png',
    'Spaghetti Carbonara': 'pasta_carbonara_1782670027641.png',
    'Penne Milanese': 'pasta_milanese_1782670040451.png',
    'Penne Arrabiata': 'pasta_arrabiata_1782670054626.png',
    'Tagliatelle Bolognese': 'pasta_bolognese_1782670068692.png',
    'Tortellini al Forno': 'pasta_tortellini_1782670083750.png',
    'Espresso': 'cafea_espresso_1782670227502.png',
    'Coca Cola 330ml': 'racoritoare_coca_cola_static.png',
    'Apa plata 500ml': 'racoritoare_apa_plata_static.png',
    'Limonada cu menta 400ml': 'racoritoare_limonada_static.png',
    'Cappuccino': 'cafea_cappuccino_static.png',
    'Caffe Latte': 'cafea_latte_static.png',
    'Frappe': 'cafea_frappe_static.png',
}

PRODUCT_IMAGES = {}

PRODUCT_DESCRIPTIONS = {
    # PIZZA
    'Margherita': 'Ingrediente: Aluat pizza (făină 250g), Mozzarella 150g, Sos de roșii 50g.',
    'Diavola': 'Ingrediente: Aluat pizza (făină 250g), Mozzarella 150g, Salam Pepperoni 100g, Sos de roșii 50g.',
    'Quattro Formaggi': 'Ingrediente: Aluat pizza (făină 250g), Mozzarella 100g, Gorgonzola 50g, Parmezan 50g.',
    'Prosciutto e Funghi': 'Ingrediente: Aluat pizza (făină 250g), Mozzarella 150g, Prosciutto Cotto 100g, Ciuperci 50g, Sos de roșii 50g.',
    'Capricciosa': 'Ingrediente: Aluat pizza (făină 250g), Mozzarella 150g, Prosciutto Cotto 80g, Anghinare 50g, Ciuperci 50g, Măsline 30g, Sos de roșii 50g.',
    'Vegetariana': 'Ingrediente: Aluat pizza (făină 250g), Mozzarella 150g, Ciuperci 50g, Ardei gras 50g, Porumb 50g, Sos de roșii 50g.',

    # PASTE
    'Spaghetti Carbonara': 'Ingrediente: Paste 150g, Bacon/Pancetta 80g, Smântână dulce 50g.',
    'Penne Milanese': 'Ingrediente: Paste 150g, Prosciutto Cotto 50g, Ciuperci 50g, Sos de roșii 50g.',
    'Penne Arrabiata': 'Ingrediente: Paste 150g, Sos de roșii 100g, Usturoi 20g, Ardei iute 10g.',
    'Tagliatelle Bolognese': 'Ingrediente: Paste 150g, Carne tocată 150g, Sos de roșii 100g.',
    'Tortellini al Forno': 'Ingrediente: Tortellini 200g, Smântână dulce 100g, Mozzarella 50g.',

    # DESERT
    'Papanasi cu smantana si dulceata': 'Ingrediente: Brânză dulce 150g, Făină 150g, Smântână 50g, Dulceață 50g, 1 Ou.',
    'Tiramisu': 'Ingrediente: Pișcoturi 100g, Mascarpone 100g, Cafea 10g, 1 Ou.',
    'Clatite cu fineti': 'Ingrediente: Făină 100g, Lapte 100ml, Cremă ciocolată 50g, 1 Ou.',
    'Lava Cake': 'Ingrediente: Ciocolată 100g, Făină 50g, 1 Ou.',
    'Cheesecake': 'Ingrediente: Cremă de brânză 150g, Biscuiți digestivi 100g, Dulceață 50g.',

    # CIORBE
    'Ciorba de burta': 'Ingrediente: Burtă de vită 200g, Smântână 50g, Usturoi 10g.',
    'Ciorba radauteana': 'Ingrediente: Piept de pui 200g, Smântână 50g, Usturoi 10g.',
    'Ciorba de vacuta': 'Ingrediente: Carne de vită 200g, Mix legume ciorbă 100g.',

    # COCKTAILS
    'Mojito': 'Ingrediente: Rom 50ml, Lime 50g, Mentă proaspătă 10g.',
    'Margarita': 'Ingrediente: Tequila 50ml, Triplu Sec 20ml, Lime 50g.',
    'Cuba Libre': 'Ingrediente: Rom 50ml, Coca Cola 330ml, Lime 50g.',
    'Pina Colada': 'Ingrediente: Rom 50ml, Suc ananas 100ml, Cremă de cocos 50ml.',
    'Aperol Spritz': 'Ingrediente: Prosecco 100ml, Aperol 50ml, Apă minerală 50ml.',
    'Gin Tonic': 'Ingrediente: Gin 50ml, Apă tonică 200ml.',

    # RACORITOARE
    'Limonada cu menta 400ml': 'Ingrediente: Lămâie 150g, Mentă proaspătă 10g, Zahăr 20g.',
    'Fresh de portocale 250ml': 'Ingrediente: Portocale proaspete 500g (250ml fresh).',

    # CAFEA
    'Espresso': 'Ingrediente: Boabe cafea macinate 9g.',
    'Cappuccino': 'Ingrediente: Lapte 150ml, Boabe cafea macinate 9g.',
    'Caffe Latte': 'Ingrediente: Lapte 250ml, Boabe cafea macinate 9g.',
    'Frappe': 'Ingrediente: Lapte 100ml, Frișcă 50ml, Cafea solubilă 15g.',

    # BERE
}

def get_product_image_path(product_name, url):
    # Nume sigur pentru fisier (folosim png deoarece imaginile noastre generate sunt png)
    use_png = product_name in LOCAL_GENERATED_IMAGES or not url
    ext = '.png' if use_png else '.jpg'
    safe_name = product_name.lower().replace(' ', '_').replace('/', '_').replace('.', '_') + ext
    
    # Cai media
    media_dir = os.path.join(settings.MEDIA_ROOT, 'products')
    os.makedirs(media_dir, exist_ok=True)
    filepath = os.path.join(media_dir, safe_name)
    db_relative_path = f'products/{safe_name}'
    
    if os.path.exists(filepath):
        return db_relative_path

    # Incarcam din imaginile noastre generate
    if product_name in LOCAL_GENERATED_IMAGES:
        import shutil
        local_name = LOCAL_GENERATED_IMAGES[product_name]
        
        # 1. Incercam mai intai calea din static resources (care se trimite pe Git)
        static_dir = os.path.join(settings.BASE_DIR, 'menu', 'static', 'products')
        src_path = os.path.join(static_dir, local_name)
        
        # 2. Daca nu exista acolo (nu s-a rulat scriptul de copiere inca), cautam local in artifacts
        if not os.path.exists(src_path):
            artifacts_dir = r"C:\Users\stanc\.gemini\antigravity-ide\brain\8428fc7b-3663-4f3d-bced-6f724335a294"
            src_path = os.path.join(artifacts_dir, local_name)
            
        if os.path.exists(src_path):
            print(f"Copiem imaginea generata pentru {product_name}...")
            shutil.copy(src_path, filepath)
            return db_relative_path

    # Altfel, descarcam din Unsplash
    if url:
        print(f"Descarcam imaginea pentru {product_name}...")
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=15) as response, open(filepath, 'wb') as f:
                f.write(response.read())
            print(f"Salvat la {filepath}")
            return db_relative_path
        except Exception as e:
            print(f"Eroare la descarcarea imaginii pentru {product_name}: {e}")
            
    return None

def create_product(category, name, price, prep_time=0):
    url = PRODUCT_IMAGES.get(name)
    image_path = get_product_image_path(name, url)
    desc = PRODUCT_DESCRIPTIONS.get(name, '')
    return Product.objects.create(
        category=category,
        name=name,
        price=price,
        prep_time=prep_time,
        image=image_path,
        description=desc
    )

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
    create_product(cat_pizza, 'Margherita', Decimal('35.00'), 15)
    create_product(cat_pizza, 'Diavola', Decimal('42.00'), 15)
    create_product(cat_pizza, 'Quattro Formaggi', Decimal('45.00'), 20)
    create_product(cat_pizza, 'Prosciutto e Funghi', Decimal('40.00'), 18)
    create_product(cat_pizza, 'Capricciosa', Decimal('43.00'), 18)
    create_product(cat_pizza, 'Vegetariana', Decimal('38.00'), 15)

    # PASTE
    create_product(cat_paste, 'Spaghetti Carbonara', Decimal('38.00'), 12)
    create_product(cat_paste, 'Penne Milanese', Decimal('36.00'), 12)
    create_product(cat_paste, 'Penne Arrabiata', Decimal('34.00'), 10)
    create_product(cat_paste, 'Tagliatelle Bolognese', Decimal('40.00'), 15)
    create_product(cat_paste, 'Tortellini al Forno', Decimal('45.00'), 20)

    # DESERT
    create_product(cat_desert, 'Papanasi cu smantana si dulceata', Decimal('28.00'), 15)
    create_product(cat_desert, 'Tiramisu', Decimal('25.00'), 5)
    create_product(cat_desert, 'Clatite cu fineti', Decimal('20.00'), 10)
    create_product(cat_desert, 'Lava Cake', Decimal('30.00'), 12)
    create_product(cat_desert, 'Cheesecake', Decimal('26.00'), 5)

    # CIORBE
    create_product(cat_ciorbe, 'Ciorba de burta', Decimal('28.00'), 5)
    create_product(cat_ciorbe, 'Ciorba radauteana', Decimal('26.00'), 5)
    create_product(cat_ciorbe, 'Ciorba de vacuta', Decimal('25.00'), 5)

    # COCKTAILS
    create_product(cat_cocktails, 'Mojito', Decimal('30.00'), 5)
    create_product(cat_cocktails, 'Margarita', Decimal('32.00'), 5)
    create_product(cat_cocktails, 'Cuba Libre', Decimal('28.00'), 5)
    create_product(cat_cocktails, 'Pina Colada', Decimal('35.00'), 5)
    create_product(cat_cocktails, 'Aperol Spritz', Decimal('35.00'), 3)
    create_product(cat_cocktails, 'Gin Tonic', Decimal('32.00'), 3)

    # RACORITOARE
    create_product(cat_racoritoare, 'Coca Cola 330ml', Decimal('10.00'), 1)
    create_product(cat_racoritoare, 'Fanta 330ml', Decimal('10.00'), 1)
    create_product(cat_racoritoare, 'Sprite 330ml', Decimal('10.00'), 1)
    create_product(cat_racoritoare, 'Apa plata 500ml', Decimal('8.00'), 1)
    create_product(cat_racoritoare, 'Apa minerala 500ml', Decimal('8.00'), 1)
    create_product(cat_racoritoare, 'Limonada cu menta 400ml', Decimal('20.00'), 5)
    create_product(cat_racoritoare, 'Fresh de portocale 250ml', Decimal('18.00'), 3)

    # CAFEA
    create_product(cat_cafea, 'Espresso', Decimal('10.00'), 3)
    create_product(cat_cafea, 'Cappuccino', Decimal('14.00'), 5)
    create_product(cat_cafea, 'Caffe Latte', Decimal('16.00'), 5)
    create_product(cat_cafea, 'Frappe', Decimal('22.00'), 5)

    # BERE
    create_product(cat_bere, 'Ursus Premium 400ml', Decimal('12.00'), 1)
    create_product(cat_bere, 'Heineken 330ml', Decimal('15.00'), 1)
    create_product(cat_bere, 'Stella Artois 330ml', Decimal('15.00'), 1)
    create_product(cat_bere, 'Corona 330ml', Decimal('18.00'), 1)

def seed_tables():
    print("Adaugam mese...")
    for i in range(1, 16):
        Table.objects.create(number=i, name=f'Masa {i}')

def seed_suppliers():
    print("Adaugam furnizori demo...")
    Supplier.objects.create(
        name="Metro Cash & Carry",
        fiscal_code="RO123456",
        trade_registry_number="J40/1111/1996",
        address="Bulevardul Theodor Pallady 51, București"
    )
    Supplier.objects.create(
        name="Selgros Cash & Carry",
        fiscal_code="RO789012",
        trade_registry_number="J08/2222/2001",
        address="Calea București 231, Brașov"
    )
    Supplier.objects.create(
        name="Auchan România",
        fiscal_code="RO345678",
        trade_registry_number="J40/3333/2005",
        address="Strada Brașov 25, București"
    )
    Supplier.objects.create(
        name="Maravela Group SRL",
        fiscal_code="RO901234",
        trade_registry_number="J12/4444/2012",
        address="Strada Bună Ziua 12, Cluj-Napoca"
    )

if __name__ == '__main__':
    print("Incepem seed-ul bazei de date...")
    clear_data()
    seed_users()
    seed_suppliers()
    seed_menu()
    seed_tables()
    print("Baza de date a fost populata cu succes!")
