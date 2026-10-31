from django.db.models.fields import BooleanField
from django.forms import ModelForm
from django.utils import timezone
from django.core.exceptions import ValidationError

from dogs.models import Dog, Parent


class StyleFormMixin:
    """-26- Миксин (mixin) для Django-форм, добавляет CSS-классы к полям формы,
        для красивого отображения на сайте (например, при использовании стилей Bootstrap)."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fild_name, fild in self.fields.items():
            if isinstance(fild, BooleanField):
                fild.widget.attrs['class'] = "form-check-input"
            else:
                fild.widget.attrs['class'] = "form-control"



class DogForm(StyleFormMixin, ModelForm):
    """-26- Класс создает форму Django для добавления или редактирования собаки в базе данных."""
    class Meta:
        model = Dog
        exclude = ("views_counter", "owner")          # exclude - скрывает поле счётчик просмотров


class ParentForm(StyleFormMixin, ModelForm):
    """-26- Класс создает форму Django для добавления и редактирования «Родителей» (Parent),
        которая автоматически генерирует HTML-поля для ввода на основе структуры вашей модели в базе данных."""
    class Meta:
        model = Parent
        fields = "__all__"         # -26- "__all__" - все поля форм

    def clean_year_born(self):
        """-26- Метод - кастомный валидатор для конкретного поля формы (для поля year_born - года рождения)"""
        year_born = self.cleaned_data['year_born']
        current_year = timezone.now().year      # -26- получаем текущий год
        timedelta = current_year - year_born
        if timedelta >= 100:
            raise ValidationError('Собаки столько не живут, проверьте год рождения')
        return year_born