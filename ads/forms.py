from django import forms  
from .models import Ad, MainCategory, SubCategory  

class AdForm(forms.ModelForm):  
    main_category = forms.ModelChoiceField(  
        queryset=MainCategory.objects.all(),  
        empty_label="Select main category",  
        widget=forms.Select(attrs={'class': 'form-select'})  
    )  
    sub_category = forms.ModelChoiceField(  
        queryset=SubCategory.objects.none(),  
        empty_label="Select subcategory",  
        widget=forms.Select(attrs={'class': 'form-select'})  
    )  

    class Meta:  
        model = Ad  
        fields = ['title', 'description', 'price', 'main_category', 'sub_category']  
        widgets = {  
            'title': forms.TextInput(attrs={'class': 'form-control'}),  
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),  
            'price': forms.NumberInput(attrs={'class': 'form-control'}),  
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'main_category' in self.data:
            try:
                main_category_id = int(self.data.get('main_category'))
                self.fields['sub_category'].queryset = SubCategory.objects.filter(
                    main_category_id=main_category_id
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.main_category:
            self.fields['sub_category'].queryset = self.instance.main_category.subcategories.all()