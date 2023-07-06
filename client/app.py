import cv2
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from pyzbar import pyzbar
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp

import controller

class QRCodeScannerApp(MDApp):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        self.image = Image()
        layout.add_widget(self.image)
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.texture = None
        self.is_processing_frame = False
        
        search_button = Button(text='Поиск', size_hint=(None, None), size=(100, 50))
        search_button.bind(on_press=self.open_search_window)
        scan_button = Button(text='Сканировать QR', size_hint=(None, None), size=(100, 50))
        scan_button.bind(on_press=self.process_frame)
        layout.add_widget(search_button)
        layout.add_widget(scan_button)

        return layout

    def process_frame(self, dt):
        # Возможно стоит изменить например на 1/60... Нужно настраивать под конкретный телефон.

        if not self.is_processing_frame:
            Clock.schedule_once(self.process_frame)

        self.is_processing_frame = True
        ret, frame = self.capture.read()
    
        if ret:
            # Преобразование кадра в оттенки серого
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Распознавание QR-кодов
            decoded_objects = pyzbar.decode(gray)
            print(decoded_objects)
            
            
            if len(decoded_objects) == 0:  # Если массивы пустые то выполняет отрисовку кадров
                buf = cv2.flip(frame, 0).tostring()
                self.texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                self.texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.image.texture = self.texture
            else:
                last_decoded_object = decoded_objects[0]
                #иначе не пустой пойманный массив декодирует 
                text = last_decoded_object.data.decode('utf-8')
                
                container_id = text[-1]
                self.show_table_popup(container_id)
                return

        self.is_processing_frame = False

    def show_table_popup(self, text):

        container_id = text
        product_data = controller.get_container(container_id)

        values = []

        for product in product_data:
            values.append([product['name'], product['type'], product['quantity']])

        table_data = values
        
        table_layout = MDDataTable(
            pos_hint = {'center_x': 0.5, 'center_y': 0.5},
            size_hint=(0.8, 0.8),
            use_pagination=True,
            rows_num = 3,
            column_data=[
                #("Номер", dp(30)),
                ("Название", dp(30)),
                ("Тип", dp(30)),
                #("Емкость", dp(30)),
                #("Напряжение", dp(30)),
                #("Сопротивление", dp(30)),
                ("Количество", dp(30)),
            ],
            row_data=table_data,
        )
        close_button = Button(text='Закрыть', size_hint=(1, 0.2))
        close_button.bind(on_press=self.close_popup)

        table_layout.add_widget(close_button)

        table_popup = Popup(title=f"Содержимое контейнера № {container_id}", content=table_layout, size_hint=(0.8, 0.8))
        table_popup.bind(on_press=self.close_popup)

        table_popup.open()


    def close_popup(self, instance):
        instance.parent.parent.parent.parent.dismiss()

    '''
    def on_popup_dismiss(self, instance):
        Clock.schedule_once(self.schedule_next_frame, 0)

    '''
    def open_search_window(self, instance):
        search_layout = BoxLayout(orientation='vertical')
        containers_tuple = controller.get_all_containers()

        # Извлечение значений id из containers_tuple
        ids = [item[0] for item in containers_tuple]

        spinner = Spinner(
            text='Select an item',
            values=ids,
            size_hint=(None, None),
            size=(200, 50)
        )
        spinner.bind(text=self.on_spinner_select)
        search_layout.add_widget(spinner)

        search_popup = Popup(title='Search', content=search_layout, size_hint=(0.6, 0.4))
        search_popup.open()
        

    def on_spinner_select(self, instance, text):
        self.display_table(text)

    def display_table(self, text):
        container_id = text
        product_data = controller.get_container(container_id)

        values = []

        for product in product_data:
            values.append([product['name'], product['type'], product['quantity']])

        table_data = values
        
        table_layout = MDDataTable(
            pos_hint = {'center_x': 0.5, 'center_y': 0.5},
            size_hint=(0.8, 0.8),
            use_pagination=True,
            rows_num = 3,
            column_data=[
                #("Номер", dp(30)),
                ("Название", dp(30)),
                ("Тип", dp(30)),
                #("Емкость", dp(30)),
                #("Напряжение", dp(30)),
                #("Сопротивление", dp(30)),
                ("Количество", dp(30)),
            ],
            row_data=table_data,
        )

        table_popup = Popup(title='Table', content=table_layout, size_hint=(0.8, 0.8))
        table_popup.open()
        

    def change_quantity(self, label, change):
        quantity = int(label.text)
        quantity += change
        label.text = str(quantity)

    def on_stop(self):
        self.capture.release()


if __name__ == '__main__':
    QRCodeScannerApp().run()
