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
        'pizza_margherita_1782636624592.png'
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
