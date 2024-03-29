import cv2
from pyzbar.pyzbar import decode
import isbnlib
import requests
import csv

def is_valid_isbn(code):
    return isbnlib.is_isbn10(code) or isbnlib.is_isbn13(code)

def get_author_name(author_key):
    url = f'https://openlibrary.org{author_key}.json'

    response = requests.get(url)
    if response.status_code == 200:
        author_info = response.json()
        author_name = author_info.get('name', 'Nombre del autor no encontrado')
        return author_name
    else:
        return 'Error al obtener el nombre del autor'

def save_to_csv(data):
    with open('books_info.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(data)

def get_book_info(isbn):
    url = f'https://openlibrary.org/isbn/{isbn}.json'

    response = requests.get(url)
    if response.status_code == 200:
        book_info = response.json()
        if 'title' in book_info:
            title = book_info['title']
            authors_list = book_info.get('authors', [])
            if authors_list:
                authors = [get_author_name(author.get('key')) for author in authors_list]
                authors_str = ', '.join(authors)
                publisher = book_info.get('publishers', ['No disponible'])[0]
                publish_date = book_info.get('publish_date', 'No disponible')
                key_link = f'https://openlibrary.org{book_info.get("key")}'

                data = [isbn, title, authors_str, publisher, publish_date, key_link]
                save_to_csv(data)
                print('Información guardada en el archivo CSV.')
            else:
                print('Información de autor no encontrada.')
        else:
            print('No se encontró información para el ISBN proporcionado.')
    else:
        print('Error al obtener la información del libro.')

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
    # Verificar si el archivo CSV existe y, de no ser así, crearlo con un encabezado
    try:
        with open('books_info.csv', mode='r', encoding='utf-8') as file:
            pass  # El archivo existe, no es necesario hacer nada
    except FileNotFoundError:
        with open('books_info.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['ISBN', 'Título', 'Autor', 'Editor', 'Año de Publicación', 'Link a Key'])

    while True:
        isbn = scan_barcode()
        if isbn:
            with open('books_info.csv', mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                existing_isbns = {row[0] for row in reader}

            if isbn not in existing_isbns:
                get_book_info(isbn)
