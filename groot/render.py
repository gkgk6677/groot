from io import BytesIO
from io import StringIO
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa
from cgi import escape

class Render:
    @staticmethod
    def render(template_src, parmas:dict):
        template = get_template(template_src)
        html = template.render(parmas)
        # result = StringIO()
        # pdf = pisa.pisaDocument(BytesIO(StringIO(html.encode("UTF-8"))), result)
        # pdf = pisa.pisaDocument(StringIO(html.encode("ISO-8859-1")), result)
        # pdf = pisa.pisaDocument(StringIO(html.encode("iso-2022-kr")), result)
        response = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), response)
        if not pdf.err:
            return HttpResponse(response.getvalue(), content_type='application/pdf')
        else:
            return HttpResponse("Error Rendering PDF", status=400)
        # return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))
