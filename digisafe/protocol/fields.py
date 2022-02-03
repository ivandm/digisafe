from django.db import models


class myFileField(models.FileField):
    pass
    
    def __str__(self):
        return "__str__"
        
    def test(self):
        return "test"