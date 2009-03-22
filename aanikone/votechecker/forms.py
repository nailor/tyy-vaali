from django import forms
from django.utils.translation import ugettext as _

from aanikone.votechecker.models import Person

class CheckForm(forms.Form):
    organization = forms.CharField(required=True)
    number = forms.CharField(required=True)

    def clean(self):
        number = self.cleaned_data.get('number')
        organization = self.cleaned_data.get('organization')
        if number and organization:
            try:
                self.person = Person.objects.get(
                    personnumber=number,
                    organization=organization,
                    )
            except Person.DoesNotExist:
                raise forms.ValidationError(_('Invalid student number'))
        super(CheckForm, self).clean()
