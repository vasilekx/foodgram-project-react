# api/process.py

from io import BytesIO
import os
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders

from django.conf import settings

# defining the function to convert an HTML file to a PDF file


def html_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(
        BytesIO(html.encode("UTF-8")),
        result,
        # encoding='utf-8'
    )
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def render_pdf_view():
    paragraphs = ['first paragraph', 'second paragraph', 'third paragraph']
    data = {'paragraphs': paragraphs}
    template_path = 'pdf_template.html'
    context = data
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


def fetch_pdf_resources(uri, rel):
    print(f'{uri.find(settings.STATIC_URL)=}')
    print(f'{uri.find(settings.MEDIA_URL)=}')

    if uri.find(settings.MEDIA_URL) != -1:
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))
        print(f'{path=}')
    elif uri.find(settings.STATIC_URL) != -1:
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ''))
        print(f'{path=}')
    else:
        path = None
        print(f'{path=}')
    return path


def fetch_resources(uri, rel):
    """
    Retrieves embeddable resource from given ``uri``.
    For now only local resources (images, fonts) are supported.
    :param str uri: path or url to image or font resource
    :returns: path to local resource file.
    :rtype: str
    :raises: :exc:`~easy_pdf.exceptions.UnsupportedMediaPathException`
    """

    if settings.STATIC_URL and uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    elif settings.MEDIA_URL and uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    else:
        path = os.path.join(settings.STATIC_ROOT, uri)
    p = path.replace("\\", "/")
    print(f'{p=}')
    return p


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
    else:
        sUrl = settings.STATIC_URL  # Typically /static/
        sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL  # Typically /media/
        mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    print(f'{path=}')
    path.replace("\\", "/")
    print(f'{path=}')
    return path


def html_to_pdf_2():
    from io import BytesIO
    from django.http import HttpResponse
    from django.template.loader import get_template
    from xhtml2pdf import pisa
    paragraphs = ['first paragraph', 'second paragraph', 'third paragraph']
    data = {'paragraphs': paragraphs}
    template_path = 'pdf_template.html'
    context = data
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    result = BytesIO()
    # pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")),
    #                         result,
    #                         encoding='UTF-8',
    #                         # link_callback=fetch_pdf_resources
    #                         # link_callback=fetch_resources
    #                         )
    pdf = pisa.CreatePDF(html,
                         result,
                         encoding='UTF-8',
                         # link_callback=fetch_pdf_resources
                         # link_callback=fetch_resources
                         link_callback=link_callback
                         )
    # pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

