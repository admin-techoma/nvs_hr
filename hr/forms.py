from bootstrap_datepicker_plus.widgets import DateTimePickerInput
from django import forms
from django.utils import timezone
from employee.models import Employee
from .models import Interview, Onboarding,candidateResume

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = candidateResume
        fields = ['candidate_id','name', 'phone_number', 'email','resume', 'remarks']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'phone_number': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-sm'}),
            'resume': forms.FileInput(attrs={'class': 'form-control form-control-sm'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
        }
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if len(str(phone_number)) > 10:
            raise forms.ValidationError("Phone number cannot exceed 10 digits.")
        return phone_number

class resumeEditForm(forms.ModelForm):
    class Meta:
        model = candidateResume
        fields = ['candidate_id','name', 'phone_number', 'resume','email','status', 'remarks']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'phone_number': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-sm'}),
            'status': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
        }
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if len(str(phone_number)) > 10:
            raise forms.ValidationError("Phone number cannot exceed 10 digits.")
        return phone_number
    
class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ('candidate_id', 'interviewMode', 'interviewRound' , 'interviewDate', 'interviewTime')
    
    def clean_interviewDate(self):
        interview_date = self.cleaned_data['interviewDate']

        if interview_date < timezone.now().date():
            raise forms.ValidationError('Interview date cannot be in the past')

        return interview_date

class InterviewFormFields(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ('interviewer', 'interviewMode', 'interviewRound' , 'interviewDate', 'interviewTime')
        widgets = {
            'interviewer': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'interviewMode': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'interviewRound': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'interviewDate': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'}),
            'interviewTime': forms.TimeInput(attrs={'type': 'time', 'format':'%H:%M',  'class': 'form-control form-control-sm'}),
        }
        labels = {
            'interviewMode': 'Interview Mode',
            'interviewRound': 'Interview Round',
            'interviewDate': 'Interview Date',
            'interviewTime': 'Interview Time',
        }

class NewResumeUploadForm(forms.ModelForm):
    class Meta:
        model = candidateResume
        fields = ['candidate_id','resume']




class professionalDetailsForm(forms.ModelForm):
    class Meta:
        model = candidateResume
        fields = ['Exp']
        widgets = { 'Exp': forms.NumberInput(attrs={'class': 'form-control'}),}     

class InterviewSelectionFeedback(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default value for interviewFeedback_date
        self.fields['interviewFeedback_date'] = forms.DateField(initial=timezone.now().date(), widget=forms.DateInput(attrs={'class': 'form-control form-control-sm ', 'type': 'date'}))

        # Filter out the 'IsEmployeeNow' choice from the interviewFeedback field
        feedback_choices = [
            ('Pending', 'Pending'),
            ('Selected', 'Selected'),
            ('Rejected', 'Rejected'),
        ]
        self.fields['interviewFeedback'].choices = feedback_choices

    class Meta:
        model = candidateResume
        fields = ['remarks', 'interviewFeedback']
        widgets = {
            'remarks': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'interviewFeedback': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        }

    
class OnboardingKYCForm(forms.ModelForm):
    class Meta:
        model = Onboarding
        fields = ['c_psimg', 'c_adhar', 'c_pan', 'c_bankDetails']
        widgets = { 'c_psimg': forms.FileInput(attrs={'class': 'form-control form-control-sm', 'required': True}),
                    'c_adhar': forms.FileInput(attrs={'class': 'form-control form-control-sm', 'required': True}),
                    'c_pan': forms.FileInput(attrs={'class': 'form-control form-control-sm', 'required': True}),
                    'c_bankDetails': forms.FileInput(attrs={'class': 'form-control form-control-sm', 'required': True}),
                    }
        labels = {
            'interviewMode': 'Interview Mode',
            'c_psimg': 'Passport Size c_psimg',
            'c_adhar': 'Adharcard',
            'c_pan': 'Pancard',
            'c_bankDetails': 'Cancel Cheque/Bank-Pass Book First Page',
        }

        def __init__(self, *args, **kwargs):
            super(OnboardingForm, self).__init__(*args, **kwargs)
            allowed_extensions = ['.png', '.jpg', '.jpeg', '.pdf', '.docx', '.doc']
            validators = [FileExtensionValidator(allowed_extensions=allowed_extensions)]

            for field_name in self.fields:
                if field_name in ['c_psimg', 'c_adhar', 'c_pan', 'c_bankDetails']:
                    self.fields[field_name].validators.extend(validators)

class onboardingAccountDetilsForm(forms.ModelForm):
    class Meta:
        model = Onboarding
        fields = ['c_bankStatement', 'c_salarySlips']
        widgets = { 
                    'c_bankStatement': forms.FileInput(attrs={'class': 'form-control form-control-sm', 'required': True}),
                    'c_salarySlips': forms.FileInput(attrs={'class': 'form-control form-control-sm'}),
        }
        labels = {
            'c_bankStatement': 'Last 3 Months Bank Statement',
            'c_salarySlips': 'Last 3 Months Salary Slips',}
        
        def __init__(self, *args, **kwargs):
            super(OnboardingForm, self).__init__(*args, **kwargs)
            allowed_extensions = ['.pdf']
            validators = [FileExtensionValidator(allowed_extensions=allowed_extensions)]

            for field_name in self.fields:
                if field_name in ['c_bankStatement', 'c_salarySlips']:
                    self.fields[field_name].validators.extend(validators)

class onboardingEducationDetilsForm(forms.ModelForm):
    class Meta:
        model = Onboarding
        fields = ['c_expLetter', 'c_previousJoiningLetter','c_degree', 'c_masters', 'c_HSC', 'c_SSC', 'c_otherCertificate']
        widgets = { 
                    'c_expLetter': forms.FileInput(attrs={'class': 'form-control form-control-sm'}),
                    'c_previousJoiningLetter': forms.FileInput(attrs={'class': 'form-control form-control-sm'}),
                    'c_degree': forms.FileInput(attrs={'class': 'form-control form-control-sm', 'required': True}),
                    'c_masters': forms.FileInput(attrs={'class': 'form-control form-control-sm'}),
                    'c_HSC': forms.FileInput(attrs={'class': 'form-control form-control-sm'}),
                    'c_SSC': forms.FileInput(attrs={'class': 'form-control form-control-sm', 'required': True}),
                    'c_otherCertificate': forms.FileInput(attrs={'class': 'form-control form-control-sm'})}
        labels = {
                    'c_expLetter': 'Experience Letters',
                    'c_previousJoiningLetter': 'Previous company Joining/Offer latter',
                    'c_degree': 'c_degree Certificates',
                    'c_masters': "Master's c_degree",
                    'c_HSC': 'HSC Certificates',
                    'c_SSC': 'SSC Certificates',
                    'c_otherCertificate': 'Other Certificates' }
        
        def __init__(self, *args, **kwargs):
            super(OnboardingForm, self).__init__(*args, **kwargs)
            allowed_extensions = ['.pdf']
            validators = [FileExtensionValidator(allowed_extensions=allowed_extensions)]

            for field_name in self.fields:
                if field_name in ['c_bankStatement', 'c_salarySlips']:
                    self.fields[field_name].validators.extend(validators)

