from django.shortcuts import render
from django.apps import apps
from django.core.exceptions import FieldDoesNotExist, PermissionDenied
from django.http import Http404, JsonResponse
from django.views import View


class CheckExistObjJsonView(View):
    """Handle AutocompleteWidget's AJAX requests for data."""
    paginate_by = 20

    def get(self, request, *args, **kwargs):
        # response_text = request.GET.get("term")
        # print("CheckExistObjJsonView.get")
        # return JsonResponse({"response": response_text
        # })
        """
        Return a JsonResponse with search results as defined in
        serialize_result(), by default:
        {
            results: [{id: "123" text: "foo"}],
            pagination: {more: true}
        }
        """
        self.term, self.model, self.source_field = self.process_request(request)

        # if not self.has_perm(request):
            # raise PermissionDenied

        self.object_list = self.get_queryset()
        return JsonResponse({
            'results': [
                self.serialize_result(self.object_list)
            ],
        })

    def serialize_result(self, objs):
        """
        Convert the provided model object to a dictionary that is added to the
        results list.
        """
        if objs:
            return [{'id': str(x.pk), 'text': str(x)} for x in objs]
        else:
            {}

    def get_queryset(self):
        """Return queryset based on ModelAdmin.get_search_results()."""
        query_dict = {"%s__contains"%self.source_field.name: self.term}
        qs = self.model.objects.filter(**query_dict)
        return qs

    def process_request(self, request):
        """
        Validate request integrity, extract and return request parameters.

        Since the subsequent view permission check requires the target model
        admin, which is determined here, raise PermissionDenied if the
        requested app, model or field are malformed.

        Raise Http404 if the target model admin is not configured properly with
        search_fields.
        """
        term = request.GET.get('term', '')
        try:
            app_label = request.GET['app_label']
            model_name = request.GET['model_name']
            field_name = request.GET['field_name']
        except KeyError as e:
            raise PermissionDenied from e

        # Retrieve objects from parameters.
        try:
            source_model = apps.get_model(app_label, model_name)
        except LookupError as e:
            raise PermissionDenied from e
        try:
            source_field = source_model._meta.get_field(field_name)
        except FieldDoesNotExist as e:
            raise PermissionDenied from e
        
        return term, source_model, source_field
