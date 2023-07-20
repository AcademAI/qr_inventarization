import cv2
from kivymd.app import MDApp
from kivy.core.window import Window
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.list import OneLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivymd.uix.button import MDIconButton
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import AsyncImage
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.graphics.texture import Texture
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.uix.camera import Camera
from pyzbar import pyzbar
import numpy as np
import tempfile
import controller
from PIL import Image as Imagep


class AndroidCamera(Camera):
    camera_resolution = (1280, 720)
    cam_ratio = camera_resolution[0] / camera_resolution[1]


class QRCodeScannerApp(MDApp):
    global check_list
    check_list = []

    def init(self, **kwargs):
        super().init(**kwargs)
        self.selected_rows = []  # List to track selected rows

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"
        layout = Builder.load_file('kvs/main.kv')
        self.cam = layout.ids.a_cam
        self.texture = None
        self.is_processing_frame = False

        screen = layout.ids.screen_with_camera
        screen.bind(on_pre_leave=self.on_screen_leave)
        containers_tuple = controller.get_all_containers()
        containers_tuple = sorted(containers_tuple, key=lambda x: int(x[0]))

        for container_id, container_data in containers_tuple:
            self.containerlist_builder(layout, container_id)
        self.products = {}

        return layout

    def containerlist_builder(self, layout, container_id):
        '''Вроде починили:)'''

        containerItem = OneLineAvatarIconListItem(
            IconLeftWidget(icon="folder", on_press=lambda *args, _id=container_id: self.show_image(_id)),
            text=f"Контейнер № {container_id}", on_press=lambda *args, _id=container_id: self.show_table_popup(_id)
        )
        # Create and add IconRightWidget
        icon_right = IconRightWidget(icon="camera",
                                        on_press=lambda *args, _id=container_id: self.on_icon_right_press(_id))
        containerItem.add_widget(icon_right)

        layout.ids['containerlist'].add_widget(containerItem)

    # Заготовка для съемки контейнера
    def on_icon_right_press(self, _id):
        self.getting_frame = True
        # Set the container ID for which the photo is being taken
        self.container_id = _id

        # Create a popup to show the camera preview
        camera_popup = Popup(title='Фотография контейнера', size_hint=(1, 1))

        # Create the camera widget
        camera = self.cam
        camera.play = True
        camera.resolution = (1280, 720)
        # Create a button to take the photo
        take_photo_button = Button(text='Сфотографировать', size_hint=(0.5, None), height=dp(50))
        take_photo_button.bind(on_press=lambda *args: Clock.schedule_once( lambda inst: self.take_photo(camera, camera_popup), 0.5))

        # Create a layout to hold the camera and the button
        layout = BoxLayout(orientation='vertical')

        layout.add_widget(take_photo_button)
        close_button = MDIconButton(icon='close')
        close_button.bind(on_release=lambda instance: self.foto_dismiss(camera_popup,camera))
        layout.add_widget(close_button)

        imn = AsyncImage()
        layout.add_widget(imn)
        Clock.schedule_interval(lambda dt: self.get_frame(camera, imn), 1 / 30.0)  # Update the frame at 30 FPS
        # Add the layout to the popup
        camera_popup.content = layout

        # Open the popup
        camera_popup.open()

    def foto_dismiss(self,camera_popup,camera):
        self.getting_frame = False
        camera.play = False
        camera_popup.dismiss()

    def get_frame(self, camera, imn):
        if not self.getting_frame:
            return
        # Capture the image from the camera
        image = camera.export_as_image()
        # Convert the image to a numpy array for use with cv2
        w, h = image._texture.size
        image_np = np.frombuffer(image._texture.pixels, 'uint8').reshape(h, w, 4)
        # Rotate the image by 180 degrees
        image_np = cv2.flip(image_np, -1)
        # Flip the image horizontally
        image_np = cv2.flip(image_np, 1)
        # Convert the numpy array back to an image
        image = Imagep.fromarray(np.uint8(image_np))
        texture = Texture.create(size=image.size)
        texture.blit_buffer(image.tobytes(), colorfmt='rgba')
        imn.texture = texture


    def take_photo(self, camera, camera_popup):
        # Capture the image from the camera
        image = camera.export_as_image()


        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = temp_dir + '/image.png'
            image.save(temp_file_path)
            with open(temp_file_path, 'rb') as temp_file:
                image_data = temp_file.read()
        # Save the image to a temporary file

            # Do something with the image file, e.g., upload to server
            controller.upload_image(self.container_id, image_data)
            camera.play = False
            # Close the camera popup
            self.foto_dismiss(camera_popup,camera)

    def update_camera_widget(self):
        # Find the camera widget that's currently displayed on the screen
        for widget in Window.children:
            if isinstance(widget, AndroidCamera):
                self.cam = widget
                break

    def submit_values(self):
        name = self.root.ids.name_input.text
        _type = self.root.ids.type_input.text
        capacity = int(self.root.ids.capacity_input.text)
        voltage = int(self.root.ids.voltage_input.text)
        resistance = int(self.root.ids.resistance_input.text)
        controller.create_product(name, _type, capacity, voltage, resistance)

    def show_image(self,_id):
        # Set current image index
        self.image_index = 0
        # Store paths
        self.image_paths = controller.get_containers_images(_id)
        image_popup = Popup(title='Фото контейнера', size_hint=(1, 1))
        # Create image widget
        self.image = AsyncImage(source=self.image_paths[self.image_index])
        self.image.size_hint = (1, 1)

        # Add buttons to scroll images
        left_button = Button(text='Назад', on_press=self.show_prev, size_hint=(0.5, None), height=dp(50))
        right_button = Button(text='Вперед', on_press=self.show_next, size_hint=(0.5, None), height=dp(50))

        # Add a button to delete the image
        delete_button = Button(text='Удалить', on_press = self.delete_image, size_hint=(1, None), height=dp(50))

        # Add to layout
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.image)

        buttons_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(50))
        buttons_layout.add_widget(left_button)
        buttons_layout.add_widget(right_button)
        close_button = MDIconButton(icon='close', on_release=image_popup.dismiss)
        buttons_layout.add_widget(close_button)
        layout.add_widget(buttons_layout)
        layout.add_widget(delete_button)
        image_popup.content = layout
        image_popup.open()

    def delete_image(self, *args):
        # Delete the current image
        if self.image_paths and len(self.image_paths) > 0:
            img_path = self.image_paths[self.image_index]
            param = img_path.split('/')
            controller.delete_image(int(param[-2]),param[-1])
            self.image.source = ''

            # Remove the deleted image path from the list
            self.image_paths.remove(img_path)
            if len(self.image_paths) > 0:
                # Show the next image if available
                self.show_next()
            else:
                # Close the popup if there are no more images to show
                self.close_popup()

    def show_prev(self, *args):
        self.image_index -= 1
        if self.image_index < 0:
            self.image_index = len(self.image_paths) - 1

        self.image.source = self.image_paths[self.image_index]

    def show_next(self, *args):
        self.image_index = (self.image_index + 1) % len(self.image_paths)
        self.image.source = self.image_paths[self.image_index]

    def start_scanning(self, *args):
        if self.is_processing_frame:
            return
        self.is_processing_frame = True
        self.cam.play = True
        Clock.schedule_once(self.process_frame, 0.5)

    def process_frame(self, dt):
        if not self.cam.play:
            self.cam.play = True
        image_object = self.cam.export_as_image()
        if image_object:
            image_object = self.cam.export_as_image()
            w, h = image_object._texture.size
            frame = np.frombuffer(image_object._texture.pixels, 'uint8').reshape(h, w, 4)
            # Преобразование кадра в оттенки серого
            gray = cv2.cvtColor(frame, cv2.COLOR_RGBA2GRAY)

            # Распознавание QR-кодов
            decoded_objects = pyzbar.decode(gray)

            if len(decoded_objects) != 0:
                # Иначе, если не пустой пойманный массив, декодирует
                last_decoded_object = decoded_objects[0]
                text = last_decoded_object.data.decode('utf-8')
                text = text.split("\\")

                container_id = int(text[-1])

                self.is_processing_frame = False
                self.cam.play = False
                self.show_table_popup(container_id)

        if self.is_processing_frame:
            Clock.schedule_once(self.process_frame, 0)


    def in_list(self, row):
        global check_list
        for i in check_list:
            # проверяем на совпадение по названию
            if i[0] == row[0]:
                return True
        return False

    def get_prod_id(self, name, product_data):
        for product in product_data:
            if name == product['name']:
                return product['id']

    def increase_selected_quantity(self, row_data, container_id, product_data):
        global check_list
        quantity = int(self.quantity_input.text)
        for row in row_data:
            if self.in_list(row):
                temp = []
                for i in row:
                    temp.append(i)

                id_prod = self.get_prod_id(row[0], product_data)
                controller.increase_product_quantity(container_id=container_id, product_id=id_prod, quantity=quantity)
                row[-1] += quantity  # Increase the quantity by quantity
                self.table_layout.update_row(self.table_layout.row_data[id_prod - 1], row)

    def decrease_selected_quantity(self, row_data, container_id, product_data):
        global check_list
        quantity = int(self.quantity_input.text)
        for row in row_data:
            if self.in_list(row):
                temp = []
                for i in row:
                    temp.append(i)

                id_prod = self.get_prod_id(row[0], product_data)
                controller.decrease_product_quantity(container_id=container_id, product_id=id_prod, quantity=quantity)
                row[-1] -= quantity  # Increase the quantity by quantity
                self.table_layout.update_row(self.table_layout.row_data[id_prod - 1], row)

    def show_table_popup(self, text):
        global check_list
        check_list = []
        container_id = text
        product_data = controller.get_container(container_id)

        values = []

        for product in product_data:
            row_data = [product['name'], product['type'], product['quantity']]
            values.append(row_data)

        table_data = sorted(values, key=lambda x: x[2])
        table_data = table_data[::-1]
        self.table_layout = MDDataTable(
            pos_hint={'center_x': 0.5, 'center_y': 0},
            size_hint=(1, 0.8),
            use_pagination=True,
            rows_num=10,
            check=True,  # Enable row selection with checkboxes
            column_data=[
                ("Название", dp(30)),
                ("Тип", dp(30)),
                ("Количество", dp(30)),
            ],
            row_data=table_data,
            sorted_on="Количество",
            sorted_order="ASC",
        )
        self.table_layout.bind(on_check_press=self.on_check_press)
        close_button = MDIconButton(icon='close', size_hint=(None, None), size=(dp(48), dp(48)))
        close_button.bind(on_press=self.close_popup)
        self.quantity_input = TextInput(text='1', size_hint=(None, None),size=(dp(48), dp(48)))
        increase_button = Button(text='Увеличить', size_hint=(1, 0.2))
        increase_button.bind(
            on_press=lambda instance: self.increase_selected_quantity(table_data, container_id, product_data))
        decrease_button = Button(text='Уменьшить', size_hint=(1, 0.2))
        decrease_button.bind(
            on_press=lambda instance: self.decrease_selected_quantity(table_data, container_id, product_data))

        button_layout = GridLayout(cols=6, size_hint=(1, None), height=dp(48))

        folder_button = MDIconButton(icon='folder', theme_text_color='Custom')
        folder_button.bind(on_press = lambda instance: self.show_image(container_id))  # Add on_press callback
        camera_button = MDIconButton(icon='camera', theme_text_color='Custom')
        camera_button.bind(on_press = lambda instance: self.on_icon_right_press(int(container_id)))  # Add on_press callback

        button_layout.add_widget(folder_button)
        button_layout.add_widget(camera_button)
        button_layout.add_widget(close_button)
        button_layout.add_widget(increase_button)
        button_layout.add_widget(self.quantity_input)
        button_layout.add_widget(decrease_button)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.table_layout)
        layout.add_widget(button_layout)
        table_popup = Popup(title=f"Содержимое контейнера № {container_id}", content=layout, size_hint=(1, 1))
        table_popup.bind(on_press=self.close_popup)
        table_popup.open()
        self.cam.play = False
        self.is_processing_frame = False

    def on_check_press(self, instance_table, current_row):
        global check_list
        '''Called when the check box in the table row is checked.'''
        for i in check_list:
            if i[0] == current_row[0] and i[1] == current_row[1]:
                check_list.remove(i)
                return
        check_list.append(current_row)

    def close_popup(self, instance):
        global check_list
        check_list = []
        instance.parent.parent.parent.parent.parent.dismiss()


    def open_search_window(self):
        self.search_containers(self.root.ids.search_input.text)

    def create_container(self):
        controller.create_container()
        containers_tuple = controller.get_all_containers()
        containers_tuple = sorted(containers_tuple, key=lambda x: int(x[0]))
        container_id=containers_tuple[-1][0]
        self.containerlist_builder(self.root,container_id)

    def on_spinner_select(self, instance, text):
        self.show_table_popup(text)

    def change_quantity(self, label, change):
        quantity = int(label.text)
        quantity += change
        label.text = str(quantity)

    def on_stop(self):
        self.cam.play = False
        self.is_processing_frame = False

    def on_screen_leave(self, *args):
        self.on_stop()

    def search_containers(self, search_text):
        if search_text=="":
            containerlist = self.root.ids.containerlist
            containerlist.clear_widgets()
            containers = controller.get_all_containers()
            for _id, data in containers:
                self.containerlist_builder(self.root, _id)

        else:
            # Get all containers
            containerlist = self.root.ids.containerlist
            containerlist.clear_widgets()
            containers = controller.get_all_containers()

            # Filter containers
            filtered = []
            for _id, data in containers:
                for product in data['products']:
                    if product['name'] == search_text and product['quantity'] > 0:
                        self.containerlist_builder(self.root, _id)
                        filtered.append((_id, data))
                        break


if __name__ == '__main__':
    QRCodeScannerApp().run()
