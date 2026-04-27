import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from menu.models import Product, Ingredient, RecipeItem

def run():
    print("Seeding ingredients and recipes...")

    # Create Ingredients (Magazie)
    faina, _ = Ingredient.objects.get_or_create(name='Făină Albă 000', defaults={'unit': 'kg', 'current_stock': 50.0})
    branza, _ = Ingredient.objects.get_or_create(name='Mozzarella', defaults={'unit': 'kg', 'current_stock': 20.0})
    gorgonzola, _ = Ingredient.objects.get_or_create(name='Gorgonzola', defaults={'unit': 'kg', 'current_stock': 5.0})
    parmezan, _ = Ingredient.objects.get_or_create(name='Parmezan', defaults={'unit': 'kg', 'current_stock': 5.0})
    sos, _ = Ingredient.objects.get_or_create(name='Sos de Roșii', defaults={'unit': 'litru', 'current_stock': 15.0})
    salam, _ = Ingredient.objects.get_or_create(name='Salam Pepperoni', defaults={'unit': 'kg', 'current_stock': 10.0})
    prosciutto, _ = Ingredient.objects.get_or_create(name='Prosciutto Cotto', defaults={'unit': 'kg', 'current_stock': 5.0})
    ciuperci, _ = Ingredient.objects.get_or_create(name='Ciuperci', defaults={'unit': 'kg', 'current_stock': 8.0})
    masline, _ = Ingredient.objects.get_or_create(name='Măsline', defaults={'unit': 'kg', 'current_stock': 5.0})
    anghinare, _ = Ingredient.objects.get_or_create(name='Anghinare', defaults={'unit': 'kg', 'current_stock': 3.0})
    ardei, _ = Ingredient.objects.get_or_create(name='Ardei Gras', defaults={'unit': 'kg', 'current_stock': 10.0})
    porumb, _ = Ingredient.objects.get_or_create(name='Porumb', defaults={'unit': 'kg', 'current_stock': 5.0})
    usturoi, _ = Ingredient.objects.get_or_create(name='Usturoi', defaults={'unit': 'kg', 'current_stock': 5.0})
    ardei_iute, _ = Ingredient.objects.get_or_create(name='Ardei Iute', defaults={'unit': 'kg', 'current_stock': 2.0})

    paste, _ = Ingredient.objects.get_or_create(name='Paste Uscate', defaults={'unit': 'kg', 'current_stock': 30.0})
    paste_tortellini, _ = Ingredient.objects.get_or_create(name='Tortellini', defaults={'unit': 'kg', 'current_stock': 10.0})
    bacon, _ = Ingredient.objects.get_or_create(name='Bacon/Pancetta', defaults={'unit': 'kg', 'current_stock': 10.0})
    carne_tocata, _ = Ingredient.objects.get_or_create(name='Carne Tocată (Amestec)', defaults={'unit': 'kg', 'current_stock': 15.0})
    smantana, _ = Ingredient.objects.get_or_create(name='Smântână Dulce', defaults={'unit': 'litru', 'current_stock': 12.0})

    # Desert
    branza_dulce, _ = Ingredient.objects.get_or_create(name='Brânză Dulce', defaults={'unit': 'kg', 'current_stock': 10.0})
    dulceata, _ = Ingredient.objects.get_or_create(name='Dulceață', defaults={'unit': 'kg', 'current_stock': 5.0})
    piscoturi, _ = Ingredient.objects.get_or_create(name='Pișcoturi', defaults={'unit': 'kg', 'current_stock': 5.0})
    mascarpone, _ = Ingredient.objects.get_or_create(name='Mascarpone', defaults={'unit': 'kg', 'current_stock': 8.0})
    oua, _ = Ingredient.objects.get_or_create(name='Ouă', defaults={'unit': 'buc', 'current_stock': 150.0})
    fineti, _ = Ingredient.objects.get_or_create(name='Cremă Ciocolată', defaults={'unit': 'kg', 'current_stock': 10.0})
    ciocolata, _ = Ingredient.objects.get_or_create(name='Ciocolată', defaults={'unit': 'kg', 'current_stock': 5.0})
    crema_branza, _ = Ingredient.objects.get_or_create(name='Cremă de Brânză', defaults={'unit': 'kg', 'current_stock': 10.0})
    biscuiti, _ = Ingredient.objects.get_or_create(name='Biscuiți Digestivi', defaults={'unit': 'kg', 'current_stock': 5.0})

    # Ciorbe
    burta, _ = Ingredient.objects.get_or_create(name='Burtă Vită', defaults={'unit': 'kg', 'current_stock': 20.0})
    piept_pui, _ = Ingredient.objects.get_or_create(name='Piept de Pui', defaults={'unit': 'kg', 'current_stock': 15.0})
    carne_vita, _ = Ingredient.objects.get_or_create(name='Carne Vită Ciorbă', defaults={'unit': 'kg', 'current_stock': 15.0})
    legume_ciorba, _ = Ingredient.objects.get_or_create(name='Mix Legume Ciorbă', defaults={'unit': 'kg', 'current_stock': 20.0})

    # Bar
    cafea, _ = Ingredient.objects.get_or_create(name='Boabe Cafea', defaults={'unit': 'kg', 'current_stock': 5.0})
    lapte, _ = Ingredient.objects.get_or_create(name='Lapte', defaults={'unit': 'litru', 'current_stock': 20.0})
    frisca, _ = Ingredient.objects.get_or_create(name='Frișcă', defaults={'unit': 'litru', 'current_stock': 10.0})
    cafea_nes, _ = Ingredient.objects.get_or_create(name='Cafea Solubilă (Nes)', defaults={'unit': 'kg', 'current_stock': 2.0})

    rom, _ = Ingredient.objects.get_or_create(name='Rom', defaults={'unit': 'litru', 'current_stock': 5.0})
    menta, _ = Ingredient.objects.get_or_create(name='Mentă Proaspătă', defaults={'unit': 'g', 'current_stock': 500.0})
    tequila, _ = Ingredient.objects.get_or_create(name='Tequila', defaults={'unit': 'litru', 'current_stock': 5.0})
    triplu_sec, _ = Ingredient.objects.get_or_create(name='Triplu Sec', defaults={'unit': 'litru', 'current_stock': 3.0})
    lime, _ = Ingredient.objects.get_or_create(name='Lime', defaults={'unit': 'kg', 'current_stock': 10.0})
    suc_ananas, _ = Ingredient.objects.get_or_create(name='Suc Ananas', defaults={'unit': 'litru', 'current_stock': 10.0})
    crema_cocos, _ = Ingredient.objects.get_or_create(name='Cremă Cocos', defaults={'unit': 'litru', 'current_stock': 5.0})
    aperol, _ = Ingredient.objects.get_or_create(name='Aperol', defaults={'unit': 'litru', 'current_stock': 5.0})
    prosecco, _ = Ingredient.objects.get_or_create(name='Prosecco', defaults={'unit': 'litru', 'current_stock': 10.0})
    gin, _ = Ingredient.objects.get_or_create(name='Gin', defaults={'unit': 'litru', 'current_stock': 5.0})
    apa_tonica, _ = Ingredient.objects.get_or_create(name='Apă Tonică', defaults={'unit': 'litru', 'current_stock': 15.0})

    # Fructe & Racoritoare
    lamaie, _ = Ingredient.objects.get_or_create(name='Lămâie', defaults={'unit': 'kg', 'current_stock': 10.0})
    portocale, _ = Ingredient.objects.get_or_create(name='Portocale', defaults={'unit': 'kg', 'current_stock': 20.0})
    zahar, _ = Ingredient.objects.get_or_create(name='Zahăr', defaults={'unit': 'kg', 'current_stock': 15.0})

    apa_sticla, _ = Ingredient.objects.get_or_create(name='Sticlă Apă Plată 500ml', defaults={'unit': 'buc', 'current_stock': 200.0})
    apa_min_sticla, _ = Ingredient.objects.get_or_create(name='Sticlă Apă Min. 500ml', defaults={'unit': 'buc', 'current_stock': 200.0})
    cola_sticla, _ = Ingredient.objects.get_or_create(name='Sticlă Coca Cola 330ml', defaults={'unit': 'buc', 'current_stock': 150.0})
    fanta_sticla, _ = Ingredient.objects.get_or_create(name='Sticlă Fanta 330ml', defaults={'unit': 'buc', 'current_stock': 150.0})
    sprite_sticla, _ = Ingredient.objects.get_or_create(name='Sticlă Sprite 330ml', defaults={'unit': 'buc', 'current_stock': 150.0})
    
    bere_ursus, _ = Ingredient.objects.get_or_create(name='Sticlă Ursus 400ml', defaults={'unit': 'buc', 'current_stock': 100.0})
    bere_heineken, _ = Ingredient.objects.get_or_create(name='Sticlă Heineken 330ml', defaults={'unit': 'buc', 'current_stock': 100.0})
    bere_stella, _ = Ingredient.objects.get_or_create(name='Sticlă Stella 330ml', defaults={'unit': 'buc', 'current_stock': 100.0})
    bere_corona, _ = Ingredient.objects.get_or_create(name='Sticlă Corona 330ml', defaults={'unit': 'buc', 'current_stock': 100.0})


    recipes_map = {
        # PIZZA
        'Margherita': [(faina, 0.250), (branza, 0.150), (sos, 0.050)],
        'Diavola': [(faina, 0.250), (branza, 0.150), (sos, 0.050), (salam, 0.100)],
        'Quattro Formaggi': [(faina, 0.250), (branza, 0.100), (gorgonzola, 0.050), (parmezan, 0.050)],
        'Prosciutto e Funghi': [(faina, 0.250), (branza, 0.150), (sos, 0.050), (prosciutto, 0.100), (ciuperci, 0.050)],
        'Capricciosa': [(faina, 0.250), (branza, 0.150), (sos, 0.050), (ciuperci, 0.050), (prosciutto, 0.080), (anghinare, 0.050), (masline, 0.030)],
        'Vegetariana': [(faina, 0.250), (branza, 0.150), (sos, 0.050), (ciuperci, 0.050), (ardei, 0.050), (porumb, 0.050)],

        # PASTE
        'Spaghetti Carbonara': [(paste, 0.150), (bacon, 0.080), (smantana, 0.050)],
        'Penne Milanese': [(paste, 0.150), (sos, 0.050), (ciuperci, 0.050), (prosciutto, 0.050)],
        'Penne Arrabiata': [(paste, 0.150), (sos, 0.100), (usturoi, 0.020), (ardei_iute, 0.010)],
        'Tagliatelle Bolognese': [(paste, 0.150), (carne_tocata, 0.150), (sos, 0.100)],
        'Tortellini al Forno': [(paste_tortellini, 0.200), (smantana, 0.100), (branza, 0.050)],

        # DESERT
        'Papanasi cu smantana si dulceata': [(faina, 0.150), (branza_dulce, 0.150), (oua, 1), (smantana, 0.050), (dulceata, 0.050)],
        'Tiramisu': [(piscoturi, 0.100), (mascarpone, 0.100), (oua, 1), (cafea, 0.010)],
        'Clatite cu fineti': [(faina, 0.100), (lapte, 0.100), (oua, 1), (fineti, 0.050)],
        'Lava Cake': [(ciocolata, 0.100), (faina, 0.050), (oua, 1)],
        'Cheesecake': [(biscuiti, 0.100), (crema_branza, 0.150), (dulceata, 0.050)],

        # CIORBE
        'Ciorba de burta': [(burta, 0.200), (smantana, 0.050), (usturoi, 0.010)],
        'Ciorba radauteana': [(piept_pui, 0.200), (smantana, 0.050), (usturoi, 0.010)],
        'Ciorba de vacuta': [(carne_vita, 0.200), (legume_ciorba, 0.100)],

        # COCKTAILS
        'Mojito': [(rom, 0.050), (menta, 10.0), (lime, 0.050)],
        'Margarita': [(tequila, 0.050), (triplu_sec, 0.020), (lime, 0.050)],
        'Cuba Libre': [(rom, 0.050), (cola_sticla, 1), (lime, 0.050)], # assuming mixed with 1 bottle cola
        'Pina Colada': [(rom, 0.050), (suc_ananas, 0.100), (crema_cocos, 0.050)],
        'Aperol Spritz': [(aperol, 0.050), (prosecco, 0.100), (apa_min_sticla, 0.5)], # 0.5 bottle
        'Gin Tonic': [(gin, 0.050), (apa_tonica, 0.200)],

        # CAFEA
        'Espresso': [(cafea, 0.009)],
        'Cappuccino': [(cafea, 0.009), (lapte, 0.150)],
        'Caffe Latte': [(cafea, 0.009), (lapte, 0.250)],
        'Frappe': [(cafea_nes, 0.015), (lapte, 0.100), (frisca, 0.050)],

        # RACORITOARE & BERE (Asociate 1-la-1 pentru a funcționa automat stocul)
        'Apa plata 500ml': [(apa_sticla, 1.0)],
        'Apa minerala 500ml': [(apa_min_sticla, 1.0)],
        'Coca Cola 330ml': [(cola_sticla, 1.0)],
        'Fanta 330ml': [(fanta_sticla, 1.0)],
        'Sprite 330ml': [(sprite_sticla, 1.0)],
        'Limonada cu menta 400ml': [(lamaie, 0.150), (menta, 10.0), (zahar, 0.020)],
        'Fresh de portocale 250ml': [(portocale, 0.500)],

        'Ursus Premium 400ml': [(bere_ursus, 1.0)],
        'Heineken 330ml': [(bere_heineken, 1.0)],
        'Stella Artois 330ml': [(bere_stella, 1.0)],
        'Corona 330ml': [(bere_corona, 1.0)],
    }

    # Assign recipes to products
    products = Product.objects.all()
    count = 0
    for product in products:
        # Mark all products from seed as requiring recipe, just to be sure
        product.requires_recipe = True
        product.save()

        if product.name in recipes_map:
            # Clear existing
            product.recipe_items.all().delete()
            for ing, qty in recipes_map[product.name]:
                RecipeItem.objects.create(
                    product=product,
                    ingredient=ing,
                    quantity=qty
                )
            count += 1
            print(f"Added recipe for {product.name}")
        else:
            print(f"Missing recipe mapping for: {product.name}")

    print(f"\nSuccessfully added recipes to {count} products!")
    print("Toate produsele din meniu ar trebui acum să aibă rețetar!")

if __name__ == '__main__':
    run()
