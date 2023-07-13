from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    # Добавьте дополнительные разрешенные источники (origins) в список
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

"""
API routes
"""
@app.post("/containers/create")
def create_container():
    try:
        next_container_folder = str(len(os.listdir(containers_folder)) + 1)
        container_path = os.path.join(containers_folder, next_container_folder)
        image_folder = os.path.join(container_path, "images")
        os.makedirs(container_path)
        os.makedirs(image_folder)
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
    
@app.get("/containers/")
def get_all_containers():
    # получаем все контейнеры в формате словаря {container_id: путь}
    containers_list = utils.init_container_list(containers_folder)
    containers_dict = {}

    for container in containers_list:
        current_container_path = os.path.join(containers_folder, container)
        container_data = {
            "path": current_container_path,
            "products": []
        }

        # получаем путь к файлу products.json
        file_path = os.path.join(current_container_path, "products.json")
        # загружаем данные из файла products.json
        products_data = utils.data_loader(file_path)
        # добавляем данные в список products контейнера
        container_data["products"] = products_data

        containers_dict[container] = container_data

    return containers_dict
    
@app.post("/products/create")
def create_product(product: dict):
    name = product.get("name")
    type = product.get("type")
    capacity = product.get("capacity")
    voltage = product.get("voltage")
    resistance = product.get("resistance")
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
                
    return {"message": "Добавлен новый тип изделия во все контейнеры"}

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


@app.post("/images/{container_id}")
def add_image(container_id: int, image: UploadFile = File(...)):
    container_id = str(container_id)
    current_container = os.path.join(containers_folder, container_id)
    image_folder = os.path.join(current_container, "images")

    try:
        img_num = len(os.listdir(image_folder)) + 1
        img_name = f"{img_num}.png"
        img_path = os.path.join(image_folder, img_name)
        contents = image.file.read()

        with open(img_path, "wb") as f:
            f.write(contents)
        
    except Exception as e:
        return {"message": "Ошибка загрузки фотографии"}
    
    finally:
        image.file.close()
        return {"message": f"Фотография сохранена в контейнер {container_id}"}
    
@app.get("/images/{container_id}/{image_name}")
def get_image(container_id: int, image_name: str):
    container_id = str(container_id)
    current_container = os.path.join(containers_folder, container_id)
    image_folder = os.path.join(current_container, "images")
    image_path = os.path.join(image_folder, image_name)

    return FileResponse(image_path, media_type="image/png")
    
@app.get("/images/{container_id}")
def get_images(container_id: int, request: Request):
    container_id = str(container_id)
    current_container = os.path.join(containers_folder, container_id)
    image_folder = os.path.join(current_container, "images")

    image_urls = []
    for filename in os.listdir(image_folder):
        if filename.endswith(".png"):
            image_url = request.url_for("get_image", container_id=container_id, image_name=filename)
            image_urls.append(image_url)

    return image_urls

    

if __name__ == "__main__":
    utils.init_containers_folder(containers_folder)
    utils.init_product_types(current_dir)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)