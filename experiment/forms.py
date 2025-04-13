from django import forms

class TeamForm(forms.Form):
    name = forms.CharField(
        max_length=100, 
        label='Название команды',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название команды'})
    )

class ExperimentForm(forms.Form):
    title = forms.CharField(
        max_length=200, 
        label='Название эксперимента',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название эксперимента'})
    )
