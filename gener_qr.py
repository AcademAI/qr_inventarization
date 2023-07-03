import qrcode
# пример данных
data = "C/Users/3"
# имя выходного файла
filename = "prov.png"
# генерировать qr-код
img = qrcode.make(data)
# сохранить img в файл
img.save(filename)