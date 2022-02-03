from django.contrib.admin.widgets import AdminFileWidget

class AdminFileSignWidget(AdminFileWidget):
    # template_name = 'admin/widgets/clearable_file_input.html'
    
    def test(self):
        return "test"