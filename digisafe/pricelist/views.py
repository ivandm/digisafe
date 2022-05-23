from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse
from django.core import serializers
from django.template.loader import render_to_string
from bootstrap_modal_forms.generic import BSModalCreateView

from companies.models import SessionBook
from .models import PriceList, SessionPrice
from .forms import PriceListForm, ExtraPriceListSet


@login_required(login_url="/account/login/")
def index(request):
    return render(request, "pricelist/index.html", context={})


class PriceListView(ListView):
    model = PriceList

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        return qs.filter(user=self.request.user)


class PriceCreateView(CreateView):
    model = PriceList
    form_class = PriceListForm
    success_url = reverse_lazy('pricelist:list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()

        if self.request.POST.get("_continue"):
            HttpResponseRedirect(reverse_lazy("pricelist:update", args=(self.object.id,)))
        return HttpResponseRedirect(self.get_success_url())


# todo: se PriceList.id usato per una worksession, allora blocca la modifica. Fatto nel model.
class PriceUpdateView(UpdateView):
    model = PriceList
    form_class = PriceListForm
    success_url = reverse_lazy('pricelist:list')

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        return qs.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        data = super(PriceUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['form'] = PriceListForm(self.request.POST, instance=self.object)
            data['extraset'] = ExtraPriceListSet(
                self.request.POST, instance=self.object,
                # queryset=self.object.extrapricelist_set.order_by("id"),
            )
        else:
            data['form'] = PriceListForm(instance=self.object)
            data['extraset'] = ExtraPriceListSet(
                instance=self.object,
                # queryset=self.object.extrapricelist_set.order_by("id"),
            )
        return data

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """
        # print("companies.PriceUpdateView.post")
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        extraset = ExtraPriceListSet(self.request.POST, instance=self.object,
                                     queryset=self.object.extrapricelist_set.order_by("id"),
                                     )

        # print(form.is_valid() )
        # print(extraset.is_valid() )
        if form.is_valid() and extraset.is_valid():
            return self.form_valid(form, extraset)
        else:
            return self.form_invalid(form, extraset)

    def form_valid(self, form, extraset):
        # print("companies.PriceUpdateView.form_valid")
        self.object = form.save()
        extraset.instance = self.object
        extraset.save()

        if self.request.POST.get("save_close"):
            return HttpResponseRedirect(self.get_success_url())
        elif self.request.POST.get("_continue"):
            return HttpResponseRedirect(reverse_lazy("pricelist:update", kwargs={'pk': self.object.id}))
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, extraset):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        # print("companies.PriceUpdateView.form_invalid")
        return self.render_to_response(
            self.get_context_data(form=form,
                                  extraset=extraset,
                                  ))


# todo: se PriceList.id usato per una worksession, allora blocca la cancellazione. Fatto nel model.
class PriceDeleteView(DeleteView):
    model = PriceList
    success_url = reverse_lazy('pricelist:list')

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        return qs.filter(user=self.request.user)


class PriceModalListView(ListView):
    model = PriceList
    template_name = 'pricelist/pricelistmodal_list.html'

    session_id = None

    def get_context_data(self, **kwargs):
        # print("pricelist.views.PriceModalListView.get_context_data")
        context = super(PriceModalListView, self).get_context_data(**kwargs)
        # context['session'] = SessionBook.objects.get(pk= self.session_id)
        context['session_id'] = self.session_id
        return context

    def get_queryset(self, *args, **kwargs):
        # print("pricelist.views.PriceModalListView.get_queryset")
        qs = super().get_queryset(*args, **kwargs)
        return qs.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        # print("pricelist.views.PriceModalListView.get")
        self.session_id = request.GET.get("session_id")
        return super(PriceModalListView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # print("pricelist.views.PriceModalListView.post")
        session_id = request.POST.get('session_id')
        price_id = request.POST.get('price_id')
        session = SessionBook.objects.get(pk=session_id)
        price = PriceList.objects.filter(user__id=request.user.id, pk=price_id)
        if price:
            session_price = SessionPrice.objects.get_or_create(session=session, user=request.user)[0]
            session_price.price = price[0]
            session_price.save()
            return JsonResponse({"success": "Success"})
        return JsonResponse({})


def getprice(request):
    # print("pricelist.views.getprice")
    res = dict()
    if request.method == 'GET':
        session_id = request.GET.get("session_id")
        data = SessionPrice.objects.get(session__id=session_id, user__id=request.user.id)

        res['table'] = render_to_string(
            'pricelist/get_price.html',
            {'price': data.price},
            request=request
        )
        # return render(request, "pricelist/get_price.html", context={'price': data.price})
        return JsonResponse(res)
