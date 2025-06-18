from FDCSM import models
from django import forms
from import_export import fields, resources

class AdminModelForm(forms.ModelForm):
    class Meta: #FDC_ADM_INFO
        model = models.FDC_ADM_INFO
        fields = ['ADM_NBR', 'ADM_NAM', 'ADM_PWD']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs = {'class': 'form-control input-data', 'placeholder': field.label}


class ProfessorModelForm(forms.ModelForm):
    class Meta: #FDC_PFS_INFO
        model = models.FDC_PFS_INFO
        fields = ['PFS_NAM', 'PFS_NBR', 'PFS_PWD', 'PFS_TEL_NBR', 'PFS_INTRO', 'PFS_NUM_MATH', 'PFS_NUM_PSC', 'PFS_NUM_SCI']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs = {'class': 'form-control input-data', 'placeholder': field.label}

class StudentModelForm(forms.ModelForm):
    class Meta: #FDC_STU_INFO
        model = models.FDC_STU_INFO
        fields = ['STU_NBR', 'STU_NAM', 'STU_PWD', 'STU_TEL_NBR', 'STU_PRO']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs = {'class': 'form-control input-data', 'placeholder': field.label}


class UploadModelForm(forms.ModelForm):
    class Meta:

        model = models.FDC_STU_INTRO
        fields = ['STU_GRADE', 'STU_VIT']
        # exclude = ['STU_NBR', 'CAT_TIM', ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs = {'class': 'form-control-file', 'placeholder': field.label}

    def save(self, commit=True):
        instance = super().save(commit=False)
        # 更新指定字段
        instance.STU_GRADE = self.cleaned_data['STU_GRADE']
        # 如果需要更新多个字段，继续更新...
        instance.STU_VIT = self.cleaned_data['STU_VIT']
        # 如果需要，可以添加额外的逻辑
        # ...
        if commit:
            instance.save()
        return instance

class ProfessorSelectModelForm(forms.ModelForm):
    class Meta:
        model = models.FDC_PFS_SEL
        fields = '__all__'

class OutExcel(resources.ModelResource):
    STU_PRO_display = fields.Field(
        attribute='get_STU_PRO_display'
    )
    class Meta:
        model = models.FDC_PFS_SEL
        fields = ['PFS_NBR__PFS_NAM', 'PFS_STU_NBR__STU_NAM', 'STU_PRO_display']