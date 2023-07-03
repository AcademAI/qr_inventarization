"""import cv2
import os
os.environ['KIVY_GL_BACKEND'] = 'sdl2'
from pyzbar.pyzbar import decode
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.label import Label
from kivy.clock import Clock

class QRCodeScanner(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = Camera(resolution=(640, 480), play=True)
        self.add_widget(self.camera)
        self.label = Label(text="QR-код не найден")
        self.add_widget(self.label)
        Clock.schedule_interval(self.update, 1/30)

    def update(self, dt):
        frame = self.camera.texture
        if frame is not None:
            frame = cv2.cvtColor(frame.pixels, cv2.COLOR_RGBA2BGR)
            decoded_objects = decode(frame)
            if decoded_objects:
                for obj in decoded_objects:
                    self.label.text = f"QR-код: {obj.data.decode('utf-8')}"
            else:
                self.label.text = "QR-код не найден"

class QRCodeScannerApp(App):
    def build(self):
        return QRCodeScanner()

if __name__ == '__main__':
    QRCodeScannerApp().run()"""
import cv2
from pyzbar.pyzbar import decode

# создаем объект cap для захвата видео с камеры
cap = cv2.VideoCapture(0)

while True:
    # считываем кадр из видеопотока
    _, frame = cap.read()

    # декодируем QR-коды на кадре
    decoded_objects = decode(frame)

    # проходимся по каждому распознанному QR-коду и выводим его данные на экран
    for obj in decoded_objects:
        print("QR Code detected: ", obj.data.decode('utf-8'))

    # отображаем текущий кадр
    cv2.imshow("QR Code Scanner", frame)

    # ждем нажатия клавиши "q" для выхода из цикла
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# освобождаем ресурсы
cap.release()
cv2.destroyAllWindows()