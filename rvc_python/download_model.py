import subprocess
import os
import json
import glob
from tqdm import tqdm
from pathlib import Path
import requests

def download_rvc_models(this_dir):
    folder = os.path.join(this_dir,'base_model')
    
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    files = {
        "hubert_base.pt": "https://huggingface.co/Daswer123/RVC_Base/resolve/main/hubert_base.pt",
        "rmvpe.pt": "https://huggingface.co/Daswer123/RVC_Base/resolve/main/rmvpe.pt",
        "rmvpe.onnx": "https://huggingface.co/Daswer123/RVC_Base/resolve/main/rmvpe.onnx"
    }
    
    for filename, url in files.items():
        file_path = os.path.join(folder, filename)
    
        if not os.path.exists(file_path):
            print(f'File {filename} not found, start loading...')
    
            response = requests.get(url)
    
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print(f'File {filename} successfully loaded.')
            else:
                print(f'f {filename}.')
