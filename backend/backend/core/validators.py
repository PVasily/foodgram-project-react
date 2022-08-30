def cooking_time_validator(value):
    try:
        if value >= 0:
            return value
    except ValueError as error:
        error.message('Время приготовления должно быть больше нуля.')
