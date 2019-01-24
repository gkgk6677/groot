# from io import BytesIO
from io import StringIO
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa
from cgi import escape

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = StringIO()
    # pdf = pisa.pisaDocument(BytesIO(StringIO(html.encode("UTF-8"))), result)
    # pdf = pisa.pisaDocument(StringIO(html.encode("ISO-8859-1")), result)
    pdf = pisa.pisaDocument(StringIO(html.encode("iso-2022-kr")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))