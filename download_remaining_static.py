import os
import urllib.request

def download_file(url, filepath):
    print(f"Descarcam {url} la {filepath}...")
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    with urllib.request.urlopen(req, timeout=15) as response, open(filepath, 'wb') as f:
        f.write(response.read())

def main():
    dest_dir = os.path.join("menu", "static", "products")
    os.makedirs(dest_dir, exist_ok=True)
    
    mappings = {
        'cafea_cappuccino_static.png': 'https://images.unsplash.com/photo-1572442388796-11668a67e53d?w=600&auto=format&fit=crop',
        'cafea_latte_static.png': 'https://images.unsplash.com/photo-1541167760496-1628856ab772?w=600&auto=format&fit=crop',
        'cafea_frappe_static.png': 'https://images.unsplash.com/photo-1578314675249-a6910f80cc4e?w=600&auto=format&fit=crop',
        'racoritoare_coca_cola_static.png': 'https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=600&auto=format&fit=crop',
        'racoritoare_apa_plata_static.png': 'https://images.unsplash.com/photo-1523362628745-0c100150b504?w=600&auto=format&fit=crop',
        'racoritoare_limonada_static.png': 'https://images.unsplash.com/photo-1621263764928-df1444c5e859?w=600&auto=format&fit=crop',
    }
    
    copied = 0
    for filename, url in mappings.items():
        filepath = os.path.join(dest_dir, filename)
        if not os.path.exists(filepath):
            try:
                download_file(url, filepath)
                copied += 1
            except Exception as e:
                print(f"Eroare la descarcarea {filename}: {e}")
        else:
            print(f"Fisierul {filename} exista deja in static.")
            
    print(f"\nFinalizat! S-au descarcat {copied} imagini in {dest_dir}.")

if __name__ == '__main__':
    main()
