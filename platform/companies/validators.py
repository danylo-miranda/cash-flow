from django.core.exceptions import ValidationError


def validate_slug(value):

    if " " in value:

        raise ValidationError(

            "Slug não pode conter espaços."

        )