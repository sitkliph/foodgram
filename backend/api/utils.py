def get_bool_field_value(user, obj, queryset):
    """
    Функция, описывающая поля MethodField.

    Используется для полей, значение которых формируется исходя из условия
    существования записи о текущум объекте в заданном QuerySet пользователя.
    """
    if user.is_anonymous:
        return False
    return queryset.filter(recipe=obj).exists()
