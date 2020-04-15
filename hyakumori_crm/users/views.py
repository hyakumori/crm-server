from typing import List
from uuid import UUID

from django.contrib.auth.models import Group
from djoser.views import UserViewSet
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAdminUser
from rest_framework_simplejwt.views import TokenViewBase
from rest_typed_views import Body, typed_action

from ..core.permissions import IsAdminOrSelf
from ..core.utils import default_paginator, make_error_json, make_success_json
from ..crm.restful.serializers import (
    ContactSerializer,
    CustomerSerializer,
    ForestSerializer,
)
from ..permissions.services import PermissionService
from .serializers import CustomTokenObtainPairSerializer


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"


class CustomUserViewSet(UserViewSet):
    @action(detail=True, url_path="permissions", methods=["get"])
    def list_permissions(self, request, pk: UUID):
        try:
            permissions = PermissionService.get_user_permissions(pk)
            return make_success_json(permissions)
        except Exception as e:
            return make_error_json(str(e))

    @typed_action(
        detail=True,
        url_path="forests",
        methods=["get"],
        permission_classes=[IsAdminOrSelf],
    )
    def forests(self, request, pk: UUID):
        if not request.user.is_superuser and str(request.user.id) != str(pk):
            raise PermissionDenied()
        try:
            queryset = PermissionService.get_user_manage_resource(pk, "crm", "forest")
            paginator = default_paginator()
            paged_list = paginator.paginate_queryset(
                request=request, queryset=queryset, view=self
            )
            forests = []
            for forest_customer in paged_list:
                _forest = ForestSerializer(forest_customer.forest).data
                _contact = ContactSerializer(forest_customer.contact).data
                _forest["contact"] = _contact
                forests.append(_forest)

            return paginator.get_paginated_response(forests)

        except Exception as e:
            return make_error_json(str(e))

    @typed_action(
        detail=True,
        url_path="customers",
        methods=["get"],
        permission_classes=[IsAdminOrSelf],
    )
    def customers(self, request, pk: UUID):
        if not request.user.is_superuser and str(request.user.id) != str(pk):
            raise PermissionDenied()
        try:
            queryset = PermissionService.get_user_manage_resource(pk, "crm", "customer")
            paginator = default_paginator()
            paged_list = paginator.paginate_queryset(
                request=request, queryset=queryset, view=self
            )
            customers = []
            for customer in paged_list:
                _customer = CustomerSerializer(customer).data
                _contact = ContactSerializer(
                    customer.customercontact_set.filter(is_basic=True).first().contact
                ).data
                _customer["contact"] = _contact

                customers.append(_customer)

            return paginator.get_paginated_response(customers)

        except Exception as e:
            return make_error_json(str(e))

    @typed_action(
        detail=True,
        url_path="archives",
        methods=["get"],
        permission_classes=[IsAdminOrSelf],
    )
    def archives(self, request, pk: UUID):
        return make_error_json("NotImplemented")

    @typed_action(
        detail=False,
        url_path="assign_groups",
        methods=["post"],
        permission_classes=[IsAdminUser],
    )
    def assign_group(
        self,
        request,
        user_id: UUID = Body(source="user_id"),
        group_ids: List[int] = Body(source="group_ids"),
    ):
        try:
            results = PermissionService.assign_user_to_group(user_id, group_ids)
            return make_success_json(dict(groups=results))
        except Exception as e:
            return make_error_json(str(e))

    @typed_action(
        detail=False,
        url_path="unassign_groups",
        methods=["post"],
        permission_classes=[IsAdminUser],
    )
    def unassign_group(
        self,
        request,
        user_id: UUID = Body(source="user_id"),
        group_ids: List[int] = Body(source="group_ids"),
    ):
        try:
            results = PermissionService.unassign_user_from_group(user_id, group_ids)
            return make_success_json(dict(groups=results))
        except Exception as e:
            return make_error_json(str(e))

    @typed_action(
        detail=False,
        url_path="assign_permissions",
        methods=["post"],
        permission_classes=[IsAdminUser],
    )
    def assign_object_permission(
        self,
        request,
        user_id: UUID = Body(source="user_id"),
        object_id: UUID = Body(source="object_id"),
        object_type_id: int = Body(source="object_type_id"),
        permission_ids: List[int] = Body(source="permission_ids"),
    ):
        try:
            permissions = PermissionService.assign_object_permissions(
                user_id, object_id, object_type_id, permission_ids
            )
            return make_success_json(
                dict(permissions=[p for p in permissions.all().iterator()])
            )
        except Exception as e:
            return make_error_json(str(e))

    @typed_action(
        detail=False,
        url_path="unassign_permissions",
        methods=["post"],
        permission_classes=[IsAdminUser],
    )
    def unassign_object_permission(
        self,
        request,
        user_id: UUID = Body(source="user_id"),
        object_id: UUID = Body(source="object_id"),
        object_type_id: int = Body(source="object_type_id"),
        permission_ids: List[int] = Body(source="permission_ids"),
    ):
        try:
            permissions = PermissionService.unassign_object_permissions(
                user_id, object_id, object_type_id, permission_ids
            )
            return make_success_json(
                dict(permissions=[p for p in permissions.all().iterator()])
            )
        except Exception as e:
            return make_error_json(str(e))


class TokenObtainPairView(TokenViewBase):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """

    serializer_class = CustomTokenObtainPairSerializer


token_obtain_pair = TokenObtainPairView.as_view()
