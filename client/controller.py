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


def increase_product_quantity(container_id: int, product_id: int):
    url = f"http://127.0.0.1:8000/products/{container_id}/{product_id}/increase"
    response = requests.put(url)
    data = response.json()

    return data


def decrease_product_quantity(container_id: int, product_id: int):
    url = f"http://127.0.0.1:8000/products/{container_id}/{product_id}/decrease"
    response = requests.put(url)
    data = response.json()

    return data


def get_containers_images(container_id: int):
    url = f"http://127.0.0.1:8000/images/{container_id}"
    response = requests.get(url)
    if response.status_code == 200:
        images = response.json()  # получаем байты изображения
        paths = [image['_url'] for image in images]
        return paths
    else:
        print("Ошибка при получении изображений")

def upload_image(container_id: int, image):
    url = f"http://localhost:8000/images/{container_id}"
    response = requests.post(url, files={"image": image})
    return response.json()


def create_product(name: str, _type: str, capacity: int, voltage: int, resistance: int):
    url = "http://127.0.0.1:8000/products/create"
    data = {
        "name": name,
        "type": _type,
        "capacity": capacity,
        "voltage": voltage,
        "resistance": resistance
    }
    response = requests.post(url, json=data)

    return response.json()