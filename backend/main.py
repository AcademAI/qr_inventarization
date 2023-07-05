from fastapi import FastAPI
import uvicorn
import json
import os
import utils

current_dir = os.path.dirname(__file__)
containers_folder = os.path.join(current_dir, "containers")

"""
APP instance
"""
app = FastAPI(
    title="Система инвентаризации"
)

"""
API routes
"""
@app.post("/containers/")
def create_container():
    try:
        next_container_folder = str(len(os.listdir(containers_folder)) + 1)
        container_path = os.path.join(containers_folder, next_container_folder)
        os.makedirs(container_path)
        utils.generate_qr(container_path, next_container_folder)
        utils.load_product_types(current_dir, container_path)
        return {"message": f"Создана новая папка контейнера № {next_container_folder}, QR код доступен по пути: {container_path}"}
    except Exception as e:
        return {"message": "Ошибка создания директории контейнера, проверьте структуру папок"}

@app.get("/containers/{container_id}")
def get_container(container_id: int):
    # получать все изделия из контейнера по id контейнера (qr коду)
    container_id = str(container_id)
    container_path = os.path.join(containers_folder, container_id)
    try:
        with open(os.path.join(container_path, "products.json"), "r") as file:
            products = json.load(file)
        return products
    except Exception as e:
        return {"message": "Ошибка чтения контейнера, возможно в нем нет изделий или он не существует"}
    
@app.post("/products/")
def create_product(name: str, type: str, capacity: int, voltage: int, resistance: int):
    # при создании изделия оно должно добавляться к специальному файлу 'product_types.json' в папке containers
    containers_list = utils.init_container_list(containers_folder)

    for container in containers_list:
        current_container = os.path.join(containers_folder, container)
        file_path = os.path.join(current_container, "products.json")

        data = utils.data_loader(file_path)
        type_exists = utils.check_existing_type(name, data)
        if type_exists == True:
            return {"message": f"Тип уже существует"}
        else:
            last_id = data[-1]["id"]
            new_id = last_id + 1
    
            new_type = {
                    "id": new_id,
                    "name": name,
                    "type": type,
                    "capacity": capacity,
                    "voltage": voltage,
                    "resistance": resistance,
                    "quantity": 0
                }
            data.append(new_type)
            utils.append_product_types(current_dir, data)
            utils.data_dumper(file_path, data)
                
    return {"message": f"Добавлен новый тип изделия во все контейнеры"}

@app.put("/products/{container_id}/{product_id}/increase")
def increase_product_quantity(container_id: int, product_id: int):
    container_id = str(container_id)
    current_container = os.path.join(containers_folder, container_id)
    file_path = os.path.join(current_container, "products.json")
    product_types_path = os.path.join(current_dir, "product_types.json")
    
    try:
        data = utils.data_loader(file_path)
        product_types = utils.data_loader(product_types_path)
    except Exception as e:
        return {"message": "Ошибка чтения контейнера или продукта, возможно он не существует"}
    
    # Поиск продукта по id
    for product_data, product_type in zip(data, product_types):
        if product_data["id"] == product_id:
            product_data["quantity"] += 1
            product_type["quantity"] += 1
            break

    utils.data_dumper(file_path, data)
    utils.data_dumper(product_types_path, product_types)
    
    return {"message": "Количество продукта увеличено"}
    
@app.put("/products/{container_id}/{product_id}/decrease")
def decrease_product_quantity(container_id: int, product_id: int):
    container_id = str(container_id)
    current_container = os.path.join(containers_folder, container_id)
    file_path = os.path.join(current_container, "products.json")
    product_types_path = os.path.join(current_dir, "product_types.json")
    
    try:
        data = utils.data_loader(file_path)
        product_types = utils.data_loader(product_types_path)
    except Exception as e:
        return {"message": "Ошибка чтения контейнера или продукта, возможно он не существует"}
    
    # Поиск продукта по id
    for product_data, product_type in zip(data, product_types):
        if product_data["id"] == product_id:
            product_data["quantity"] -= 1
            product_type["quantity"] -= 1
            break

    utils.data_dumper(file_path, data)
    utils.data_dumper(product_types_path, product_types)
    
    return {"message": "Количество продукта уменьшено"}

@app.get("/products/{name}")
def find_product(name: str):
    # искать изделие по всем контейнерам
    containers_list = utils.init_container_list(containers_folder)
    product_inside = []

    for container in containers_list:
        current_container = os.path.join(containers_folder, container)
        file_path = os.path.join(current_container, "products.json")

        data = utils.data_loader(file_path)

        for product in data:
            if product["name"] == name and product["quantity"] > 0:
                product_inside.append(container)

    return product_inside

if __name__ == "__main__":
    utils.init_containers_folder(containers_folder)
    utils.init_product_types(current_dir)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)