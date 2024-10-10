from django import forms

SLOTS_CHOICES = [
    ('monday_morning', 'Lundi Matin'),
    ('monday_afternoon', 'Lundi Après-midi'),
    ('monday_evening', 'Lundi Soir'),
    ('tuesday_morning', 'Mardi Matin'),
    ('tuesday_afternoon', 'Mardi Après-midi'),
    ('tuesday_evening', 'Mardi Soir'),
    ('wednesday_morning', 'Mercredi Matin'),
    ('wednesday_afternoon', 'Mercredi Après-midi'),
    ('wednesday_evening', 'Mercredi Soir'),
    ('thursday_morning', 'Jeudi Matin'),
    ('thursday_afternoon', 'Jeudi Après-midi'),
    ('thursday_evening', 'Jeudi Soir'),
    ('friday_morning', 'Vendredi Matin'),
    ('friday_afternoon', 'Vendredi Après-midi'),
    ('friday_evening', 'Vendredi Soir'),
    ('saturday_morning', 'Samedi Matin'),
    ('saturday_afternoon', 'Samedi Après-midi'),
    ('saturday_evening', 'Samedi Soir'),
    ('sunday_morning', 'Dimanche Matin'),
    ('sunday_afternoon', 'Dimanche Après-midi'),
    ('sunday_evening', 'Dimanche Soir'),
]

class AvailabilityForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Date de début"
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Date de fin"
    )
    availability_slots = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=SLOTS_CHOICES,
        label="Disponibilités"
    )