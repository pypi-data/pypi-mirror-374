
import os
import zipfile
import urllib.request
import sys
import subprocess
import tempfile
import shutil
import re
import importlib
def get_layer_from_api_tl(api_tl_path):
    #Get LAYER version from api.tl file
    try:
        with open(api_tl_path, 'r', encoding='utf-8') as f:
            content = f.read()
        layer_match = re.search(r'// LAYER (\d+)', content)
        if layer_match:
            return int(layer_match.group(1))
        return None
    except Exception as e:
        print(f"[snakegram_up]:Error reading api.tl: {e}")
        return None

def download_api_tl(temp_dir):
    #Download api.tl file once to temporary directory
    api_tl_url = "https://github.com/telegramdesktop/tdesktop/raw/dev/Telegram/SourceFiles/mtproto/scheme/api.tl"
    api_tl_path = os.path.join(temp_dir, "api.tl")
    
    try:
        urllib.request.urlretrieve(api_tl_url, api_tl_path)
        return api_tl_path
    except Exception as e:
        print(f"[snakegram_up]:Error downloading api.tl: {e}")
        return None

def download_and_update_snakegram(api_tl_path, latest_layer):
    #Download and update snakegram source with pre-downloaded api.tl
    
    snakegram_zip_url = "https://github.com/mivmi/snakegram/archive/dev.zip"
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
        zip_path = tmp_file.name
    
    try:
        # Download snakegram source
        urllib.request.urlretrieve(snakegram_zip_url, zip_path)
        
        # Extract to temporary directory
        extract_dir = os.path.join(os.path.dirname(__file__), "snakegram_temp")
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Find snakegram folder
        extracted_folders = os.listdir(extract_dir)
        snakegram_folder = None
        for folder in extracted_folders:
            if folder.startswith('snakegram'):
                snakegram_folder = os.path.join(extract_dir, folder)
                break
        
        if not snakegram_folder:
            print("[snakegram_up]:snakegram folder not found in extracted files")
            return False
        
        # Copy pre-downloaded api.tl to snakegram
        target_api_tl_path = os.path.join(snakegram_folder, "builder", "resource", "schema.tl")
        os.makedirs(os.path.dirname(target_api_tl_path), exist_ok=True)
        shutil.copy(api_tl_path, target_api_tl_path)
        
        # Install snakegram
        setup_py = os.path.join(snakegram_folder, "setup.py")
        if os.path.exists(setup_py):
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", ".", "--force-reinstall"],
                capture_output=True,
                text=True,
                cwd=snakegram_folder
            )
            
            if result.returncode == 0:
              try:
                snakegram = force_reload_snakegram()
                import snakegram
                print(f"[snakegram_up]:snakegram updated successfully to layer {snakegram.tl.LAYER}")
                return True
              except ImportError:
                return False   
            else:
                print(f"[snakegram_up]:Installation failed: {result.stderr}")
                return False
        else:
            print("[snakegram_up]:setup.py not found in snakegram directory")
            return False
            
    except Exception as e:
        print(f"[snakegram_up]:Error during snakegram update: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up temporary files
        try:
            os.unlink(zip_path)
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir, ignore_errors=True)
        except:
            pass
def force_reload_snakegram():
    to_delete = [name for name in sys.modules if name.startswith("snakegram.")]
    for name in to_delete:
        sys.modules.pop(name, None)
    sys.modules.pop("snakegram", None)
    snakegram = importlib.import_module("snakegram")
    return snakegram
def chack():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Download api.tl once
        api_tl_path = download_api_tl(temp_dir)
        if not api_tl_path:
            return
        
        # Check layer version
        latest_layer = get_layer_from_api_tl(api_tl_path)
        if not latest_layer:
            print("[snakegram_up]:Could not determine latest layer")
            return
            
        try:
            from snakegram.tl import LAYER
            current_layer = LAYER
            if current_layer < latest_layer:
                print(f"[snakegram_up]:Updating snakegram from layer {current_layer} to {latest_layer}...")
                success = download_and_update_snakegram(api_tl_path, latest_layer)
                if not success:
                    print("[snakegram_up]:Failed to update snakegram")
                    return
            else:
                print("[snakegram_up]:snakegram is up to date!")
                return
                
        except ImportError:
            print("[snakegram_up]:snakegram not found, installing latest version...")
            success = download_and_update_snakegram(api_tl_path, latest_layer)
            if not success:
                raise ImportError("[snakegram_up]:Failed to install snakegram")
chack()



