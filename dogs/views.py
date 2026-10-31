from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import inlineformset_factory
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from dogs.forms import DogForm, ParentForm
from dogs.models import Dog, Parent


class DogListView(ListView):
    """-25- Контроллер автоматически создает страницу со списком всех собак.
    1. Выполняет запрос к базе данных: Dog.objects.all().
    2. Сохраняет весь список собак в переменную object_list (и дублирует в dog_list).
    3. Передает эту переменную в HTML-шаблон (по умолчанию dogs/dog_list.html) для вывода на экран."""
    model = Dog



class DogDetailView(DetailView):
    """-25 Контроллер DogDetailView открывает профиль одной конкретной собаки (её персональную карточку).
    Он делает следующее:
    1. Берет ID собаки из ссылки (например, /dogs/5/).
    2. Находит эту собаку в базе данных (если её нет — покажет ошибку 404).
    3. Передает все её данные в HTML-шаблон (dog_detail.html) для вывода на экран.
    """
    model = Dog

    def get_object(self, queryset = None):
        """-25- Метод get_object контроллера (класса представления), отвечает за подсчёт просмотров страницы
            (счётчик кликов по карточке объекта)."""
        self.object = super().get_object(queryset)
        self.object.views_counter += 1
        self.object.save()
        return self.object



class DogCreateView(CreateView, LoginRequiredMixin):

    """-25- Контроллер автоматизирует создание новой записи в базе данных через HTML-форму."""
    model = Dog
    form_class = DogForm
    success_url = reverse_lazy('dogs:dogs_list')

    def form_valid(self, form):
        dog = form.save()
        user = self.request.user
        dog.owner = user
        dog.save()
        return super().form_valid(form)



class DogUpdateView(UpdateView):
    """-25- Контроллер автоматизирует изменение (редактирование) данных уже существующей собаки в базе данных."""
    model = Dog
    form_class = DogForm
    success_url = reverse_lazy('dogs:dogs_list')

    def get_success_url(self):
        """-26- метод динамически вычисляет адрес страницы профиля конкретной собаки и
           перенаправляет пользователя туда сразу после успешного редактирования."""
        return reverse('dogs:dogs_detail', args=[self.kwargs.get('pk')])

    def get_context_data(self, **kwargs):
        """-26- Метод собрать и передать дополнительные данные в HTML-шаблон (контекст страницы),
        чтобы их можно было там отобразить."""
        context_data = super().get_context_data(**kwargs)
        DogFormset = inlineformset_factory(Dog, Parent, ParentForm, extra=1)
        if self.request.method == 'POST':
            context_data["formset"] = DogFormset(self.request.POST, instance=self.object)
        else:
            context_data["formset"] = DogFormset(instance=self.object)
        return  context_data

    def form_valid(self, form):
        """-26- Метод отвечает за финальное сохранение всех данных в базу,
            когда пользователь нажимает кнопку «Сохранить» (отправляет заполненную форму на сервер)."""
        context_data = self.get_context_data()
        formset = context_data["formset"]
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form, formset=formset))


class DogDeleteView(DeleteView):
    """-26- Контроллер автоматизирует удаление существующей записи о собаке из базы данных."""
    model = Dog
    success_url = reverse_lazy('dogs:dogs_list')