# api/utilities.py

from typing import Type

from django.db.models.base import ModelBase
from django.db.models import Model
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework import serializers


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
