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
    containers_list = []
    containers_list.extend(os.listdir(containers_folder))

    for container in containers_list:
        current_container = os.path.join(containers_folder, container)
        file_path = os.path.join(current_container, "products.json")

        if os.path.exists(file_path):
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
                utils.data_dumper(file_path, data)
        else:   
            data = [ 
                {
                    "id": 1,
                    "name": name,
                    "type": type,
                    "capacity": capacity,
                    "voltage": voltage,
                    "resistance": resistance,
                    "quantity": 0
                }
            ]
            utils.data_dumper(file_path, data)
        
    return {"message": f"Добавлен новый тип изделия во все контейнеры"}

@app.post("/products/{container_id}")
def manage_products(container_id: int, name: str):
    # функция принимает container_id и name, увеличивает и уменьшает количество изделий определенного типа
    container_id = str(container_id)
    product_path = os.path.join(containers_folder, container_id)
    if not os.path.exists(product_path):
        return {"message": f"Контейнера с номером {container_id} не существует, невозможно добавить изделие."}
    
    file_path = os.path.join(product_path, "products.json")

    if os.path.exists(file_path):
        data = utils.data_loader(file_path)
        last_id = data[-1]["id"]
        new_id = last_id + 1

        new_product = {
                "id": new_id,
                "name": name,
                "type": type,
                "capacity": capacity,
                "voltage": voltage,
                "resistance": resistance
            }
        data.append(new_product)
    else:
        data = [
            {
                "id": 1,
                "name": name,
                "type": type,
                "capacity": capacity,
                "voltage": voltage,
                "resistance": resistance
            }
        ]
    
    utils.data_dumper(file_path, data)
    
    return {"message": f"Добавлено изделие в контейнере № {container_id} по пути: {product_path}"}

@app.get("/products/{container_id}")
def find_product(container_id: int, name: str, type: str, capactiy: int, voltage: int, resistance: int):
    # искать изделие по всем контейнерам
    pass


if __name__ == "__main__":
    utils.create_containers_folder(containers_folder)
    utils.create_product_types(containers_folder)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)