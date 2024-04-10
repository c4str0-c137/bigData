import re
import json
import pymongo
import ssl
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


class datos:
    def __init__(self):
        self.driver = webdriver.Firefox()
        self.datos_anuncios = []

    def iniciar_ventana(self, url):
        self.driver.get(url)
    
    def get_url(self):
        return self.driver.current_url

    def get_datos(self):
        return self.datos_anuncios

    def inicio(self):
        self.iniciar_ventana("https://clasificados.lostiempos.com/inmuebles?sort_by=created&sort_order=DESC&page=0")

    def limiteUrl(self):
        anuncios = self.driver.find_elements(By.CSS_SELECTOR, '.view-content .views-row')
        ultimo_enlace = self.driver.find_element(By.CSS_SELECTOR,".pager-last > a:nth-child(1)")

        # Obtener la URL del último enlace
        url_ultimo_enlace = ultimo_enlace.get_attribute("href")
        num = re.split("=",url_ultimo_enlace)
        return num[-1]

    def agregar_elementos(self):
        # Encuentra todos los anuncios en la página
        anuncios = self.driver.find_elements(By.CSS_SELECTOR, '.view-content .views-row')
        # Itera sobre cada anuncio e imprime sus datos
        for anuncio in anuncios:
            try:
                titulo = anuncio.find_element(By.CSS_SELECTOR, '.title a').text
                fecha_publicacion = anuncio.find_element(By.CSS_SELECTOR, '.publish-date .field-content').text
                cuerpo = anuncio.find_element(By.CSS_SELECTOR, '.body .field-content').text
                precio = anuncio.find_element(By.CSS_SELECTOR, '.ads-price .field-content').text
                ubicacion = anuncio.find_element(By.CSS_SELECTOR, '.description .field-content:first-child').text
                tipo = anuncio.find_element(By.CSS_SELECTOR, '.description .field-content:nth-child(2)').text
                categoria = anuncio.find_element(By.CSS_SELECTOR, '.description .field-content:last-child').text
                # Guarda los datos del anuncio en un diccionario
                datos_anuncio = {
                    "Título": titulo,
                    "Fecha de publicación": fecha_publicacion,
                    "Cuerpo": cuerpo,
                    "Precio": precio,
                    "Ubicación": ubicacion,
                    "Tipo": tipo,
                    "Categoría": categoria
                }
                # Agrega el diccionario de datos del anuncio a la lista
                self.datos_anuncios.append(datos_anuncio)
            except NoSuchElementException as e:
                pass
        # Guarda los datos de los anuncios en un archivo JSON

    def agregar_mongodb(self):
        uri = "mongodb+srv://rodricastro223:NBU83a3KlUmDsTQM@cluster0.brihnwx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

        cliente = pymongo.MongoClient(uri)
        base_de_datos = cliente["anuncios_db"]
        coleccion = base_de_datos["anuncios"]

        # Leer el JSON y cargar los datos
        with open("datos_anuncios.json", encoding='utf-8', errors='ignore') as f:
            datos = json.load(f)

        # Actualizar cada anuncio en la colección
        for anuncio in datos:
            filtro = {"Cuerpo": anuncio["Cuerpo"]}
            nuevo_valor = {"$set": anuncio}
            try:
                resultado = coleccion.update_one(filtro, nuevo_valor, upsert=True)
                if resultado.modified_count:
                    print("Documento modificado:", resultado.modified_count)
                else:
                    print("Nuevo documento creado")
            except Exception as e:
                print("Error durante la actualización:", e)
        

if __name__ == "__main__":
    dato_anuncios = datos()
    dato_anuncios.inicio()
    dato_anuncios.agregar_elementos()
    limit = dato_anuncios.limiteUrl()
    for i in range(int(limit)):
        dato_anuncios.iniciar_ventana("https://clasificados.lostiempos.com/inmuebles?sort_by=created&sort_order=DESC&page="+str(i+1))
        dato_anuncios.agregar_elementos()
    with open('datos_anuncios.json', 'w', encoding='utf-8') as f:
        json.dump(dato_anuncios.get_datos(), f, ensure_ascii=False, indent=4)
    
    dato_anuncios.agregar_mongodb()
