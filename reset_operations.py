import os
import django

# Setează mediul Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from orders.models import Order, OrderGroup, OrderItem, OperationLog
from payments.models import Payment
from tables.models import QRSession
from menu.models import Ingredient, StockReceipt, PurchaseInvoice

def reset_all_operations():
    print("==================================================")
    print(" INCEPE RESETAREA TUTUROR OPERATIUNILOR ")
    print("==================================================")
    
    # 1. Ștergere Plăți
    deleted_payments, _ = Payment.objects.all().delete()
    print(f"✔ Șters {deleted_payments} tranzacții / plăți.")
    
    # 2. Ștergere Articole Comenzi
    deleted_order_items, _ = OrderItem.objects.all().delete()
    print(f"✔ Șters {deleted_order_items} preparate comandate.")
    
    # 3. Ștergere Grupuri de Comenzi
    deleted_order_groups, _ = OrderGroup.objects.all().delete()
    print(f"✔ Șters {deleted_order_groups} grupuri de comenzi.")
    
    # 4. Ștergere Comenzi
    deleted_orders, _ = Order.objects.all().delete()
    print(f"✔ Șters {deleted_orders} comenzi.")
    
    # 5. Ștergere Sesiuni QR
    deleted_sessions, _ = QRSession.objects.all().delete()
    print(f"✔ Șters {deleted_sessions} sesiuni active QR.")
    
    # 6. Ștergere Loguri de Audit / Operare
    deleted_logs, _ = OperationLog.objects.all().delete()
    print(f"✔ Șters {deleted_logs} loguri de operațiuni.")
    
    # 7. Ștergere Recepții de Stoc și NIR-uri (Facturi)
    deleted_receipts, _ = StockReceipt.objects.all().delete()
    print(f"✔ Șters {deleted_receipts} intrări de stoc.")
    
    deleted_invoices, _ = PurchaseInvoice.objects.all().delete()
    print(f"✔ Șters {deleted_invoices} facturi de achiziții (NIR-uri).")
    
    # 8. Resetare Stoc Curent Ingrediente la 0
    updated_ingredients = Ingredient.objects.all().update(current_stock=0)
    print(f"✔ Resetat stocul curent la 0 pentru {updated_ingredients} ingrediente.")
    
    print("==================================================")
    print(" RESETARE COMPLETĂ REUȘITĂ! ")
    print("==================================================")
    print("Am păstrat intacte următoarele date structurale:")
    print(" - Conturile de utilizator (Angajații și Administratorii)")
    print(" - Mesele configurate")
    print(" - Meniul (Produse și Categorii)")
    print(" - Rețetarele aferente produselor")
    print("==================================================")

if __name__ == '__main__':
    reset_all_operations()
