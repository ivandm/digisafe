from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect


from .models import PriceList
from .forms import PriceForm

@login_required(login_url="/account/login/")
def index(request):
    return render(request, "pricelist/index.html", context={})


class PriceListView(ListView):
    model = PriceList


class PriceCreateView(CreateView):
    model = PriceList
    form_class = PriceForm
    success_url = reverse_lazy('pricelist:list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class PriceUpdateView(UpdateView):
    model = PriceList
    form_class = PriceForm
    success_url = reverse_lazy('pricelist:list')


class PriceDeleteView(DeleteView):
    model = PriceList
    success_url = reverse_lazy('pricelist:list')
