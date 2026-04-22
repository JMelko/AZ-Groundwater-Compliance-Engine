import os

def bare_metal_search(csv_path, target_id):
    if not os.path.exists(csv_path):
        print(f"Cannot find {csv_path}. Check your path.")
        return

    print(f"Initiating bare-metal text scan for {target_id}...")
    
    # We open the file in raw text mode, ignoring encoding errors
    with open(csv_path, 'r', encoding='utf-8', errors='ignore') as file:
        # We grab the headers first so we know what we are looking at
        headers = file.readline().strip()
        
        for line_num, line in enumerate(file, start=2):
            if target_id in line:
                print(f"\n✅ SUCCESS: Well found on Line {line_num}!")
                print("-" * 50)
                print("HEADERS: " + headers)
                print("-" * 50)
                print("RAW ROW: " + line.strip())
                print("-" * 50)
                return
                
    print(f"\n🚨 {target_id} not found in the raw text.")

if __name__ == "__main__":
    RAW_FILE = "data/raw/adwr_wells.csv"
    ANCHOR_WELL = "227120"
    
    bare_metal_search(RAW_FILE, ANCHOR_WELL)