# core/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Case, PastIllness
# import re # Not currently used, can be removed if not needed elsewhere

# UPDATED Widgets with the new CSS class 'form-input'
textarea_widget = forms.Textarea(attrs={'rows': 3, 'class': 'form-input'})
input_widget = forms.TextInput(attrs={'class': 'form-input'})
number_widget = forms.NumberInput(attrs={'class': 'form-input'}) # Assuming age is number, but your model seems to use CharField for age
date_widget = forms.DateInput(attrs={'class': 'form-input', 'type': 'date'})
select_widget = forms.Select(attrs={'class': 'form-input'})
# For ChoiceFields that should be rendered as radio buttons or custom selects:
# radio_select_widget = forms.RadioSelect(attrs={'class': 'form-check-input'}) # Example


class CaseForm(forms.ModelForm):
    # --- Fields corresponding to structured JSON data in the model ---
    # Ensure all these use the updated widgets or have 'form-input' in their attrs
    personal_thermal_state = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Thermal State")
    personal_perspiration = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Perspiration")
    personal_appetite = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Appetite")
    personal_diet = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Diet")
    personal_desire = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Desire")
    personal_aversion = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Aversion")
    personal_thirst = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Thirst")
    personal_urine = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Urine")
    personal_bowels = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Bowels")
    personal_habits_addiction = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Habits/Addiction")
    personal_sleep = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Sleep")
    personal_dreams = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}), label="Dreams")
    personal_other = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}), label="Other Personal History Notes")

    menstrual_age_of_puberty = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Age of Puberty")
    menstrual_menses = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Menses (Cycle/Duration/Flow)")
    menstrual_menses_complaints = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}), label="Complaints During Menses")
    menstrual_age_at_marriage = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Age at Marriage")
    menstrual_lmp = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="LMP (Last Menstrual Period)")
    menstrual_menses_triggers = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Menses Triggers")
    menstrual_leucorrhea = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Leucorrhea Details")
    menstrual_pregnancy = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}), label="Pregnancy History (G/P/L/A)")
    menstrual_menopause_age = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Menopause Age")
    menstrual_menopause_complaints = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}), label="Menopause Complaints")

    physical_built = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Built")
    physical_head = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Head")
    physical_throat = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Throat")
    physical_hair = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Hair")
    physical_mouth = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Mouth")
    physical_ear = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Ear")
    physical_nails = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Nails")
    physical_tongue = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Tongue")
    physical_eyes = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Eyes")
    physical_extremities = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Extremities")
    physical_teeth = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Teeth")
    physical_skin = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Skin")
    physical_lymph_glands = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Lymph Glands")
    physical_gums = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Gums")
    physical_nose = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Nose")
    physical_bp = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="BP")
    physical_temperature = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Temperature")
    physical_pulse = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="Pulse")
    physical_rr = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="RR (Respiratory Rate)")
    physical_spo2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}), label="SpO2")
    physical_other = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}), label="Other Physical Examination Notes")

    class Meta:
        model = Case
        fields = [
            'date', 'opd_no', 'patient_name', 'patient_age', 'patient_sex',
            'patient_occupation', 'patient_address', 'patient_phone',
            'presenting_complaints', 'history_of_present_illness',
            'past_history_vaccination', 'family_history',
            'patient_as_person', 'systemic_examination',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'opd_no': forms.TextInput(attrs={'class': 'form-input'}),
            'patient_name': forms.TextInput(attrs={'class': 'form-input'}),
            'patient_age': forms.TextInput(attrs={'class': 'form-input'}), # If age can be "30 years" or "6 months", TextInput is fine. If purely numeric, NumberInput.
            'patient_sex': forms.Select(attrs={'class': 'form-input'}),
            'patient_occupation': forms.TextInput(attrs={'class': 'form-input'}),
            'patient_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}),
            'patient_phone': forms.TextInput(attrs={'class': 'form-input'}),
            'presenting_complaints': forms.Textarea(attrs={'rows': 4, 'class': 'form-input'}),
            'history_of_present_illness': forms.Textarea(attrs={'rows': 4, 'class': 'form-input'}),
            'past_history_vaccination': forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}),
            'family_history': forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}),
            'patient_as_person': forms.Textarea(attrs={'rows': 4, 'class': 'form-input'}),
            'systemic_examination': forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}),
        }
        labels = {
            'patient_name': 'Patient Name *',
            'presenting_complaints': 'Presenting Complaints *',
            # Add other custom labels if needed
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['patient_name'].required = True
        self.fields['presenting_complaints'].required = True
        for field_name, field in self.fields.items():
            if field_name not in ['patient_name', 'presenting_complaints']:
                field.required = False

    def clean_opd_no(self): # This method is fine
        opd_no = self.cleaned_data.get('opd_no')
        return opd_no


class PastIllnessForm(forms.ModelForm):
    class Meta:
        model = PastIllness
        fields = ['disease', 'approximate_age', 'duration', 'treatment', 'completely_recovered']
        widgets = {
             'disease': forms.TextInput(attrs={'class': 'form-input'}),
             'approximate_age': forms.TextInput(attrs={'class': 'form-input'}),
             'duration': forms.TextInput(attrs={'class': 'form-input'}),
             'treatment': forms.Textarea(attrs={'rows': 2, 'class': 'form-input'}),
             'completely_recovered': forms.Select(choices=((True, 'Yes'), (False, 'No'), (None, 'N/A')), attrs={'class': 'form-input'}), # Assuming boolean or null here
        }
        # You might want to ensure 'completely_recovered' is a BooleanField in your model for this widget to make most sense
        # Or if it's a CharField, use TextInput or a Select with appropriate string choices.
        # I've changed to Select with Yes/No/N/A as an example. Adjust as per your model.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False


PastIllnessFormSet = inlineformset_factory(
    Case,
    PastIllness,
    form=PastIllnessForm,
    extra=1,
    can_delete=True
)