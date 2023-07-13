import cv2
from kivymd.app import MDApp
from kivy.core.window import Window
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.list import IRightBodyTouch, OneLineAvatarIconListItem, IconLeftWidget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import AsyncImage
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.graphics.texture import Texture
from kivy.properties import StringProperty
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.uix.camera import Camera
from pyzbar import pyzbar
import numpy as np
import controller
'''
class ContainerListItem(IRightBodyTouch, MDBoxLayout):
    adaptive_width = True
'''


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

        self.containerlist_builder(layout)
        self.products = {}

        return layout

    def containerlist_builder(self, layout):
        '''Вроде починили:)'''
        containers_tuple = controller.get_all_containers()

        for container_id, container_data in containers_tuple:
            self.image_paths = controller.get_containers_images(container_id)
            containerItem = OneLineAvatarIconListItem(
                IconLeftWidget(icon="folder", on_press=lambda *args, id=self.image_paths: self.show_image(id)),
                text=f"Контейнер № {container_id}", on_press=lambda *args, id=container_id: self.show_table_popup(id)
            )

            # containerItem.bind(on_release=lambda *args, id=container_id: self.show_table_popup(id))

            layout.ids['containerlist'].add_widget(containerItem)

    # Keep a list of image paths
    # image_paths = []

    def show_image(self, paths):

        # Set current image index
        self.image_index = 0

        # Store paths
        self.image_paths = paths

        image_popup = Popup(title='Фото контейнера', size_hint=(0.8, 0.8))

        # Create image widget
        self.image = AsyncImage(source=self.image_paths[self.image_index])
        self.image.size_hint = (1, 1)

        # Add buttons to scroll images
        left_button = Button(text='Назад', on_press=self.show_prev, size_hint=(0.5, None), height = dp(50))
        right_button = Button(text='Вперед', on_press=self.show_next, size_hint=(0.5, None), height = dp(50))

        # Add to layout
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.image)

        buttons_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height= dp(50))
        buttons_layout.add_widget(left_button)
        buttons_layout.add_widget(right_button)

        layout.add_widget(buttons_layout)

        image_popup.content = layout
        image_popup.open()

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
        image_object = None
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
            print(decoded_objects)

            if len(decoded_objects) != 0:
                # Иначе, если не пустой пойманный массив, декодирует
                last_decoded_object = decoded_objects[0]
                text = last_decoded_object.data.decode('utf-8')

                container_id = text[-1]
                self.is_processing_frame = False
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

        for row in row_data:
            if self.in_list(row):
                temp = []
                for i in row:
                    temp.append(i)

                id_prod = self.get_prod_id(row[0], product_data)
                print(container_id, id_prod)
                controller.increase_product_quantity(container_id=container_id, product_id=id_prod)
                row[-1] += 1  # Increase the quantity by 1
                self.table_layout.update_row(self.table_layout.row_data[id_prod - 1], row)

    def decrease_selected_quantity(self, row_data, container_id, product_data):
        global check_list

        for row in row_data:
            if self.in_list(row):
                temp = []
                for i in row:
                    temp.append(i)

                id_prod = self.get_prod_id(row[0], product_data)
                print(container_id, id_prod)
                controller.decrease_product_quantity(container_id=container_id, product_id=id_prod)
                row[-1] -= 1  # Increase the quantity by 1
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

        table_data = values
        self.table_layout = MDDataTable(
            pos_hint={'center_x': 0.5, 'center_y': 0},
            size_hint=(1, 0.8),
            use_pagination=True,
            rows_num=6,
            check=True,  # Enable row selection with checkboxes
            column_data=[
                ("Название", dp(30)),
                ("Тип", dp(30)),
                ("Количество", dp(30)),
            ],
            row_data=table_data,

        )
        self.table_layout.bind(on_check_press=self.on_check_press)
        close_button = Button(text='Закрыть', size_hint=(1, 0.2))
        close_button.bind(on_press=self.close_popup)

        increase_button = Button(text='Увеличить', size_hint=(1, 0.2))
        increase_button.bind(
            on_press=lambda instance: self.increase_selected_quantity(table_data, container_id, product_data))
        decrease_button = Button(text='Уменьшить', size_hint=(1, 0.2))
        decrease_button.bind(
            on_press=lambda instance: self.decrease_selected_quantity(table_data, container_id, product_data))

        button_layout = GridLayout(cols=3, size_hint=(1, None), height=dp(48))
        button_layout.add_widget(close_button)
        button_layout.add_widget(increase_button)
        button_layout.add_widget(decrease_button)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.table_layout)
        layout.add_widget(button_layout)

        table_popup = Popup(title=f"Содержимое контейнера № {container_id}", content=layout, size_hint=(1, 0.8))
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

    '''
    def on_popup_dismiss(self, instance):
        Clock.schedule_once(self.schedule_next_frame, 0)

    '''

    def open_search_window(self):
        if not (self.is_processing_frame):
            search_layout = BoxLayout(orientation='vertical')
            containers_tuple = controller.get_all_containers()

            # Извлечение значений id из containers_tuple
            ids = [item[0] for item in containers_tuple]

            spinner = Spinner(
                text='Выберите контейнер из списка',
                values=ids,
                size_hint=(None, None),
                size=(200, 50)
            )
            spinner.bind(text=self.on_spinner_select)
            search_layout.add_widget(spinner)

            search_popup = Popup(title='Поиск', content=search_layout, size_hint=(0.6, 0.4))
            search_popup.open()

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


if __name__ == '__main__':
    QRCodeScannerApp().run()