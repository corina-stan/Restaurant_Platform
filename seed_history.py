import os
import django
import random
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from accounts.models import User
from menu.models import Category, Product, Ingredient, StockReceipt, PurchaseInvoice, RecipeItem, Supplier
from orders.models import Order, OrderGroup, OrderItem, OperationLog
from payments.models import Payment, ZReport
from tables.models import Table, QRSession

def get_realistic_unit_price(ing):
    name_lower = ing.name.lower()
    
    # Check specific items by name
    if 'mozzarella' in name_lower or 'gorgonzola' in name_lower or 'parmezan' in name_lower or 'cascaval' in name_lower:
        return Decimal(str(round(random.uniform(25.00, 45.00), 2)))
    elif 'salam' in name_lower or 'prosciutto' in name_lower or 'bacon' in name_lower or 'carne' in name_lower or 'piept' in name_lower or 'burta' in name_lower:
        return Decimal(str(round(random.uniform(20.00, 40.00), 2)))
    elif 'rom' in name_lower or 'tequila' in name_lower or 'triplu sec' in name_lower or 'aperol' in name_lower or 'prosecco' in name_lower or 'gin' in name_lower:
        return Decimal(str(round(random.uniform(40.00, 75.00), 2)))
    elif 'sticla' in name_lower or 'apa' in name_lower or 'cola' in name_lower or 'fanta' in name_lower or 'sprite' in name_lower or 'bere' in name_lower:
        return Decimal(str(round(random.uniform(1.80, 4.50), 2)))
    elif 'oua' in name_lower or 'ouă' in name_lower:
        return Decimal(str(round(random.uniform(0.60, 1.10), 2)))
    
    # Check general items by unit
    if ing.unit == 'g':
        return Decimal(str(round(random.uniform(0.04, 0.09), 2)))
    elif ing.unit == 'ml':
        return Decimal(str(round(random.uniform(0.005, 0.015), 2)))
    elif ing.unit == 'kg':
        return Decimal(str(round(random.uniform(4.00, 15.00), 2)))
    elif ing.unit == 'litru':
        return Decimal(str(round(random.uniform(4.00, 12.00), 2)))
    else:
        return Decimal(str(round(random.uniform(2.00, 8.00), 2)))

def clear_operations():
    print("Stergem datele tranzactionale si resetam ID-urile la 1...")
    from django.db import connection
    tables = [
        'payments_payment',
        'payments_zreport',
        'orders_orderitem',
        'orders_ordergroup',
        'orders_order',
        'tables_qrsession',
        'orders_operationlog',
        'menu_stockreceipt',
        'menu_purchaseinvoice',
    ]
    
    truncated = False
    with connection.cursor() as cursor:
        try:
            # Postgres permite truncate cu RESTART IDENTITY pentru resetare secventa
            tables_str = ", ".join(tables)
            cursor.execute(f"TRUNCATE TABLE {tables_str} RESTART IDENTITY CASCADE;")
            truncated = True
            print("✔ Tabelele au fost golite si ID-urile (secventele) resetate la 1.")
        except Exception as e:
            print(f"Info: Nu s-a putut folosi TRUNCATE ({e}). Incercam stergere standard...")
            
    if not truncated:
        ZReport.objects.all().delete()
        Payment.objects.all().delete()
        OrderItem.objects.all().delete()
        OrderGroup.objects.all().delete()
        Order.objects.all().delete()
        QRSession.objects.all().delete()
        OperationLog.objects.all().delete()
        StockReceipt.objects.all().delete()
        PurchaseInvoice.objects.all().delete()
        print("✔ Datele tranzactionale au fost sterse prin ORM.")
        
    # Resetam stocul ingredientelor la 0
    Ingredient.objects.all().update(current_stock=0)
    print("Curatare finalizata cu succes!")

def seed_history():
    print("Incepem generarea istoricului pe 14 zile...")
    
    waiters = list(User.objects.filter(role='waiter'))
    if not waiters:
        print("Eroare: Nu exista ospatari in baza de date! Ruleaza mai intai seed_db.py.")
        return
        
    suppliers = list(Supplier.objects.all())
    if not suppliers:
        print("Eroare: Nu exista furnizori in baza de date! Ruleaza mai intai seed_db.py.")
        return
        
    products = list(Product.objects.filter(is_available=True))
    if not products:
        print("Eroare: Nu exista produse in baza de date! Ruleaza mai intai seed_db.py.")
        return
        
    tables = list(Table.objects.filter(is_active=True))
    if not tables:
        print("Eroare: Nu exista mese active in baza de date! Ruleaza mai intai seed_db.py.")
        return

    ingredients = list(Ingredient.objects.all())
    if not ingredients:
        print("Eroare: Nu exista ingrediente in baza de date! Ruleaza mai intai seed_recipes.py.")
        return

    now = timezone.now()
    
    # 1. Pe ziua -14 adaugam NIR-uri masive pentru toate ingredientele pentru a preveni stocul negativ
    start_date = now - timedelta(days=14)
    print("Generam aprovizionare masiva initiala pe ziua -14...")
    
    inv_date = start_date.date()
    invoice = PurchaseInvoice.objects.create(
        invoice_number="FACT-INIT-001",
        supplier=suppliers[0],
        supplier_name=suppliers[0].name,
        date=inv_date
    )
    # Fortam created_at
    PurchaseInvoice.objects.filter(id=invoice.id).update(created_at=start_date)
    
    # Adaugam log de operare pentru NIR
    desc = f"A fost înregistrată factura de achiziție #{invoice.invoice_number} de la furnizorul '{invoice.supplier_name}', conținând {len(ingredients)} linii de produse recepționate."
    log = OperationLog.objects.create(
        user=None,
        user_name="System",
        user_role="admin",
        order=None,
        order_number="",
        operation_type="Recepție Marfă (NIR)",
        description=desc
    )
    OperationLog.objects.filter(id=log.id).update(created_at=start_date)
    
    for ing_from_list in ingredients:
        ing = Ingredient.objects.get(id=ing_from_list.id)
        if ing.unit == 'g':
            qty = Decimal('5000.000')  # 5 kg of mint
        elif ing.unit == 'ml':
            qty = Decimal('20000.000')  # 20 liters
        else:
            qty = Decimal('200.000') if ing.unit != 'buc' else Decimal('200')
        price = get_realistic_unit_price(ing)
        receipt = StockReceipt.objects.create(
            invoice=invoice,
            ingredient=ing,
            quantity=qty,
            unit_price_without_vat=price,
            vat_rate=9
        )
        StockReceipt.objects.filter(id=receipt.id).update(created_at=start_date)
        
    # Acum parcurgem zilele de la ziua -14 pana la ziua 0 (azi)
    for day_offset in range(14, -1, -1):
        day_date = now - timedelta(days=day_offset)
        print(f"Generam date pentru ziua: {day_date.strftime('%Y-%m-%d')} (acum {day_offset} zile)...")
        
        # A. Aprovizionare periodica la fiecare 3 zile (in afara de prima zi care e deja facuta)
        if day_offset < 14 and day_offset % 3 == 0:
            supplier = random.choice(suppliers)
            invoice_num = f"FACT-SUP-{day_date.strftime('%Y%m%d')}"
            invoice = PurchaseInvoice.objects.create(
                invoice_number=invoice_num,
                supplier=supplier,
                supplier_name=supplier.name,
                date=day_date.date()
            )
            PurchaseInvoice.objects.filter(id=invoice.id).update(created_at=day_date)
            
            sub_ingredients = random.sample(ingredients, k=random.randint(5, min(12, len(ingredients))))
            
            # Adaugam log de operare pentru NIR
            desc = f"A fost înregistrată factura de achiziție #{invoice.invoice_number} de la furnizorul '{invoice.supplier_name}', conținând {len(sub_ingredients)} linii de produse recepționate."
            log = OperationLog.objects.create(
                user=None,
                user_name="System",
                user_role="admin",
                order=None,
                order_number="",
                operation_type="Recepție Marfă (NIR)",
                description=desc
            )
            OperationLog.objects.filter(id=log.id).update(created_at=day_date)
            
            for ing_from_list in sub_ingredients:
                ing = Ingredient.objects.get(id=ing_from_list.id)
                # Determine realistic quantities based on unit and price
                if ing.unit == 'g':
                    qty = Decimal(str(random.randint(500, 1500)))
                elif ing.unit == 'ml':
                    qty = Decimal(str(random.randint(2000, 5000)))
                elif ing.unit == 'buc':
                    qty = Decimal(str(random.randint(30, 80)))
                else:  # kg or litru
                    if price > 15.00:
                        qty = Decimal(str(random.randint(5, 15)))
                    else:
                        qty = Decimal(str(random.randint(10, 30)))
                price = get_realistic_unit_price(ing)
                receipt = StockReceipt.objects.create(
                    invoice=invoice,
                    ingredient=ing,
                    quantity=qty,
                    unit_price_without_vat=price,
                    vat_rate=9
                )
                StockReceipt.objects.filter(id=receipt.id).update(created_at=day_date)

        # B. Comenzi si vanzari zilnice
        is_weekend = day_date.weekday() in [5, 6]  # 5=Sambata, 6=Duminica
        num_orders = random.randint(15, 30) if is_weekend else random.randint(8, 18)
        
        day_payments = []
        
        for o_idx in range(num_orders):
            # Ora comenzii: intre 12:00 si 22:30
            order_hour = random.randint(12, 22)
            order_minute = random.randint(0, 59)
            order_time = day_date.replace(hour=order_hour, minute=order_minute, second=0, microsecond=0)
            
            table = random.choice(tables)
            waiter = random.choice(waiters)
            
            # Sesiune QR
            session = QRSession.objects.create(
                table=table,
                is_active=False,
                closed_at=order_time + timedelta(minutes=random.randint(45, 90))
            )
            QRSession.objects.filter(id=session.id).update(created_at=order_time)
            
            # Comanda
            order = Order.objects.create(
                session=session,
                waiter=waiter,
                status='closed'
            )
            Order.objects.filter(id=order.id).update(
                created_at=order_time,
                updated_at=order_time + timedelta(minutes=random.randint(30, 80))
            )
            
            # Log de Creare Comandă
            log_create = OperationLog.objects.create(
                user=waiter,
                user_name=waiter.username,
                user_role=waiter.role,
                order=order,
                order_number=str(order.id),
                operation_type="Creare Comandă",
                description=f"A fost creată comanda #{order.id} la masa {table.number}."
            )
            OperationLog.objects.filter(id=log_create.id).update(created_at=order_time)
            
            # Grup general
            group = OrderGroup.objects.create(
                order=order,
                name="Masa"
            )
            
            # Selectam intre 2 si 6 produse
            num_products = random.randint(2, 6)
            ordered_products = random.sample(products, k=num_products)
            
            total_amount = Decimal('0.00')
            
            for prod in ordered_products:
                qty = random.randint(1, 3)
                item_total = prod.price * qty
                total_amount += item_total
                
                order_item = OrderItem.objects.create(
                    order=order,
                    group=group,
                    product=prod,
                    quantity=qty,
                    unit_price=prod.price,
                    status='served'
                )
                OrderItem.objects.filter(id=order_item.id).update(
                    created_at=order_time,
                    updated_at=order_item.created_at + timedelta(minutes=random.randint(10, 20))
                )
                
                # Scadem stocul ingredientelor conform retetarului
                if prod.requires_recipe:
                    for recipe in prod.recipe_items.all():
                        ing = Ingredient.objects.get(id=recipe.ingredient.id)
                        ing.current_stock -= (recipe.quantity * Decimal(str(qty)))
                        ing.save()
            
            # Log de Actualizare Comandă (simulată cu probabilitate de 40%)
            if random.random() < 0.4:
                update_time = order_time + timedelta(minutes=random.randint(5, 15))
                log_update = OperationLog.objects.create(
                    user=waiter,
                    user_name=waiter.username,
                    user_role=waiter.role,
                    order=order,
                    order_number=str(order.id),
                    operation_type="Actualizare Comandă",
                    description=f"S-au adăugat produse noi în comanda #{order.id} la masa {table.number}."
                )
                OperationLog.objects.filter(id=log_update.id).update(created_at=update_time)
            
            # Log de Schimbare Status Preparat (pentru primul produs din listă)
            if ordered_products:
                status_time = order_time + timedelta(minutes=random.randint(15, 25))
                target_prod = ordered_products[0]
                log_status = OperationLog.objects.create(
                    user=waiter,
                    user_name=waiter.username,
                    user_role=waiter.role,
                    order=order,
                    order_number=str(order.id),
                    operation_type="Schimbare Status Preparat",
                    description=f"Statusul preparatului '{target_prod.name}' (1x) din comanda #{order.id} a fost schimbat în 'Servit'."
                )
                OperationLog.objects.filter(id=log_status.id).update(created_at=status_time)
                        
            # Plata
            method = random.choices(['cash', 'card', 'ticket'], weights=[40, 50, 10], k=1)[0]
            tip_percent = random.choices([0, 5, 10, 15], weights=[30, 20, 40, 10], k=1)[0]
            tip = (total_amount * Decimal(str(tip_percent)) / Decimal('100')).quantize(Decimal('0.01'))
            
            payment = Payment.objects.create(
                order=order,
                group=group,
                collected_by=waiter,
                method=method,
                amount=total_amount,
                tip=tip,
                status='completed'
            )
            Payment.objects.filter(id=payment.id).update(created_at=order.updated_at)
            
            # Log de operare
            desc = f"A fost inregistrata plata de {total_amount:.2f} lei (+ bacsis {tip:.2f} lei) prin {payment.get_method_display()} pentru comanda #{order.id}."
            log = OperationLog.objects.create(
                user=waiter,
                user_name=waiter.username,
                user_role=waiter.role,
                order=order,
                order_number=str(order.id),
                operation_type="Plată și Închidere",
                description=desc
            )
            OperationLog.objects.filter(id=log.id).update(created_at=order.updated_at)
            
            day_payments.append(payment)

        # C. Generare rapoarte Z zilnice pe ospatari la sfarsitul zilei (ora 23:30)
        z_time = day_date.replace(hour=23, minute=30, second=0, microsecond=0)
        
        # Luam toti ospatarii care au colectat plati in aceasta zi
        waiters_with_payments = set([p.collected_by for p in day_payments if p.collected_by])
        
        for w in waiters_with_payments:
            w_payments = [p for p in day_payments if p.collected_by == w]
            if not w_payments:
                continue
                
            # Calculam agregate
            tot_amt = Decimal('0.00')
            tot_tip = Decimal('0.00')
            
            c_amt = Decimal('0.00')
            card_amt = Decimal('0.00')
            t_amt = Decimal('0.00')
            
            c_tip = Decimal('0.00')
            card_tip = Decimal('0.00')
            t_tip = Decimal('0.00')
            
            v11_gross = Decimal('0.00')
            v11_net = Decimal('0.00')
            v11_amount = Decimal('0.00')
            
            v21_gross = Decimal('0.00')
            v21_net = Decimal('0.00')
            v21_amount = Decimal('0.00')
            
            for p in w_payments:
                amount = p.amount
                tip = p.tip
                tot_amt += amount
                tot_tip += tip
                
                if p.method == 'cash':
                    c_amt += amount
                    c_tip += tip
                elif p.method == 'card':
                    card_amt += amount
                    card_tip += tip
                elif p.method == 'ticket':
                    t_amt += amount
                    t_tip += tip
                    
                # Calcule TVA
                items = OrderItem.objects.filter(order=p.order).exclude(status='rejected')
                for item in items:
                    qty = Decimal(str(item.quantity))
                    price = Decimal(str(item.unit_price))
                    item_gross = qty * price
                    
                    rate = 11
                    if item.product and item.product.category:
                        if item.product.category.department == 'bar':
                            rate = 21
                            
                    if rate == 21:
                        item_net = item_gross / Decimal('1.21')
                        item_vat = item_gross - item_net
                        v21_gross += item_gross
                        v21_net += item_net
                        v21_amount += item_vat
                    else:
                        item_net = item_gross / Decimal('1.11')
                        item_vat = item_gross - item_net
                        v11_gross += item_gross
                        v11_net += item_net
                        v11_amount += item_vat
            
            from django.db.models import Max
            next_num = (ZReport.objects.aggregate(Max('number'))['number__max'] or 0) + 1
            
            z_report = ZReport.objects.create(
                number=next_num,
                waiter=w,
                total_amount=tot_amt,
                total_tip=tot_tip,
                cash_amount=c_amt,
                card_amount=card_amt,
                ticket_amount=t_amt,
                cash_tip=c_tip,
                card_tip=card_tip,
                ticket_tip=t_tip,
                vat_11_gross=v11_gross,
                vat_11_net=v11_net,
                vat_11_amount=v11_amount,
                vat_21_gross=v21_gross,
                vat_21_net=v21_net,
                vat_21_amount=v21_amount,
                payments_count=len(w_payments)
            )
            ZReport.objects.filter(id=z_report.id).update(created_at=z_time)
            
            payment_ids = [p.id for p in w_payments]
            Payment.objects.filter(id__in=payment_ids).update(z_report=z_report)
            
    print("A fost populata baza de date cu istoric pe 14 zile!")

if __name__ == '__main__':
    clear_operations()
    seed_history()
