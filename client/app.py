import cv2
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from pyzbar import pyzbar
from functools import partial
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button


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
        Clock.schedule_interval(self.schedule_next_frame, 1.0/30)

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
        close_button = Button(text='Закрыть', size_hint=(1, 0.2))
        close_button.bind(on_press=self.close_popup)
        content.add_widget(close_button)

        popup = Popup(title='QR Code', content=content, size_hint=(0.8, 0.8))
        popup.bind(on_dismiss=self.on_popup_dismiss)
        popup.open()

    def close_popup(self, instance):
        instance.parent.parent.parent.parent.dismiss()

    def on_popup_dismiss(self, instance):
        Clock.schedule_once(self.schedule_next_frame, 0)

    def on_stop(self):
        self.capture.release()


if __name__ == '__main__':
    QRCodeScannerApp().run()
