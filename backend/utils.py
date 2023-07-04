import os
import qrcode
import json

"""
UTILS functions
"""

def create_containers_folder(containers_folder):
    if not os.path.exists(containers_folder):
        os.makedirs(containers_folder)
        print("Папка 'containers' успешно создана!")
    else:
        print("Папка 'containers' уже существует!")

def create_product_types(containers_folder):
    file_path = os.path.join(containers_folder, "product_types.json")
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
        print(f"Файл типов создан по пути {file_path} успешно создан!")
        data_dumper(file_path, data)
    else:
        print(f"Файл типов доступен по пути {file_path}")

def append_product_type():
    pass

def check_existing_type(name: str, data) -> bool:
        for obj in data:
            if obj["name"] == name:
                return True
        return False

def data_loader(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
        return data
    
def data_dumper(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
    
def generate_qr(container_path, next_container_folder):
    filename = f"qr{next_container_folder}.png"
    img = qrcode.make(container_path)
    full_path = os.path.join(container_path, filename)
    img.save(full_path)