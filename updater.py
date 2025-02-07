import json
import hashlib
import logging
import os
import requests
import traceback as tb

def _is_new_model_available(old_config, new_config):
    curr_version = old_config['mversion']
    latest_version = new_config['mversion']
    return latest_version > curr_version

def _download_binary_file(url, file_path):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(file_path, 'wb') as file:
            for chunk in r.iter_content(chunk_size=8192):
                file.write(chunk)
        logging.info(f"File saved successfully to {file_path}")
        return True
    else:
        logging.warning(f"Failed to download file. Status code: {r.status_code}")
        return False

def _sha256(file_path):
    with open(file_path,"rb") as f:
        bytes = f.read()
        readable_hash = hashlib.sha256(bytes).hexdigest();
    return readable_hash

def _get_local_config():
    with open('config.json') as fp:
        config = json.load(fp)
    return config

config_url = 'https://mayankbhagya.github.io/HelloNN/config.json'
def check_for_updates():
    local_config = _get_local_config()
    try:
        r = requests.get(config_url, timeout=15)
        new_config = r.json()
        return _is_new_model_available(local_config, new_config)
    except Exception as e:
        logging.warning("Failed to update.")
        logging.debug(tb.print_exc())
    return False

def update_model():
    try:
        r = requests.get(config_url, timeout=15)
        new_config = r.json()
    except Exception as e:
        logging.warning("Failed to update.")
        logging.debug(tb.print_exc())
    is_downloaded = _download_binary_file(new_config['murl'], 'tmp.pt')
    if is_downloaded and _sha256('tmp.pt')==new_config['msig']:
        os.rename('tmp.pt', 'model.pt')
        with open('config.json', 'w') as fp:
            json.dump(new_config, fp)
