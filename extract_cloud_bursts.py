import os
import glob
import h5py
import numpy as np
import pandas as pd

# --- CONFIGURATION ---
DATA_DIR = "./NASA_IMERG_Data/"  # Folder where your 480 files are
OUTPUT_CSV = "cloud_burst_events.csv"

# The IMD defines a cloud burst as > 100mm/hr. However, since satellite data is an average 
# over a 10kmx10km grid, it often underestimates the pure peak of the burst. 
# We will use 50.0 mm/hr as our threshold to capture extreme convection.
THRESHOLD = 50.0  

def extract_bursts():
    # Find all HDF5 files in the directory
    hdf5_files = glob.glob(os.path.join(DATA_DIR, "*.HDF5"))
    print(f"Starting scan of {len(hdf5_files)} NASA files...")
    
    records = []
    
    for count, file_path in enumerate(hdf5_files, 1):
        filename = os.path.basename(file_path)
        
        # 1. Parse the Date and Time from the NASA filename
        # Example: 3B-HHR.MS.MRG.3IMERG.20230810-S233000-E235959...
        try:
            parts = filename.split('.')
            date_time_part = parts[4] 
            
            date_str = date_time_part.split('-')[0]      # 20230810
            time_str = date_time_part.split('-')[1][1:]  # 233000 
            
            # Format nicely for pandas later
            timestamp = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]} {time_str[:2]}:{time_str[2:4]}:{time_str[4:]}"
        except IndexError:
            continue # Skip files that don't match the NASA standard naming
            
        # 2. Open the file and extract the heavy rain
        try:
            with h5py.File(file_path, 'r') as f:
                # Transpose gives us a [Latitude, Longitude] matrix grid
                precip = f['Grid']['precipitation'][0, :, :].T
                lats = f['Grid']['lat'][:]
                lons = f['Grid']['lon'][:]
                
                # NumPy magic to instantly find the coordinates of any extreme rainfall
                y_indices, x_indices = np.where(precip >= THRESHOLD)
                
                # If we found extreme rain, record exactly when and where it happened
                for y, x in zip(y_indices, x_indices):
                    rainfall = precip[y, x]
                    records.append({
                        "Timestamp": timestamp,
                        "Latitude": round(float(lats[y]), 4),
                        "Longitude": round(float(lons[x]), 4),
                        "Precipitation_mm_hr": round(float(rainfall), 2),
                        "CloudBurst_Flag": 1
                    })
                    
        except Exception as e:
            print(f"Error reading inside {filename}: {e}")
            
        # Print a progress update every 50 files
        if count % 50 == 0:
            print(f"Processed {count}/{len(hdf5_files)} files...")

    # 3. Save everything to a perfect, ML-ready CSV
    if records:
        df = pd.DataFrame(records)
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"\n✅ SUCCESS: Found {len(records)} extreme convection events!")
        print(f"✅ Saved results to: {OUTPUT_CSV}")
    else:
        print(f"\n❌ NO EVENTS FOUND. The highest rain didn't cross {THRESHOLD} mm/hr.")
        print("Try lowering the THRESHOLD at the top of the script!")

if __name__ == "__main__":
    extract_bursts()
