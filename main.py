import cv2
from pyzbar.pyzbar import decode
import isbnlib

def is_valid_isbn(code):
    return isbnlib.is_isbn10(code) or isbnlib.is_isbn13(code)

def scan_barcode():
    cap = cv2.VideoCapture(0)  # Acceder a la cámara

    # Verificar si la cámara se abrió correctamente
    if not cap.isOpened():
        print("No se pudo abrir la cámara. Asegúrate de tener los permisos adecuados.")
        return

    # Obtener dimensiones de la cámara
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Calcular posición y tamaño del rectángulo centrado
    rect_w, rect_h = int(width * 0.6), int(height * 0.8)
    rect_x, rect_y = int((width - rect_w) / 2), int((height - rect_h) / 2)

    rect_color = (255, 0, 0)  # Color del rectángulo (en formato BGR)
    rect_thickness = 2

    while True:
        ret, frame = cap.read()  # Capturar un fotograma de la cámara

        if not ret:
            print("No se pudo capturar el fotograma.")
            break

        # Dibujar el rectángulo overlay en el centro de la imagen de la cámara
        cv2.rectangle(frame, (rect_x, rect_y), (rect_x + rect_w, rect_y + rect_h), rect_color, rect_thickness)

        cv2.imshow('Barcode Scanner', frame)  # Mostrar la imagen de la cámara en una ventana

        # Capturar automáticamente el código de barras dentro del rectángulo overlay
        barcode_frame = frame[rect_y:rect_y+rect_h, rect_x:rect_x+rect_w]
        barcodes = decode(barcode_frame)

        if barcodes:
            for barcode in barcodes:
                barcode_data = barcode.data.decode('utf-8')
                print(f'Código de barras detectado: {barcode_data}')

                if is_valid_isbn(barcode_data):
                    print(f'ISBN válido detectado: {barcode_data}')
                    return barcode_data  # Salir del bucle y devolver el ISBN válido

        # Esperar a que se presione la tecla 'q' para salir
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()  # Liberar la cámara
    cv2.destroyAllWindows()  # Cerrar todas las ventanas

if __name__ == "__main__":
    scanned_isbn = None
    while not scanned_isbn or not is_valid_isbn(scanned_isbn):
        scanned_isbn = scan_barcode()
