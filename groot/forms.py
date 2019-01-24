from django import forms
from .models import *

class EnrollmentForm(forms.ModelForm):

    sort_idx = forms.ModelChoiceField(queryset = SortMst.objects.all(), empty_label="산업분류", required=True, widget=forms.Select(attrs={'class':'dropdown1'}) )
    title= forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '100자 이내로 입력해주세요.', 'onkeyup':"chkword(this, 100)"}))
    summary = forms.CharField(widget=forms.Textarea(attrs={'class ': 'form-control', 'placeholder': '300자 이내로 입력해주세요.', 'onkeyup':"chkword(this, 300)"}))
    #
    class Meta:
        model = Enrollment
        fields = ['sort_idx', 'title', 'term','summary']
        labels = {
            'title': 'title_label',
            'sort_idx': 'sort_idx_label',
            'summary_label': 'summary_label'
        }


    def save(self, commit=True):
         enrollment = Enrollment(**self.cleaned_data)
         if commit:
             enrollment.save()
         return enrollment



class SearchForm(forms.ModelForm):
    word = forms.CharField(label="검색")

    class Meta:
        model = User
        fields = ['user_id']


class ExtendForm(forms.ModelForm):

    reason = forms.CharField(widget=forms.Textarea(attrs={'class ': 'form-control', 'placeholder': '300자 이내로 입력해주세요.', 'onkeyup':"chkword(this, 300)"}))
    #
    class Meta:
        model = Extend
        fields = ['term','reason']
        labels = {
            'reason_label': 'reason_label'
        }


    def save(self, commit=True):
         extend = Extend(**self.cleaned_data)
         if commit:
             extend.save()
         return extend

class ExpireForm(forms.ModelForm):

    reason = forms.CharField(widget=forms.Textarea(attrs={'class ': 'form-control', 'placeholder': '300자 이내로 입력해주세요.', 'onkeyup':"chkword(this, 300)"}))
    #
    class Meta:
        model = Expire
        fields = ['reason']
        labels = {
            'reason_label': 'reason_label'
        }


    def save(self, commit=True):
         expire = Expire(**self.cleaned_data)
         if commit:
             expire.save()
         return expire



class ContractForm(forms.ModelForm):

    reason = forms.CharField(widget=forms.Textarea(attrs={'class ': 'form-control', 'placeholder': '300자 이내로 입력해주세요.', 'onkeyup':"chkword(this, 300)"}))
    #
    class Meta:
        model = Extend
        fields = ['term','reason']
        labels = {
            'reason_label': 'reason_label'
        }


    def save(self, commit=True):
         contract = Contract(**self.cleaned_data)
         if commit:
             contract.save()
         return contract