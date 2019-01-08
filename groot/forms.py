import datetime

from django import forms
from django.forms import SelectDateWidget
 
from .models import *

class EnrollmentForm(forms.ModelForm):

    sort_idx = forms.ModelChoiceField(queryset = SortMst.objects.all())

    class Meta:
        model = Enrollment
        fields = ['sort_idx', 'title', 'term']



    def save(self, commit=True):
         enrollment = Enrollment(**self.cleaned_data)
         if commit:
             enrollment.save()
         return enrollment
