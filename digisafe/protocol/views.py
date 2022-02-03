from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.autocomplete import AutocompleteJsonView
from django.contrib.admin.sites import AdminSite
from django.http import HttpResponse, Http404
from django.conf import settings
from django.utils.translation import gettext as _

import os

from users.models import User
from protocol.models import Protocol

class ProtocolAutocompleteJsonView(AutocompleteJsonView):
    def __init__(self, *args, **kwargs):
        self.admin_site = AdminSite()
        super(ProtocolAutocompleteJsonView, self).__init__(*args, **kwargs)
        
    # def get_queryset(self):
        # return super(ProtocolAutocompleteJsonView, self).get_queryset()
        
def protocol_download_file(request, path):
    file_root, file_ext = os.path.splitext(path)
    file_path = os.path.join(settings.BASE_DIR, "files", path)
    # print("views.download", file_path, file_root, file_ext)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/"+file_ext.replace(".",""))
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    # print("views.download Http404")
    raise Http404

def protocol_download_sign_file(request, path):
    file_root, file_ext = os.path.splitext(path)
    file_path = os.path.join(settings.BASE_DIR, "signs", path)
    # print("views.download", file_path, file_root, file_ext)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/"+file_ext.replace(".",""))
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    # print("views.download Http404")
    raise Http404


from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
import io
import math

class pagination:
    MAX_LEARNER_PER_PAGE = 35 #aumentare significa rivedere l'altezza in px delle singole righe
    TOT_PAGES = 0
    TOT_LEARNER_PAGES = 0
    learners = None
    sessions = None
    
    def __init__(self, protocol):
        self.protocol  = protocol
        self._learners  = protocol.learners_set.all().order_by("pk")
        self.TOT_PAGES = self.TOT_PAGES + 1 # la prima pagina 
        # devono essere chiamati in questo ordine
        self.learners  = self._get_learner_per_page()   #crea il dict dei learners
        # self._get_rest_blank()                          #aggiunge eventuali righe vuote
        self.sessions  = self._sessions_pages()         #crea la lista di sessioni
    
    def _get_rest_blank(self, learners):
        v = list(learners.values())[-1]
        # print("_get_rest_blank", len(v))
        last_k = list(learners.keys())[-1]
        rest_list = ["" for x in range(self.MAX_LEARNER_PER_PAGE-len(v))]
        # print("last_k", last_k)
        # print("rest_list", rest_list)
        
        learners[last_k] = learners[last_k]+rest_list
        # print("learners[last_k]", learners[last_k])
        return learners
        
    def _get_learner_per_page(self):
        # Suddivide gli utenti learners assegandone un numero massimo a pagina.
        # Numero massimo definito in MAX_LEARNER_PER_PAGE
        # Ritorna:
        # {1: [user, ...], 2: [user, ...], ...}
        learners = self._learners
        pages = int(math.ceil(len(learners)/self.MAX_LEARNER_PER_PAGE))
        # print("protocoltags.get_num_page_learner ",pages)
        learner_list = {}
        start = 0
        for i in range(pages): # i inizia con 0
            # print(i)
            stop = (i+1)*self.MAX_LEARNER_PER_PAGE
            # print("get_learner_per_page ",start, stop )
            learner_list[i+1+self.TOT_PAGES] = learners[start : stop]
            start = stop
        learner_list = self._get_rest_blank(learner_list) #aggiunge riche vuote
        self.TOT_LEARNER_PAGES = i +1
        self.TOT_PAGES = self.TOT_PAGES + i +1# pagine aggiunte al totale
        # print(self.TOT_PAGES, learner_list)
        return learner_list
        
    def _sessions_pages(self):
        # Ritorna:
        # [sessione, {1: [user, ...], 2: [user, ...], ...} ,
        #  sessione, {1: [user, ...], 2: [user, ...], ...}, ...]
        sessions = self.protocol.session_set.all()
        sessions_pages = len(sessions)
        # print("sessions_pages", sessions_pages)
        res = []
        for i in range(sessions_pages):
            res.append([sessions[i], self._get_learner_per_page()])
        return res
    
def registerView(request, pk):
    p = Protocol.objects.get(pk=pk)
    sessions = p.session_set.all()
    learners = p.learners_set.all().order_by("pk")
    pag = pagination(p)
    
    authorization = {}
    if p.course.need_institution:
        authorization["entity"] = p.institution
    else:
        authorization["entity"] = p.center
    # print("registerView authorization", authorization)
    return render(request, 'protocol/register_print.html', 
                  context={'protocol': p, 
                           'sessions': pag.sessions, 
                           'learners': pag.learners, 
                           'authorization': authorization, 
                           'tot_pages': pag.TOT_PAGES,
                           })
    
def registerPdf(request, pk):
    """Generate pdf."""
    # Model data
    p = Protocol.objects.get(pk=pk)
    sessions = p.session_set.all()
    learners = p.learners_set.all()
    # print("protocol.views.registerView sessions", sessions)
    # print("protocol.views.registerView learners",learners)

    # Rendered
    html_string = render_to_string('protocol/register_print.html', {'protocol': p, 'sessions': sessions, 'learners': learners, })
    html = HTML(string=html_string,base_url=request.build_absolute_uri())
    result = html.write_pdf()

    # Creating http response
    response = HttpResponse(content_type='application/pdf;')
    response['Content-Disposition'] = 'inline; filename={name}.pdf'.format(name=_("Prot_{0}_register".format(pk)))
    response['Content-Transfer-Encoding'] = 'binary'
    
    with io.BytesIO(result) as f:
        response.write(f.read())
    return response
    
def examView(request, pk):
    """Generate pdf."""
    p = Protocol.objects.get(pk=pk)
    sessions = p.session_set.all()
    learners = p.learners_set.all().order_by("pk")
    pag = pagination(p)
    
    authorization = {}
    if p.course.need_institution:
        authorization["entity"] = p.institution
    else:
        authorization["entity"] = p.center
    context = {
               'protocol': p, 
               'sessions': pag.sessions, 
               'learners': pag.learners, 
               'authorization': authorization, 
               'tot_pages': pag.TOT_PAGES,
               'tot_learners_pages': pag.TOT_LEARNER_PAGES,
              }
    return render(request, 'protocol/exam_print.html', context=context)
    
def protocol_user_check(request, protocol_pk, user_pk):
    try:
        p = Protocol.objects.get(pk=protocol_pk)
        u = User.objects.get(pk=user_pk)
        l = p.learners_set.filter(user=u)[0]
        context = {
            "protocol": p,
            "learner": l,
        }
        return render(request, 'protocol/certificate_user_check.html', context=context)
    # except Protocol.DoesNotExist:
    except:
        # errore sul .get del protocollo
        # errore sul ...[0] del filter
        return render(request,  "protocol/certificate_user_check_http404.html", context={})
    
from .models import Files
def sign_file(request, file_pk):
    f = Files.objects.get(pk=file_pk)
    p = f.protocol
    context = {
               'file': f, 
               'filename': f.get_doc_type_display,
               'protocol': p,
              }
    return render(request, 'protocol/sign_file.html', context=context)

from django.http import JsonResponse
import json
from .models import Signs
def save_signs(request):
    # print(request.POST.get("data"))
    data = request.POST.get("data")
    if data:
        data = json.loads(data)

        p = Protocol.objects.get(pk=data["protocol"])
        f = p.files_set.get(pk=data["file_id"])
        u = request.user
        for pages in data["signs"].values():
            # print(pages)
            for item in pages:
                # print(item)
                s = Signs()
                # print(item["pdfcoord"][0])
                s.pdf_x   = item["pdfcoord"][0]
                s.pdf_y   = item["pdfcoord"][1]
                s.html_x  = item["coord"][0]
                s.html_y  = item["coord"][1]
                s.page    = item["file_page"]
                s.user = u
                s.file = f
                s.save()
        f.signFile()
        # f.signFile(u, data)
        return JsonResponse({'save': True})
    return JsonResponse({'save': False})
    
def remove_signs(request):
    print("protocol.views.remove_signs")
    data = request.POST.get("data")
    if data:
        data = json.loads(data)
        p = Protocol.objects.get(pk=data["protocol"])
        f = p.files_set.get(pk=data["file_id"])
        print(f.signs_set.filter(user=request.user))
        [x.delete() for x in f.signs_set.filter(user=request.user)]
        f.signFile()
        return JsonResponse({'remove': True})
    return JsonResponse({'remove': False})    