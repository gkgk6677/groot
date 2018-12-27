from django import forms
from django.forms import SelectDateWidget

# from .models import Contract

# class ContractForm(forms.ModelForm):
#     e_date = forms.DateField(widget=SelectDateWidget())
#     class Meta:
#         model = Contract
#         fields = ['title', 'sort', 'e_date']


#     def save(self, commit=True):
#         contract = Contract(**self.cleaned_data)
#         if commit:
#             contract.save()
#         return contract
