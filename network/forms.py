from django import forms
from django.db.models import Q
from selectable.forms import AutoCompleteWidget

from . import lookups
# from selectable import forms as selectable

from . import models
# from django.forms.models import inlineformset_factory
# from analysis import metaplot


class ExperimentFilterForm(forms.Form):

    search = forms.CharField(
        label='Search',
        required=False)

    name = forms.CharField(
        label='Name',
        required=False)

    description = forms.CharField(
        label='Description',
        required=False)

    data_type = forms.CharField(
        label='Data type',
        help_text="ex: ChIP-seq",
        required=False)

    cell_type = forms.CharField(
        label='Cell type',
        help_text='ex: K562',
        required=False)

    assembly = forms.CharField(
        label='Assembly',
        help_text='ex: hg19',
        required=False)

    target = forms.CharField(
        label='Target',
        help_text='Target antibody',
        required=False)

    paginate_by = forms.IntegerField(
        label='Items per page',
        min_value=1,
        initial=10,
        max_value=10000,
        required=False)

    def get_query(self):

        search = self.cleaned_data.get('search')

        search_query = Q()
        if search:
            search_query |= Q(name__icontains=search)
            search_query |= Q(description__icontains=search)
            search_query |= Q(experiment_type__name__icontains=search)
            search_query |= Q(cell_type__icontains=search)
            search_query |= Q(dataset__assembly__name__icontains=search)
            search_query |= Q(target__icontains=search)

        name = self.cleaned_data.get('name')
        description = self.cleaned_data.get('description')
        data_type = self.cleaned_data.get('data_type')
        cell_type = self.cleaned_data.get('cell_type')
        assembly = self.cleaned_data.get('assembly')
        target = self.cleaned_data.get('target')

        filter_query = Q()
        if name:
            filter_query &= Q(name__icontains=name)
        if description:
            filter_query &= Q(description__icontains=description)
        if data_type:
            filter_query &= Q(experiment_type__name__icontains=data_type)
        if cell_type:
            filter_query &= Q(cell_type__icontains=cell_type)
        if assembly:
            filter_query &= Q(dataset__assembly__name__icontains=assembly)
        if target:
            filter_query &= Q(target__icontains=target)

        return Q(search_query & filter_query)


class AllExperimentFilterForm(ExperimentFilterForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['search'].widget = \
            AutoCompleteWidget(lookups.AllExpSearchLookup)
        self.fields['name'].widget = \
            AutoCompleteWidget(lookups.AllExpNameLookup)
        self.fields['description'].widget = \
            AutoCompleteWidget(lookups.AllExpDescriptionLookup)
        self.fields['data_type'].widget = \
            AutoCompleteWidget(lookups.AllExpTypeLookup)
        self.fields['cell_type'].widget = \
            AutoCompleteWidget(lookups.AllExpCellTypeLookup)
        self.fields['assembly'].widget = \
            AutoCompleteWidget(lookups.AllExpAssemblyLookup)
        self.fields['target'].widget = \
            AutoCompleteWidget(lookups.AllExpTargetLookup)


class RecommendedExperimentFilterForm(ExperimentFilterForm):
    order_choices = [
        ('correlation_rank', 'correlation'),
        ('metadata_rank', 'metadata'),
    ]

    order = forms.ChoiceField(
        label='Recommendation criteria',
        choices=order_choices,
        initial=[c[0] for c in order_choices],
        required=False,
    )

    field_order = [
        'order'
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['search'].widget = \
            AutoCompleteWidget(lookups.RecExpSearchLookup)
        self.fields['name'].widget = \
            AutoCompleteWidget(lookups.RecExpNameLookup)
        self.fields['description'].widget = \
            AutoCompleteWidget(lookups.RecExpDescriptionLookup)
        self.fields['data_type'].widget = \
            AutoCompleteWidget(lookups.RecExpTypeLookup)
        self.fields['cell_type'].widget = \
            AutoCompleteWidget(lookups.RecExpCellTypeLookup)
        self.fields['assembly'].widget = \
            AutoCompleteWidget(lookups.RecExpAssemblyLookup)
        self.fields['target'].widget = \
            AutoCompleteWidget(lookups.RecExpTargetLookup)

    def get_order(self):
        return self.cleaned_data.get('order')


class PersonalExperimentFilterForm(ExperimentFilterForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['search'].widget = \
            AutoCompleteWidget(lookups.PerExpSearchLookup)
        self.fields['name'].widget = \
            AutoCompleteWidget(lookups.PerExpNameLookup)
        self.fields['description'].widget = \
            AutoCompleteWidget(lookups.PerExpDescriptionLookup)
        self.fields['data_type'].widget = \
            AutoCompleteWidget(lookups.PerExpTypeLookup)
        self.fields['cell_type'].widget = \
            AutoCompleteWidget(lookups.PerExpCellTypeLookup)
        self.fields['assembly'].widget = \
            AutoCompleteWidget(lookups.PerExpAssemblyLookup)
        self.fields['target'].widget = \
            AutoCompleteWidget(lookups.PerExpTargetLookup)


class FavoriteExperimentFilterForm(ExperimentFilterForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['search'].widget = \
            AutoCompleteWidget(lookups.FavExpSearchLookup)
        self.fields['name'].widget = \
            AutoCompleteWidget(lookups.FavExpNameLookup)
        self.fields['description'].widget = \
            AutoCompleteWidget(lookups.FavExpDescriptionLookup)
        self.fields['data_type'].widget = \
            AutoCompleteWidget(lookups.FavExpTypeLookup)
        self.fields['cell_type'].widget = \
            AutoCompleteWidget(lookups.FavExpCellTypeLookup)
        self.fields['assembly'].widget = \
            AutoCompleteWidget(lookups.FavExpAssemblyLookup)
        self.fields['target'].widget = \
            AutoCompleteWidget(lookups.FavExpTargetLookup)


class SimilarExperimentFilterForm(ExperimentFilterForm):

    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk', None)
        print('form', pk)
        super().__init__(*args, **kwargs)

        self.fields['search'].widget = \
            AutoCompleteWidget(lookups.SimExpSearchLookup)
        self.fields['name'].widget = \
            AutoCompleteWidget(lookups.SimExpNameLookup)
        self.fields['description'].widget = \
            AutoCompleteWidget(lookups.SimExpDescriptionLookup)
        self.fields['data_type'].widget = \
            AutoCompleteWidget(lookups.SimExpDataTypeLookup)
        self.fields['cell_type'].widget = \
            AutoCompleteWidget(lookups.SimExpCellTypeLookup)
        self.fields['assembly'].widget = \
            AutoCompleteWidget(lookups.SimExpAssemblyLookup)
        self.fields['target'].widget = \
            AutoCompleteWidget(lookups.SimExpTargetLookup)

        for field in self.fields:
            if isinstance(self.fields[field].widget, AutoCompleteWidget):
                self.fields[field].widget.update_query_parameters(
                    {'pk': pk})


class ExperimentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ExperimentForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

    class Meta:
        model = models.Experiment
        fields = (
            'name', 'experiment_type', 'cell_type', 'target', 'description',
        )


class DatasetForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(DatasetForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

    class Meta:
        model = models.Dataset
        fields = (
            'name', 'assembly', 'description', 'ambiguous_url', 'plus_url',
            'minus_url'
        )

    def clean(self):
        cleaned_data = super().clean()

        ambiguous_url = cleaned_data.get('ambiguous_url')
        plus_url = cleaned_data.get('plus_url')
        minus_url = cleaned_data.get('minus_url')

        error_text = 'An ambiguous URL may not be included with stranded URLs.'

        if ambiguous_url:
            if plus_url or minus_url:
                raise forms.ValidationError(error_text)
        elif plus_url and minus_url:
            if ambiguous_url:
                raise forms.ValidationError(error_text)
        else:
            raise forms.ValidationError(
                'Either ambiguous or stranded URLs required.')
