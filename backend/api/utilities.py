# api/utilities.py

from typing import Type

from django.db.models.base import ModelBase
from django.db.models import Model
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.request import Request


def delete_object(model: ModelBase, fields: dict,
                  exist: bool, errors_message: str) -> Response:
    if not exist:
        return Response(
            {
                'errors': errors_message
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    get_object_or_404(model, **fields).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def response_created_object(model: Type[Model], fields: dict,
                            exist: bool, errors_message: str,
                            serializer_class: serializers.SerializerMetaclass,
                            context: dict) -> Response:
    if exist:
        return Response(
            {
                'errors': errors_message
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    serializer = serializer_class(
        model.objects.create(**fields),
        context=context
    )
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def create_or_delete_favorite_or_purchase_recipe(
        request: Request,
        pk_object: str,
        model_object: Type[Model],
        model_recipe: Type[Model],
        serializer_class: serializers.SerializerMetaclass,
        post_errors_message: str,
        delete_errors_message: str
) -> Response:
    recipe = get_object_or_404(model_recipe, pk=pk_object)
    fields = {'user': request.user, 'recipe': recipe}
    if_already_exists = model_object.objects.filter(**fields).exists()
    if request.method == 'DELETE':
        return delete_object(
            model=model_object,
            fields=fields,
            exist=if_already_exists,
            errors_message=delete_errors_message,
        )
    return response_created_object(
        model=model_object,
        fields=fields,
        exist=if_already_exists,
        errors_message=post_errors_message,
        serializer_class=serializer_class,
        context={'request': request}
    )
