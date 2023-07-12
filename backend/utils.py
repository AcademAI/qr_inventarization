import os
import qrcode
import json
import time
import logging

#TODO дописать логирование с временем в нужные функции

"""
UTILS functions
"""

def init_containers_folder(containers_folder):
    # создает папку контейнеров
    if not os.path.exists(containers_folder):
        os.makedirs(containers_folder)
        print("Папка 'containers' успешно создана!")
    else:
        print("Папка 'containers' уже существует!")

def init_product_types(current_dir):
    # иницаилизирует все базовые типы в product_types.json
    file_path = os.path.join(current_dir, "product_types.json")
    if not os.path.exists(file_path):
        data = [ 
                {
                    "id": 1,
                    "name": "кон-1",
                    "type": "конденсатор",
                    "capacity": 550,
                    "voltage": 220,
                    "resistance": 5,
                    "quantity": 0
                },
                {
                    "id": 2,
                    "name": "кон-2",
                    "type": "конденсатор",
                    "capacity": 440,
                    "voltage": 220,
                    "resistance": 3,
                    "quantity": 0
                },
                {
                    "id": 3,
                    "name": "тир-1",
                    "type": "тиристор",
                    "capacity": 110,
                    "voltage": 220,
                    "resistance": 5,
                    "quantity": 0
                },
                {
                    "id": 4,
                    "name": "тир-2",
                    "type": "тиристор",
                    "capacity": 120,
                    "voltage": 220,
                    "resistance": 4,
                    "quantity": 0
                },
                {
                    "id": 5,
                    "name": "дио-1",
                    "type": "диод",
                    "capacity": 50,
                    "voltage": 220,
                    "resistance": 3,
                    "quantity": 0
                },
                {
                    "id": 6,
                    "name": "дио-2",
                    "type": "диод",
                    "capacity": 55,
                    "voltage": 220,
                    "resistance": 3,
                    "quantity": 0
                },
            ]
        print(f"Файл типов по пути {file_path} успешно создан!")
        data_dumper(file_path, data)
    else:
        print(f"Файл типов доступен по пути {file_path}")

def init_container_list(containers_folder):
    # создает список существующих контейнеров ['1','2','3'...]
    containers_list = []
    containers_list.extend(os.listdir(containers_folder))
    return containers_list

def append_product_types(current_dir, data):
    # при создании нового типа добавляет его к product_types.json
    file_path = os.path.join(current_dir, "product_types.json")
    data_dumper(file_path, data)
    
def load_product_types(current_dir, container_path):
    # при создании контейнера загружает в products.json все типы из product_types.json
    product_types_path = os.path.join(current_dir, "product_types.json")
    file_path = os.path.join(container_path, "products.json")

    data = data_loader(product_types_path)
    for product in data:
        product["quantity"] = 0
        
    data_dumper(file_path, data)
    
def check_existing_type(name: str, data) -> bool:
    # проверка имени объекта на соответствие существующим
    for obj in data:
        if obj["name"] == name:
            return True
    return False

def data_loader(file_path):
    # загрузка данных из json
    with open(file_path, "r") as f:
        data = json.load(f)
        return data
    
def data_dumper(file_path, data):
    # выгрузка данных в json
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
    
def generate_qr(container_path, next_container_folder):
    # генерация qr кода на основе пути к контейнеру (последний символ - id)
    filename = f"qr{next_container_folder}.png"
    img = qrcode.make(container_path)
    full_path = os.path.join(container_path, filename)
    img.save(full_path)