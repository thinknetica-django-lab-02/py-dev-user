from django.http import HttpRequest
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404
from django.http.response import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.cache import cache

from .models import ItemModel, TagModel
from .forms import SendMessage

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


def index(request: HttpRequest) -> HttpResponse:
    turn_on_block = True
    return render(request, 'main/index.html', {'turn_on_block': turn_on_block})


@method_decorator(cache_page(CACHE_TTL), name='dispatch')
class ItemListView(ListView):
    model = ItemModel
    paginate_by = 5

    def get_queryset(self) -> ItemModel:
        try:
            tag = get_object_or_404(TagModel, tag=self.kwargs['tag_name'])
            return ItemModel.objects.filter(tag=tag.id, published=1)
        except KeyError:
            return ItemModel.objects.filter(published=1)


class ItemDetailView(DetailView):
    model = ItemModel

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super(ItemDetailView, self).get_context_data(**kwargs)
        amount_views = cache.get_or_set(key='amount_views', default=0, timeout=60)
        cache.set(key='amount_views', value=amount_views+1, timeout=60)
        context['amount_views'] = amount_views+1

        return context


# class UserProfileView(DetailView):
#     model = Profile
#
#
# # позже заменю на класс
# @login_required
# def update_profile(request):
#     if request.method == 'POST':
#         user_form = UserForm(request.POST, instance=request.user)
#         profile_form = ProfileForm(request.POST, instance=request.user.profile)
#         if user_form.is_valid() and profile_form.is_valid():
#             user_form.save()
#             profile_form.save()
#             return HttpResponseRedirect(reverse('profile', args=[user_form.instance.id]))
#         else:
#             messages.error(request, _('Please fix issues: '))
#     else:
#         user_form = UserForm(instance=request.user)
#         profile_form = ProfileForm(instance=request.user.profile)
#     return render(request, 'main/profile_form.html', {
#         'user_form': user_form,
#         'profile_form': profile_form
#     })


class ItemCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'main.add_item'
    model = ItemModel
    fields = '__all__'


class ItemUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'main.change_item'
    model = ItemModel
    fields = '__all__'


class ItemDeleteView(PermissionRequiredMixin, DeleteView):
    pass


@login_required
def send_message_to_email(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = SendMessage(request.POST)
        if form.is_valid():
            form.send_messages()

            return HttpResponseRedirect(reverse('index'))
    else:
        form = SendMessage()

    return render(request, 'main/send_message.html', {'form': form})
