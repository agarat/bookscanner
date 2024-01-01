import cv2
from pyzbar.pyzbar import decode

def scan_barcode():
    cap = cv2.VideoCapture(0)  # Acceder a la cámara (puede que necesites cambiar el número 0 por otro valor si tienes múltiples cámaras)

    while True:
        ret, frame = cap.read()  # Capturar un fotograma de la cámara
        cv2.imshow('Barcode Scanner', frame)  # Mostrar la imagen de la cámara en una ventana

        if cv2.waitKey(1) & 0xFF == ord('s'):  # Presiona 's' para tomar una captura
            cv2.imwrite('barcode.png', frame)  # Guardar la imagen
            break

    cap.release()  # Liberar la cámara
    cv2.destroyAllWindows()  # Cerrar todas las ventanas

    # Leer la imagen capturada y decodificar el código de barras
    barcode_img = cv2.imread('barcode.png', 0)  # Lee la imagen en escala de grises
    barcodes = decode(barcode_img)

    if barcodes:
        for barcode in barcodes:
            barcode_data = barcode.data.decode('utf-8')
            print(f'Código de barras detectado: {barcode_data}')
    else:
        print('No se detectó ningún código de barras.')

if __name__ == "__main__":
    scan_barcode()
