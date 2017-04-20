from django.shortcuts import render
from django.http import HttpResponse
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
import sys
import urllib.request
from barrapunto.models import Pages
from django.views.decorators.csrf import csrf_exempt

# Variable global
content_rss = ""

class myContentHandler(ContentHandler):
    def __init__ (self):
        self.inItem = False
        self.inContent = False
        self.theContent = ""

    def startElement (self, name, attrs):
        if name == 'item':
            self.inItem = True
        elif self.inItem:
            if name == 'title':
                self.inContent = True
            elif name == 'link':
                self.inContent = True

    def endElement (self, name):

        if name == 'item':
            self.inItem = False
        elif self.inItem:
            if name == 'title':
                line = "Title: " + self.theContent + "."
                # To avoid Unicode trouble
                self.htmlFile.write(line.encode('utf-8'))
                self.inContent = False
                self.theContent = ""
            elif name == 'link':
                self.htmlFile.write("<a href =" + self.theContent + ">Link</a> <br/>")
                self.inContent = False
                self.theContent = ""

    def characters (self, chars):
        if self.inContent:
            self.theContent = self.theContent + chars

    ## Main program ##

def barra(request):
    resp = "Las direcciones disponibles son: "
    lista_pages = Pages.objects.all()
    for page in lista_pages:
        resp += "<br>-/" + page.name + " --> " + page.page

@csrf_exempt
def process(request, req):
    if request.method == "GET":
        try:
            page = Pages.objects.get(name=req)
            resp = "<html><body><div>La página solicitada es /" + page.name + " -> " + page.page + "</div><div>""<br>Titulares de barrapunto.com:<br>" + content_rss + "</div></body></html>"
        except Pages.DoesNotExist:
            resp = "La página introducida no está en la base de datos. Créala:"
            resp += "<form action='/" + req + "' method='POST'>"
            resp += "Nombre: <input type='text' name='nombre'>"
            resp += "<br>Página: <input type='text' name='page'>"
            resp += "<input type='submit' value='Enviar'></form>"
    elif request.method == "POST":
        if request.user.is_authenticated():
            nombre = request.POST['nombre']
            page = request.POST['page']
            pagina = Pages(name=nombre, page=page)
            pagina.save()
            resp = "Has creado la página " + nombre + " con id " + str(pagina.id)
    elif request.method == "PUT":
        try:
            page = Pages.objects.get(name=req)
            resp = "Ya existe una página con ese nombre"
        except Pages.DoesNotExist:
            page = request.body
            pagina = Pages(name=req, page=page)
            pagina.save()
            resp = "Has creado la página " + req
    else:
        resp = "Error. Method not supported."

    resp += "<br/><br/>Eres " + request.user.username + ' <a href="/logout">haz logout</a>.'
    return HttpResponse(resp)

def update(request):
    theParser = make_parser()
    theHandler = myContentHandler()
    theParser.setContentHandler(theHandler)
    xmlFile = urllib.request.urlopen("http://barrapunto.com/index.rss")
    theParser.parse(xmlFile)
    resp = ("<html><body><div>Contenido de barrapunto: " + content_rss + "</div></body></html>")
    return HttpResponse(resp)
