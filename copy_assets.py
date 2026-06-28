import os
import shutil

def main():
    src_dir = r"C:\Users\stanc\.gemini\antigravity-ide\brain\8428fc7b-3663-4f3d-bced-6f724335a294"
    dest_dir = os.path.join("menu", "static", "products")
    
    os.makedirs(dest_dir, exist_ok=True)
    
    files_to_copy = [
        'papanasi_1782635701220.png',
        'ciorba_de_burta_1782635715229.png',
        'ciorba_radauteana_1782635728708.png',
        'ciorba_de_vacuta_1782635745600.png',
        'clatite_cu_fineti_1782635760819.png',
        'cheesecake_1782635772898.png',
        'fanta_1782635787600.png',
        'sprite_1782635800852.png',
        'apa_minerala_1782635817566.png',
        'fresh_portocale_1782635830406.png',
        'tiramisu_1782635846036.png',
        'lava_cake_1782635858736.png',
        'bere_ursus_1782636562532.png',
        'bere_heineken_1782636579595.png',
        'bere_stella_1782636596274.png',
        'bere_corona_1782636610484.png',
        'pizza_margherita_1782636624592.png',
        'cocktail_mojito_1782669572600.png',
        'cocktail_margarita_1782669587044.png',
        'cocktail_cuba_libre_1782669600661.png',
        'cocktail_pina_colada_1782669612557.png',
        'cocktail_aperol_spritz_1782669625472.png',
        'cocktail_gin_tonic_1782669641120.png',
        'pizza_diavola_1782669886242.png',
        'pizza_quattro_formaggi_1782669898858.png',
        'pizza_prosciutto_funghi_1782669910856.png',
        'pizza_capricciosa_1782669923729.png',
        'pizza_vegetariana_1782669936827.png',
        'pasta_carbonara_1782670027641.png',
        'pasta_milanese_1782670040451.png',
        'pasta_arrabiata_1782670054626.png',
        'pasta_bolognese_1782670068692.png',
        'pasta_tortellini_1782670083750.png',
        'cafea_espresso_1782670227502.png',
        'cafea_cappuccino_static.png',
        'cafea_latte_static.png',
        'cafea_frappe_static.png',
        'racoritoare_coca_cola_static.png',
        'racoritoare_apa_plata_static.png',
        'racoritoare_limonada_static.png'
    ]
    
    copied_count = 0
    for file_name in files_to_copy:
        src_path = os.path.join(src_dir, file_name)
        dest_path = os.path.join(dest_dir, file_name)
        
        if os.path.exists(src_path):
            shutil.copy(src_path, dest_path)
            print(f"Copiat: {file_name} -> {dest_path}")
            copied_count += 1
        else:
            print(f"Avertisment: Nu s-a gasit {src_path}")
            
    print(f"\nFinalizat! S-au copiat {copied_count} imagini in {dest_dir}.")
    print("Acum puteti adauga aceste imagini in Git Desktop pentru a le avea pe orice alt calculator.")

if __name__ == '__main__':
    main()
