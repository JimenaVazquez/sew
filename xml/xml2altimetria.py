"""
SEW - Sesión XML 2 - Ejercicio 3
Generar archivos SVG desde archivos XML

Programa: xml2altimetria.py
Entrada: etapaEsquema.xml
Salida: altimetria.svg

@author: Jimena Vázquez Suárez - UO301668
"""

import xml.etree.ElementTree as ET

class Svg(object):
    """
    Genera archivos SVG con formas vectoriales
    """

    # crea el elemento raíz, el namespace del svg y la versión
    def __init__(self):
        self.raiz = ET.Element('svg', xmlns="http://www.w3.org/2000/svg", version="2.0")

    def addPolyline(self,points,style=""):
        # convertimos los puntos en coordenadas svg
        puntos = ""
        for p in points:
            puntos += (str(p[0]) + "," + str(p[1]) + " ")
        # añade una polilínea
        ET.SubElement(self.raiz,'polyline', points=puntos, style=style)

    def addText(self,texto,x,y,style):
        # añade una cadena de texto
            ET.SubElement(self.raiz,'text', x=x, y=y, style=style).text=texto
    
    def escribir(self, svg):
        # escribe el archivo svg
        arbol = ET.ElementTree(self.raiz)
        ET.indent(arbol)
        arbol.write(svg, encoding='utf-8', xml_declaration=True)


class FromXmlToSvg(object):
    """
    Lectura de un XML y genera el SVG 
    """

    def __init__(self, archivo):
        # trae el arbol DOM del xml
        self.raiz = ET.parse(archivo).getroot()
        self.ns = '{http://www.uniovi.es}'   # ns de los elementos del xml

    def altimetriaPunto(self, elemento):
        # se trae la altitud y la distancia de un punto -> son atributos
        # uso de xpath
        distancia = elemento.get('distancia')
        altitud = elemento.get('altitud')
        return distancia + ',' + altitud + ','

    def altimetriaHito(self, elemento):
            # se trae la altitud y la distancia de un hito -> son atributos
            # uso de xpath
            distancia = elemento.get('distancia')
            altitud = elemento.get('altitud')
            identificacion = elemento.find(self.ns + 'identificación').text
            return distancia + ',' + altitud + ',' + identificacion

    def altimetriaSalida(self, elemento):
        # se trae la altitud de la salida, su distancia = 0
        # uso de xpath
        altitud = elemento.get('altitud')
        return '0,' + altitud + ',Salida'

    def altimetriaMeta(self, etapa):
        # se trae la altitud de la meta
        # distancia = longitud de la etapa, por eso pasamos toda la etapa
        # uso de xpath
        distancia = etapa.get('longitud')
        meta = etapa.find(self.ns + 'meta')
        altitud = meta.get('altitud')
        return distancia + ',' + altitud + ',Meta'

    def generarPuntosAnonimos(self):
        # creación de una lista -> almacén de coordenadas de los puntos anónimos e hitos
        listaDePuntos = []

        # se añaden a la lista los puntos anónimos
        for punto in self.raiz.findall('.//' + self.ns + 'punto'):
            listaDePuntos.append(self.altimetriaPunto(punto))
 
        # se añaden a la lista los hitos (puertos y esprints)
        for hito in self.raiz.findall('.//' + self.ns + 'hito'):
            listaDePuntos.append(self.altimetriaHito(hito))

        return listaDePuntos

    def generarRutaCompleta(self, listaDePuntos):
        etapa = self.raiz.find('.//' + self.ns + 'etapa')
       # creación de la ruta para la polilinea (futuro plano de altimetría)
        ruta = []

        # creación del punto de salida -> añadimos salida a la ruta
        ruta.append(self.altimetriaSalida(etapa.find(self.ns + 'salida')))

         # ordenamos la lista de puntos, para que esté ordenada según su distancia a la salida
        listaDePuntos.sort(key=lambda elemento: float(elemento.split(',')[0]))
        for punto in listaDePuntos:
            ruta.append(punto) # añadimos los puntos a la ruta 1 a 1

        # creación del punto de meta -> añadimos meta a la ruta
        ruta.append(self.altimetriaMeta(etapa))

        return ruta

    def generarSvg(self, archivo):
        # creación de una lista -> almacén de coordenadas de los puntos anónimos e hitos
        listaDePuntos = self.generarPuntosAnonimos()

        # creación de la ruta para la polilinea (futuro plano de altimetría)
        ruta = self.generarRutaCompleta(listaDePuntos)

        # lista de tríos, "distancia,altitud,identificación"
        # la identificación es opcional
        altimetria = []
        for punto in ruta:
            splited = punto.split(',')
            altimetria.append((float(splited[0]), float(splited[1]), splited[2]))

        # generamos el svg dado el archivo
        svg = Svg()
        # atributos de la imagen
        margen_izq = 25
        margen_sup = 40
        nivMar = 550
        anchoAlt = 1150
        longitudEtapa = float(altimetria[-1][0])
        altoAlt = 475
        altitudMaxEtapa = max(alt[1] for alt in altimetria)

        # titulo de la imagen
        titulo = "Altimetría de la etapa nº" + self.raiz.find('.//' + self.ns + 'número').text + " - " + self.raiz.find('.//' + self.ns + 'nombre').text
        svg.addText(titulo, str(margen_izq), str(margen_sup), "font-weight:bold;font-size:40px;")

        # imagen altimetría -> de la que se basará la polilínea
        vertices = [(margen_izq, nivMar)] # punto inicial
        x=0
        for punto in altimetria:
            x = margen_izq + punto[0] * anchoAlt / longitudEtapa    # distancia del punto al inicio
            y = nivMar - punto[1] * altoAlt / altitudMaxEtapa       # altitud, sobre el nivel del mar
            vertices.append((x,y))
            if punto[2]!="":
                svg.addText(punto[2], str(x), str(nivMar), "font-size:20px;writing-mode:tb;glyph-orientation-vertical:0;")
        vertices.append((x, nivMar)) # punto previo final para polilinea
        vertices.append((margen_izq, nivMar)) # punto final = punto inicial

        # creación de la línea
        svg.addPolyline(vertices, "fill:white;stroke:red;stroke-width:4;")

        # guardamos el archivo
        svg.escribir(archivo)

def main():
    etapa = FromXmlToSvg('etapaEsquema.xml')
    etapa.generarSvg('altimetria.svg')

if __name__ == "__main__":
    main()
