from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import logging
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Configuración del logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración del navegador
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# Listas para almacenar los resultados
urls = []
ratings = []
comments_list = []

def obtener_datos(url, rating_selector, comments_selector):
    driver = None  # Inicializar driver fuera del bloque try
    rating = "N/A"  # Inicializar rating con un valor predeterminado
    comments = "N/A"  # Inicializar comments con un valor predeterminado

    try:
        # Inicializar el navegador
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        driver.get(url)

        try:
            # Esperar a que el elemento de la calificación esté presente
            rating_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, rating_selector))
            )
            rating = rating_element.text.strip()
            logger.info(f"Texto completo de la calificación: {rating}")
        except Exception as e:
            logger.error(f"Error al obtener la nota media: {e}")

        try:
            # Esperar a que el elemento de los comentarios esté presente
            comments_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, comments_selector))
            )
            comments_text = comments_element.text.strip()
            logger.info(f"Texto completo de los comentarios: {comments_text}")

            # Extraer el número de comentarios usando una expresión regular
            comments_match = re.search(r"(\d+)\s*(comentarios|reviews|ratings)", comments_text, re.IGNORECASE)
            if comments_match:
                comments = comments_match.group(1)
            else:
                logger.error(f"No se pudo extraer el número de comentarios del texto: {comments_text}")
        except Exception as e:
            logger.error(f"Error al obtener el número de comentarios: {e}")

        # Almacenar los resultados
        urls.append(url)
        ratings.append(rating)
        comments_list.append(comments)

        logger.info(f"Nota media: {rating}")
        logger.info(f"Número de comentarios: {comments}")

    except Exception as e:
        logger.error(f"Error al procesar la URL {url}: {e}")

    finally:
        # Cerrar el navegador si está inicializado
        if driver is not None:
            driver.quit()

# URLs y selectores
url_1 = "https://www.anwbcamping.nl/campings/camping-playa-brava"
rating_selector_1 = "span.css-1qthp5w"
comments_selector_1 = "div#campsite-reviews h4"

url_2 = "https://www.zoover.nl/spanje/costa-brava/platja-de-pals-playa-de-pals/camping-bungalows-platja-brava/camping"
rating_selector_2 = 'span[class="tss-54qlaj-rating-box-ratingValue"]'
comments_selector_2 = 'a.tss-1dystbt-LinkComponent-defaultLink-reviewCount'

url_3 = "https://www.camping.info/en/campsite/camping-playa-brava"
rating_selector_3 = "span.circular-text"
comments_selector_3 = "div.text-small-book.text-primary"

url_4 = "https://www.booking.com/hotel/es/camping-playa-brava-mobile-home-2.ca.html?"
rating_selector_4 = "div.a3b8729ab1.d86cee9b25"  # Selector de calificación en Booking.com
comments_selector_4 = "div.abf093bdfe.f45d8e4c32.d935416c47" # Selector de comentarios en Booking.com

# Llamar a la función para cada URL
obtener_datos(url_1, rating_selector_1, comments_selector_1)
obtener_datos(url_2, rating_selector_2, comments_selector_2)
obtener_datos(url_3, rating_selector_3, comments_selector_3)
obtener_datos(url_4, rating_selector_4, comments_selector_4)

# Crear un DataFrame con los resultados
data = {
    'URL': urls,
    'Calificación promedio': ratings,
    'Número de comentarios': comments_list
}

df = pd.DataFrame(data)

# Función para extraer la primera palabra después de "www."
def extraer_etiqueta(url):
    match = re.search(r"www\.([a-zA-Z]+)", url)
    if match:
        return match.group(1).capitalize()  # Devuelve la primera palabra en mayúscula
    return url  # Si no se encuentra, devuelve la URL completa

# Crear una lista de etiquetas simplificadas
etiquetas = [extraer_etiqueta(url) for url in urls]

# Convertir las calificaciones y comentarios a números
calificaciones = pd.to_numeric(df['Calificación promedio'], errors='coerce')
comentarios = pd.to_numeric(df['Número de comentarios'], errors='coerce')

# Crear la gráfica
fig, ax1 = plt.subplots(figsize=(12, 6))

# Posiciones de las barras
x = np.arange(len(etiquetas))  # Posiciones en el eje X
ancho = 0.35  # Ancho de las barras

# Barras para el número de comentarios (eje Y izquierdo)
barras_comentarios = ax1.bar(x - ancho/2, comentarios, ancho, label='Comentarios', color='skyblue')

# Configurar el eje Y izquierdo
ax1.set_xlabel('Camping')
ax1.set_ylabel('Número de Comentarios', color='skyblue')
ax1.tick_params(axis='y', labelcolor='skyblue')

# Crear un segundo eje Y para las calificaciones (eje Y derecho)
ax2 = ax1.twinx()
barras_calificaciones = ax2.bar(x + ancho/2, calificaciones, ancho, label='Calificación Media', color='orange')

# Configurar el eje Y derecho
ax2.set_ylabel('Calificación Media', color='orange')
ax2.tick_params(axis='y', labelcolor='orange')

# Añadir etiquetas de datos sobre las barras
def añadir_etiquetas(barras, eje_y, desplazamiento_y=0, formato="{:.1f}"):
    for barra in barras:
        altura = barra.get_height()
        eje_y.annotate(formato.format(altura),
                    xy=(barra.get_x() + barra.get_width() / 2, altura),
                    xytext=(0, desplazamiento_y),  # Desplazamiento vertical
                    textcoords="offset points",
                    ha='center', va='bottom')

# Añadir etiquetas a las barras de comentarios y calificaciones
añadir_etiquetas(barras_comentarios, ax1, 5, formato="{:.0f}")  # Sin decimales para comentarios
añadir_etiquetas(barras_calificaciones, ax2, 5, formato="{:.1f}")  # Un decimal para calificaciones

# Añadir título y ajustar el layout
plt.title('Comparación de Comentarios y Calificaciones por Camping')
plt.xticks(x, etiquetas, rotation=15, ha='right')
fig.tight_layout()

# Mostrar la gráfica
plt.show()

# Guardar el DataFrame en un archivo CSV
df.to_csv('resultados_camping.csv', index=False)

# Confirmación
logger.info("Los resultados se han guardado correctamente en 'resultados_camping.csv'.")