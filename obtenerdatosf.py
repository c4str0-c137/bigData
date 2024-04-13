import json
import pymongo
#import ssl
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import tkinter as tk
from tkinter import messagebox

class DatosExtractor:
    def __init__(self):
        self.driver = webdriver.Firefox()
        self.datos_anuncios = []

    def iniciar_ventana(self, url):
        self.driver.get(url)

    def obtener_datos(self):
        self.iniciar_ventana("https://clasificados.lostiempos.com/inmuebles?sort_by=created&sort_order=DESC&page=0")
        limit = self.limite_url()
        for i in range(int(limit)):
            self.iniciar_ventana("https://clasificados.lostiempos.com/inmuebles?sort_by=created&sort_order=DESC&page="+str(i+1))
            self.agregar_elementos()

    def agregar_elementos(self):
        anuncios = self.driver.find_elements(By.CSS_SELECTOR, '.view-content .views-row')
        for anuncio in anuncios:
            try:
                titulo = anuncio.find_element(By.CSS_SELECTOR, '.title a').text
                fecha_publicacion = anuncio.find_element(By.CSS_SELECTOR, '.publish-date .field-content').text
                cuerpo = anuncio.find_element(By.CSS_SELECTOR, '.body .field-content').text
                precio = anuncio.find_element(By.CSS_SELECTOR, '.ads-price .field-content').text
                ubicacion = anuncio.find_element(By.CSS_SELECTOR, '.description .field-content:first-child').text
                tipo = anuncio.find_element(By.CSS_SELECTOR, '.description .field-content:nth-child(2)').text
                categoria = anuncio.find_element(By.CSS_SELECTOR, '.description .field-content:last-child').text
                datos_anuncio = {
                    "Título": titulo,
                    "Fecha de publicación": fecha_publicacion,
                    "Cuerpo": cuerpo,
                    "Precio": precio,
                    "Ubicación": ubicacion,
                    "Tipo": tipo,
                    "Categoría": categoria
                }
                self.datos_anuncios.append(datos_anuncio)
            except NoSuchElementException as e:
                pass

    def limite_url(self):
        ultimo_enlace = self.driver.find_element(By.CSS_SELECTOR, ".pager-last > a:nth-child(1)")
        url_ultimo_enlace = ultimo_enlace.get_attribute("href")
        num = re.split("=", url_ultimo_enlace)
        return num[-1]

    def guardar_json(self, nombre_archivo):
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            json.dump(self.datos_anuncios, f, ensure_ascii=False, indent=4)

    def guardar_mongodb(self, uri):
        cliente = pymongo.MongoClient(uri)
        base_de_datos = cliente["anuncios_db"]
        coleccion = base_de_datos["anuncios"]
        for anuncio in self.datos_anuncios:
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

class InterfazAnuncios:
    def __init__(self, root):
        self.root = root
        self.root.title("Extracción de Datos de Inmuebles")

        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=90, pady=90)

        self.btn_extraer = tk.Button(self.frame, text="Extraer Datos", command=self.extraer_datos, bg="CadetBlue", fg="black", font=("Arial", 14, "bold"))
        self.btn_extraer.pack()

    def extraer_datos(self):
        extractor = DatosExtractor()
        try:
            extractor.obtener_datos()
            extractor.guardar_json('datos_anuncios.json')
            extractor.guardar_mongodb('mongodb+srv://rodricastro223:NBU83a3KlUmDsTQM@cluster0.brihnwx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
            messagebox.showinfo("Extracción Completada", "Se han obtenido los datos de todos los anuncios.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error durante la extracción de datos:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazAnuncios(root)
    root.mainloop()
