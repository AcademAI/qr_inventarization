import cv2
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from pyzbar import pyzbar
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.metrics import dp
from kivy.clock import Clock
from kivymd.uix.list import OneLineListItem

import controller


class QRCodeScannerApp(MDApp):
    global check_list
    check_list = []

    def init(self, **kwargs):
        super().init(**kwargs)
        self.selected_rows = []  # List to track selected rows

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"
        layout = Builder.load_file('main.kv')
        self.image = layout.ids.image
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.texture = None
        self.is_processing_frame = False


        return layout

    def start_scanning(self, *args):
        if self.is_processing_frame:
            return
        self.is_processing_frame = True
        Clock.schedule_once(self.process_frame, 0)

    def process_frame(self, dt):

        ret, frame = self.capture.read()

        if ret:
            # Преобразование кадра в оттенки серого
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Распознавание QR-кодов
            decoded_objects = pyzbar.decode(gray)
            print(decoded_objects)

            if len(decoded_objects) == 0:
                # Если массивы пустые, то выполняет отрисовку кадров
                buf = cv2.flip(frame, 0).tostring()
                self.texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                self.texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.image.texture = self.texture
            else:
                # Иначе, если не пустой пойманный массив, декодирует
                last_decoded_object = decoded_objects[0]
                text = last_decoded_object.data.decode('utf-8')

                container_id = text[-1]
                self.is_processing_frame = False
                self.show_table_popup(container_id)

        if self.is_processing_frame:
            Clock.schedule_once(self.process_frame, 0)

    def in_list(self,row):
        global check_list
        for i in check_list:
            # проверяем на совпадение по названию
            if i[0] == row[0]:
                return True
        return False
    def get_prod_id(self,name,product_data):
        for product in product_data:
            if name == product['name']:
                return product['id']
    def increase_selected_quantity(self, row_data,container_id,product_data):
        global check_list

        for row in row_data:
            if self.in_list(row):
                temp = []
                for i in row:
                    temp.append(i)

                id_prod = self.get_prod_id(row[0],product_data)
                print(container_id,id_prod)
                controller.increase_product_quantity(container_id = container_id, product_id = id_prod)
                row[-1] += 1  # Increase the quantity by 1
                self.table_layout.update_row(self.table_layout.row_data[id_prod-1],row)


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
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(0.8, 0.8),
            use_pagination=True,
            rows_num=3,
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
        increase_button.bind(on_press=lambda instance: self.increase_selected_quantity(table_data,container_id,product_data))

        button_layout = GridLayout(cols=2, size_hint=(1, None), height=dp(48))
        button_layout.add_widget(close_button)
        button_layout.add_widget(increase_button)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.table_layout)
        layout.add_widget(button_layout)

        table_popup = Popup(title=f"Содержимое контейнера № {container_id}", content=layout, size_hint=(0.8, 0.8))
        table_popup.bind(on_press=self.close_popup)

        table_popup.open()


    def on_check_press(self, instance_table, current_row):
        global check_list
        '''Called when the check box in the table row is checked.'''
        for i in check_list:
            if i==current_row:
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

    def on_start(self):
        # заготовка для списка контейнеров на скрине Containers, функция open_search_window в текщуем виде будет ненужна
        for i in range(20):
            self.root.ids.container.add_widget(
                OneLineListItem(text=f"Single-line item {i}")
            )

    def on_spinner_select(self, instance, text):
        self.show_table_popup(text)



    def change_quantity(self, label, change):
        quantity = int(label.text)
        quantity += change
        label.text = str(quantity)

    def on_stop(self):
        self.capture.release()


if __name__ == '__main__':
    QRCodeScannerApp().run()
