"""
SEW - Sesión XML 2 - Ejercicio 2
Generar archivos KML desde archivos XML

Programa: xml2kml.py
Entrada: etapaEsquema.xml
Salida: etapa.kml

@author: Jimena Vázquez Suárez - UO301668
"""

import xml.etree.ElementTree as ET

class Kml(object):
    """
    Genera archivos KML con puntos y líneas
    """

    # crea el elemento raíz y el namespace del kml
    def __init__(self):
        self.raiz = ET.Element('kml', xmlns="http://www.opengis.net/kml/2.2")
        self.doc = ET.SubElement(self.raiz, 'Document')

    def addPlacemark(self, nombre, coordenadas, color):
        # crea un elemento <Placemark> con puntos <Punto>
        pm = ET.SubElement(self.doc, 'Placemark')
        ET.SubElement(pm, 'name').text = nombre
        estilo = ET.SubElement(pm, 'Style')
        icono = ET.SubElement(estilo, 'IconStyle')
        ET.SubElement(icono, 'color').text = color
        etiqueta = ET.SubElement(estilo, 'LabelStyle')
        ET.SubElement(etiqueta, 'color').text = color
        punto = ET.SubElement(pm, 'Point')
        # añade el punto al documento
        ET.SubElement(punto, 'coordinates').text = coordenadas

    def addLine(self, listaCoordenadas):
        # crea un elemento <Placemark> con líneas <LineString>
        # une los puntos para crear una línea
        pm = ET.SubElement(self.doc, 'Placemark')
        ls = ET.SubElement(pm, 'LineString')
        ET.SubElement(ls, 'tessellate').text = '1' # adaptamos la línea al terreno

        # se leen las coordenadas
        ET.SubElement(ls, 'coordinates').text = listaCoordenadas

        # cambiamos el estilo de la línea
        estilo = ET.SubElement(pm, 'Style')
        linea = ET.SubElement(estilo, 'LineStyle')
        ET.SubElement(linea, 'color').text = '#ff0000ff'
        ET.SubElement(linea, 'width').text = '5'

    def escribir(self, kml):
        # escribe el archivo kml
        arbol = ET.ElementTree(self.raiz)
        ET.indent(arbol)
        arbol.write(kml, encoding='utf-8', xml_declaration=True)


class FromXmlToKml(object):
    """
    Lectura de un XML y genera el KML 
    """

    def __init__(self, archivo):
        # trae el arbol DOM del xml
        self.raiz = ET.parse(archivo).getroot()
        self.ns = '{http://www.uniovi.es}'   # ns de los elementos del xml

    def coordenadas(self, elemento):
        # se trae la longitud, latitud y altitud de un elemento -> son atributos
        # uso de xpath
        longitud = elemento.get('longitud')
        latitud = elemento.get('latitud')
        altitud = elemento.get('altitud')
        return longitud + ',' + latitud + ',' + altitud

    def generarKml(self, archivo):
        # generamos el kml dado el archivo
        ns = self.ns
        kml = Kml()

        # creación de los puntos de salida y meta
        salida = self.coordenadas(self.raiz.find('.//' + ns + 'salida'))
        kml.addPlacemark('Salida', salida, "#ff0000ff") # En rojo
        meta = self.coordenadas(self.raiz.find('.//' + ns + 'meta'))
        kml.addPlacemark('Meta', meta, '#ff0000ff') # En rojo

        # creación de una lista -> almacén de coordenadas de los puntos anónimos e hitos
        listaDePuntos = []
        
        # se añaden a la lista los puntos anónimos
        for punto in self.raiz.findall('.//' + ns + 'punto'):
            listaDePuntos.append(punto)
            kml.addPlacemark('', self.coordenadas(punto), "#ff00ffff") # En amarillo

        # se añaden a la lista los hitos (puertos y esprints)
        for hito in self.raiz.findall('.//' + ns + 'hito'):
            listaDePuntos.append(hito)
            if hito.find(ns + 'tipoHito').text.startswith("Esprint "):
                # si el hito es un sprint
                kml.addPlacemark(hito.find(ns + 'identificación').text, self.coordenadas(hito), "#ffff0000") # En azul 
            else:
                # si el hito es un puerto
                kml.addPlacemark(hito.find(ns + 'identificación').text, self.coordenadas(hito), "#ff00ff00") # En verde

        # creación de la ruta
        ruta = salida + '\n' # añadimos la salida
        
        # ordenamos la lista de puntos, para que esté ordenada según su distancia a la salida
        listaDePuntos.sort(key=lambda elemento: float(elemento.get('distancia')))
        for punto in listaDePuntos:
            ruta += self.coordenadas(punto) + '\n' # añadimos los puntos a la ruta 1 a 1

        # terminamos la ruta
        ruta += meta # añadimos la meta
        
        # creación de la línea
        kml.addLine(ruta)

        # guardamos el archivo
        kml.escribir(archivo)

def main():
    
    etapa = FromXmlToKml('etapaEsquema.xml')
    etapa.generarKml('etapa.kml')

if __name__ == "__main__":
    main()
