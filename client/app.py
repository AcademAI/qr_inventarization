import cv2
from kivy.app import App
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

class QRCodeScannerApp(App):
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
        # Возможно стоит изменить например на 1/60... Нужно настраивать под конкретный телефон.
        Clock.schedule_interval(self.schedule_next_frame, 1.0 / 30)

        search_button = Button(text='Search', size_hint=(None, None), size=(100, 50))
        search_button.bind(on_press=self.open_search_window)
        layout.add_widget(search_button)

        return layout

    def schedule_next_frame(self, dt):
        if not self.is_processing_frame:
            Clock.schedule_once(self.process_frame)

    def process_frame(self, dt):
        self.is_processing_frame = True
        ret, frame = self.capture.read()
        if ret:
            # Преобразование кадра в оттенки серого
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Распознавание QR-кодов
            decoded_objects = pyzbar.decode(gray)
            for obj in decoded_objects:
                text = obj.data.decode('utf-8')
                self.show_popup(text)
            buf = cv2.flip(frame, 0).tostring()
            self.texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            self.texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.image.texture = self.texture
        self.is_processing_frame = False

    def show_popup(self, text):
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=text))
        close_button = Button(text='Close', size_hint=(1, 0.2))
        close_button.bind(on_press=self.close_popup)
        content.add_widget(close_button)
        popup = Popup(title='QR Code', content=content, size_hint=(0.8, 0.8))
        popup.bind(on_dismiss=self.on_popup_dismiss)
        popup.open()

    def close_popup(self, instance):
        instance.parent.parent.parent.parent.dismiss()

    def on_popup_dismiss(self, instance):
        Clock.schedule_once(self.schedule_next_frame, 0)

    def open_search_window(self, instance):
        search_layout = BoxLayout(orientation='vertical')
        spinner = Spinner(
            text='Select an item',
            values=('конденсатор', 'транзистор', 'диод'),
            size_hint=(None, None),
            size=(200, 50)
        )
        spinner.bind(text=self.on_spinner_select)
        search_layout.add_widget(spinner)

        search_popup = Popup(title='Search', content=search_layout, size_hint=(0.6, 0.4))
        search_popup.open()

    def on_spinner_select(self, instance, text):
        if text == 'диод':
            self.display_table()

    def display_table(self):

        table_layout = GridLayout(cols=5, size_hint=(None, None), size=(600, 400), spacing=5, padding=5)
        table_layout.bind(minimum_width=table_layout.setter('width'))
        #table_layout = GridLayout(cols=5, size_hint=(None, None), size=(600, 400), spacing=5, padding=5)

        table_layout.add_widget(Label(text='Название', bold=True, size_hint_x=None, width=100))
        table_layout.add_widget(Label(text='Характеристика', bold=True, size_hint_x=None, width=150))
        table_layout.add_widget(Label(text='Сопротивление', bold=True, size_hint_x=None, width=100))
        table_layout.add_widget(Label(text='Количество', bold=True, size_hint_x=None, width=100))
        table_layout.add_widget(Label(text=' ', size_hint_x=None, width=50))  # Пустой столбец для кнопок

        table_layout.add_widget(Label(text='Диод 1'))
        table_layout.add_widget(Label(text='Характеристика 1'))
        table_layout.add_widget(Label(text='100 Ом'))
        quantity_label = Label(text='0')
        increase_button = Button(text='+', size_hint=(None, None), size=(50, 30))
        increase_button.bind(on_press=lambda instance: self.change_quantity(quantity_label, 1))
        decrease_button = Button(text='-', size_hint=(None, None), size=(50, 30))
        decrease_button.bind(on_press=lambda instance: self.change_quantity(quantity_label, -1))
        table_layout.add_widget(quantity_label)
        table_layout.add_widget(increase_button)
        table_layout.add_widget(decrease_button)
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
