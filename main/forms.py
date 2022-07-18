from django import forms

class AddFilialForm(forms.Form):
    filial = forms.CharField(label='Qwertyu', max_length=100)
    address = forms.CharField(max_length=100, required=False)
    excel_file = forms.FileField()
