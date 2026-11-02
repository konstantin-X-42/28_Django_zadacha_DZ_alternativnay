from http.client import HTTPResponse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.forms.models import inlineformset_factory
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from dogs.forms import DogForm, ParentForm, DogModeratorForm
from dogs.models import Dog, Parent


class DogListView(ListView):
    """-25- Контроллер автоматически создает страницу со списком всех собак.
    1. Выполняет запрос к базе данных: Dog.objects.all().
    2. Сохраняет весь список собак в переменную object_list (и дублирует в dog_list).
    3. Передает эту переменную в HTML-шаблон (по умолчанию dogs/dog_list.html) для вывода на экран."""
    model = Dog

    # -28- Метод динамической фильтрации списка собак для выполнения Задания 3
    def get_queryset(self):
        # -28- Извлекаем базовый список всех собак из базы данных
        queryset = super().get_queryset()
        user = self.request.user

        # -28- Исправление ошибки TypeError: проверяем, что пользователь авторизован, а не является анонимным гостем
        if user.is_authenticated:
            # -28- Задание 2: Если зашел суперпользователь или модератор, возвращаем абсолютно всех собак питомника
            if user.is_superuser or user.has_perm("dogs.can_edit_breed"):
                return queryset
            # -28- Задание 3: Обычным владельцам возвращаем только ИХ собственных собак
            return queryset.filter(owner=user)

        # -28- Для неавторизованных гостей возвращаем полный список (чтобы они видели карточки, но зайти внутрь не могли)
        return queryset


class HTTPResponseForbidden:
    pass


class DogDetailView(LoginRequiredMixin,
                    DetailView):  # -28- LoginRequiredMixin перенесен в начало для корректного перенаправления гостей
    """-25 Контроллер DogDetailView открывает профиль одной конкретной собаки (её персональную карточку).
    Он делает следующее:
    1. Берет ID собаки из ссылки (например, /dogs/5/).
    2. Находит эту собаку в базе данных (если её нет — покажет ошибку 404).
    3. Передает все её данные в HTML-шаблон (dog_detail.html) для вывода на экран.
    """
    model = Dog

    def get_object(self, queryset=None):
        """-25- Метод get_object контроллера (класса представления), отвечает за подсчёт просмотров страницы
            (счётчик кликов по карточке объекта)."""
        self.object = super().get_object(queryset)
        user = self.request.user  # -28- Получаем текущего пользователя для проверки прав

        # -28- Задание 3: Реализуем ограничение — карточку может открыть только владелец, суперпользователь или модератор
        if user == self.object.owner or user.is_superuser or user.has_perm("dogs.can_edit_breed"):
            self.object.views_counter += 1
            self.object.save()
            return self.object
        raise PermissionDenied


class DogCreateView(LoginRequiredMixin,
                    CreateView):  # -28- Переместили LoginRequiredMixin на первое место, защищая создание от гостей
    """-25- Контроллер автоматизирует создание новой записи в базе данных через HTML-форму."""
    model = Dog
    form_class = DogForm
    success_url = reverse_lazy('dogs:dogs_list')

    def form_valid(self, form):
        # -28- Изменено на commit=False, чтобы избежать двойного сохранения пустой формы в БД
        dog = form.save(commit=False)
        user = self.request.user
        dog.owner = user  # -28- Автоматически назначаем текущего пользователя создателем и владельцем собаки
        dog.save()
        return super().form_valid(form)


class DogUpdateView(LoginRequiredMixin,
                    UpdateView):  # -28- Оставили LoginRequiredMixin на первом месте для защиты от гостей
    """-28- Контроллер автоматизирует изменение (редактирование) данных уже существующей собаки в базе данных."""
    model = Dog
    success_url = reverse_lazy('dogs:dogs_list')

    # -28- Метод get_object проверяет права пользователя перед тем, как открыть форму редактирования
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user

        # -28- Задание 3: Изменять карточку могут только владелец, суперпользователь или модератор
        if user == obj.owner or user.is_superuser or user.has_perm("dogs.can_edit_breed"):
            return obj
        raise PermissionDenied

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
        return context_data

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

    def get_form_class(self):
        user = self.request.user
        # -28- Задание 2: Исправлено ошибочное условие True==True. Теперь проверяем, хозяин ли это или суперюзер
        if user.is_superuser or user == self.object.owner:
            return DogForm
        # -28- Задание 2: Если это модератор с кастомными правами из Meta, отдаем урезанную форму DogModeratorForm
        if user.has_perm("dogs.can_edit_breed") and user.has_perm("dogs.can_edit_description"):
            return DogModeratorForm
        raise PermissionDenied


class DogDeleteView(LoginRequiredMixin,
                    DeleteView):  # -28- Добавлен LoginRequiredMixin, чтобы гости не могли удалять собак по прямым ссылкам
    """-26- Контроллер автоматизирует удаление существующей записи о собаке из базы данных."""
    model = Dog
    success_url = reverse_lazy('dogs:dogs_list')




# -------ранее с 28 правками --------

# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.core.exceptions import PermissionDenied
# from django.forms.models import inlineformset_factory
# from django.urls import reverse_lazy, reverse
# from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
#
# from dogs.forms import DogForm, ParentForm, DogModeratorForm
# from dogs.models import Dog, Parent
#
#
# class DogListView(ListView):
#     """-25- Контроллер автоматически создает страницу со списком всех собак.
#     1. Выполняет запрос к базе данных: Dog.objects.all().
#     2. Сохраняет весь список собак в переменную object_list (и дублирует в dog_list).
#     3. Передает эту переменную в HTML-шаблон (по умолчанию dogs/dog_list.html) для вывода на экран."""
#     model = Dog
#
#
# class HTTPResponseForbidden:
#     pass
#
#
# class DogDetailView(DetailView, LoginRequiredMixin):
#     """-25 Контроллер DogDetailView открывает профиль одной конкретной собаки (её персональную карточку).
#     Он делает следующее:
#     1. Берет ID собаки из ссылки (например, /dogs/5/).
#     2. Находит эту собаку в базе данных (если её нет — покажет ошибку 404).
#     3. Передает все её данные в HTML-шаблон (dog_detail.html) для вывода на экран.
#     """
#     model = Dog
#
#     def get_object(self, queryset = None):
#         """-25- Метод get_object контроллера (класса представления), отвечает за подсчёт просмотров страницы
#             (счётчик кликов по карточке объекта)."""
#         self.object = super().get_object(queryset)
#         if self.request.user == self.object.owner:
#             self.object.views_counter += 1
#             self.object.save()
#             return self.object
#         raise PermissionDenied
#
#
#
# class DogCreateView(CreateView, LoginRequiredMixin):
#
#     """-25- Контроллер автоматизирует создание новой записи в базе данных через HTML-форму."""
#     model = Dog
#     form_class = DogForm
#     success_url = reverse_lazy('dogs:dogs_list')
#
#     def form_valid(self, form):
#         dog = form.save()
#         user = self.request.user
#         dog.owner = user
#         dog.save()
#         return super().form_valid(form)
#
#
#
# class DogUpdateView(LoginRequiredMixin, UpdateView):
#     """-28- Контроллер автоматизирует изменение (редактирование) данных уже существующей собаки в базе данных."""
#     model = Dog
#     form_class = DogForm
#     success_url = reverse_lazy('dogs:dogs_list')
#
#     def get_success_url(self):
#         """-26- метод динамически вычисляет адрес страницы профиля конкретной собаки и
#            перенаправляет пользователя туда сразу после успешного редактирования."""
#         return reverse('dogs:dogs_detail', args=[self.kwargs.get('pk')])
#
#     def get_context_data(self, **kwargs):
#         """-26- Метод собрать и передать дополнительные данные в HTML-шаблон (контекст страницы),
#         чтобы их можно было там отобразить."""
#         context_data = super().get_context_data(**kwargs)
#         DogFormset = inlineformset_factory(Dog, Parent, ParentForm, extra=1)
#         if self.request.method == 'POST':
#             context_data["formset"] = DogFormset(self.request.POST, instance=self.object)
#         else:
#             context_data["formset"] = DogFormset(instance=self.object)
#         return  context_data
#
#     def form_valid(self, form):
#         """-26- Метод отвечает за финальное сохранение всех данных в базу,
#             когда пользователь нажимает кнопку «Сохранить» (отправляет заполненную форму на сервер)."""
#         context_data = self.get_context_data()
#         formset = context_data["formset"]
#         if form.is_valid() and formset.is_valid():
#             self.object = form.save()
#             formset.instance = self.object
#             formset.save()
#             return super().form_valid(form)
#         else:
#             return self.render_to_response(self.get_context_data(form=form, formset=formset))
#
#
#     def get_form_class(self):
#         user = self.request.user
#         if user == self.request.user:
#             return DogForm
#         if user.has_perm("dogs.can_edit_breed") and user.has_perm("dogs.can_edit_description"):
#             return DogModeratorForm
#         raise PermissionDenied
#
#
# class DogDeleteView(DeleteView):
#     """-26- Контроллер автоматизирует удаление существующей записи о собаке из базы данных."""
#     model = Dog
#     success_url = reverse_lazy('dogs:dogs_list')