from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View, TemplateView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from django.views.generic.base import ContextMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import available_attrs, method_decorator
from django.utils.cache import add_never_cache_headers
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from functools import wraps

from . import models, forms


def get_name(request):
    if request.method == 'POST':
        form = forms.DatasetForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/thanks/')
    else:
        form = forms.DatasetForm()

    return render(request, 'name.html', {'form': form})


def never_cache(view_func):
    """Add headers for no client-side caching."""
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view_func(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        add_never_cache_headers(response)
        if not response.has_header('Pragma'):
            response['Pragma'] = 'no-Cache'
        if not response.has_header('Cache-Control'):
            response['Cache-Control'] = 'no-Store, no-Cache'
        return response

    return _wrapped_view_func


@api_view()
def browser(request):
    chromosome = request.GET.get('chr')
    start = request.GET.get('start')
    end = request.GET.get('end')
    datasets = request.GET.get('datasets')
    return Response(models.Dataset.get_browser_view(chromosome, start, end, datasets))


class NeverCacheFormMixin:

    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class AddUserToFormMixin(LoginRequiredMixin):

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['owner'] = self.request.user
        return kwargs


class AddMyUserMixin(ContextMixin, LoginRequiredMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['login_user'] = models.MyUser.objects.get(user=self.request.user)
        return context


class ExperimentCreate(NeverCacheFormMixin, CreateView):
    model = models.Experiment
    # form_class = forms.DatasetForm

    # def form_valid(self, form):
    #     form.instance.slug = form.instance.name
    #     form.instance.promoter_intersection = None
    #     form.instance.enhancer_intersection = None
    #     form.instance.promoter_metaplot = None
    #     form.instance.enhancer_metaplot = None
    #
    #     self.object = form.save()
    #     self.object.owners.add(models.MyUser.objects.get(user=self.request.user))
    #     return super(DatasetCreate, self).form_valid(form)


class ExperimentUpdate(NeverCacheFormMixin, UpdateView):
    model = models.Experiment
    # form_class = forms.ExperimentForm


class ExperimentDelete(NeverCacheFormMixin, DeleteView):
    model = models.Experiment
    # form_class = forms.DatasetForm

    def get_success_url(self):
        return reverse('personal_experiments')


class Index(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('Hello, world.')


class Home(TemplateView, AddMyUserMixin):
    template_name = 'network/home.html'


class Experiment(DetailView, AddMyUserMixin):
    template_name = 'network/experiment.html'
    model = models.Experiment

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        login_user = context['login_user']
        exp = self.get_object()

        context['selectable'] = dict()
        context['selectable']['personal'] = login_user.get_personal_experiment_ids()
        context['selectable']['favorite'] = login_user.get_favorite_experiment_ids()

        context['display_data'] = exp.get_display_data(context['login_user'])

        return context


class MyUser(DetailView, AddMyUserMixin):
    template_name = 'network/user.html'
    model = models.MyUser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_user = self.get_object()
        login_user = context['login_user']

        latest = (models.Experiment.objects
                        .filter(owners__in=[my_user])
                        .latest())
        context.update(my_user.get_display_data(login_user))
        context['latest_dataset'] = latest.get_display_data(login_user)

        return context


class PersonalExperiments(ListView, AddMyUserMixin):
    model = models.Experiment
    template_name = 'network/personal_experiments.html'
    paginate_by = 2

    def get_queryset(self):
        my_user = models.MyUser.objects.get(user=self.request.user)
        qs = self.model.objects.filter(owners__in=[my_user])
        for obj in qs:
            obj.plot_data = obj.get_average_metaplots()
            obj.meta_data = obj.get_metadata(my_user)
            obj.urls = obj.get_urls()
        return qs

    def get_context_data(self, **kwargs):
        context = super(PersonalExperiments, self).get_context_data(**kwargs)
        return context


class FavoriteExperiments(TemplateView, AddMyUserMixin):
    template_name = 'network/favorite_experiments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_user = models.MyUser.objects.get(user=self.request.user)

        experiments = []
        for fav in models.ExperimentFavorite.objects.filter(owner=my_user):
            experiments.append(fav.favorite.get_display_data(my_user))

        context['experiments'] = experiments
        context['experiment_counts'] = my_user.get_experiment_counts()

        return context


class RecommendedExperiments(TemplateView, AddMyUserMixin):
    template_name = 'network/recommended_experiments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_user = models.MyUser.objects.get(user=self.request.user)

        experiments = []
        for rec in models.ExperimentRecommendation.objects.filter(owner=my_user, hidden=False):
            experiments.append(rec.get_recommendation_data(my_user))

        context['experiments'] = experiments
        context['experiment_counts'] = my_user.get_experiment_counts()

        return context


class FavoriteUsers(TemplateView, AddMyUserMixin):
    template_name = 'network/favorite_users.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_user = models.MyUser.objects.get(user=self.request.user)

        users = []
        for fav in models.UserFavorite.objects.filter(owner=my_user):
            users.append(fav.favorite.get_display_data(my_user))

        context['users'] = users
        context['user_counts'] = my_user.get_user_counts()

        return context


class RecommendedUsers(TemplateView, AddMyUserMixin):
    template_name = 'network/recommended_users.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_user = models.MyUser.objects.get(user=self.request.user)

        users = []
        for rec in models.UserRecommendation.objects.filter(owner=my_user):
            users.append(rec.recommended.get_display_data(my_user))

        context['users'] = users
        context['user_counts'] = my_user.get_user_counts()

        return context


def dataset_comparison(request, x, y):
    dataset_x = get_object_or_404(models.Dataset, pk=x)
    dataset_y = get_object_or_404(models.Dataset, pk=y)
    return render(
        request, 'network/dataset_comparison.html',
        {'dataset_x': dataset_x, 'dataset_y': dataset_y})


class TestSmallDataView(TemplateView, AddMyUserMixin):
    template_name = 'network/test_small_data_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_user = models.MyUser.objects.get(user=self.request.user)

        datasets = []
        for ds in models.Dataset.objects.filter(owners__in=[my_user]):
            datasets.append(ds.get_display_data(my_user))

        context['datasets'] = datasets
        context['dataset_counts'] = my_user.get_dataset_counts()

        return context


class TestSmallUserView(TemplateView, AddMyUserMixin):
    template_name = 'network/test_small_user_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_user = models.MyUser.objects.get(user=self.request.user)

        users = []
        for fav in models.UserFavorite.objects.filter(owner=my_user):
            users.append(fav.favorite.get_display_data(my_user))

        context['users'] = users
        context['user_counts'] = my_user.get_user_counts()

        return context
