from django import forms

class UploadCSVForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        file = self.cleaned_data.get('file')

        if file:
            if not file.name.endswith('.csv'):
                raise forms.ValidationError('This is not a csv file.')
                
            if file:
                try:
                    if file.content_type != 'text/csv':
                        raise forms.ValidationError('File is not CSV type.')
                except AttributeError:
                    pass

        return file