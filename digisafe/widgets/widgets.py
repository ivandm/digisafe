from django import forms

class AutocompleteSelect(forms.widgets.Select):
    class Media:
        # css = {'all': (
            # "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css", )}
        js = (
                "https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js",
                "https://code.jquery.com/ui/1.13.0/jquery-ui.js",
                "/static/js/autocompleteselect.js",
            )
        pass
        
    def __init__(self, attrs=None, *args, **kwargs):
        attrs = attrs or {}

        attrs.update({
                        "class":"autocompleteselect",
                        "autocomplete":"on",
                        # "onChange": "getOption(this)",
                    })
        
        super().__init__(attrs, *args, **kwargs)