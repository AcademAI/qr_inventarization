import requests

def get_all_containers():
    url = "http://127.0.0.1:8000/containers/"
    response = requests.get(url)
    data = response.json()
    
    # Преобразование словаря в кортеж
    result = tuple(data.items())
    
    return result

def get_container(container_id):
    url = f"http://127.0.0.1:8000/containers/{container_id}"
    response = requests.get(url)
    data = response.json()
    
    return data