from uuid import UUID

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q
from djoser import signals
from djoser.views import UserViewSet
from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenViewBase

from ..api.decorators import api_validate_model
from ..activity.services import ActivityService, UserActions
from ..core.models import Paginator
from ..core.utils import default_paginator, make_error_json, make_success_json
from ..permissions import IsAdminUser, is_admin_request
from ..permissions.services import PermissionService
from ..archive.permissions import ChangeArchivePersmission

from .serializers import CustomTokenObtainPairSerializer, UserMinimalSerializer
from .types import GroupAssginmentInput, PermissionAssignmentInput

User = get_user_model()


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"


class MyFilterBackend:
    def filter_queryset(self, request, queryset, view):
        paginator = Paginator(
            sort_by=request.GET.getlist("sort_by"),
            sort_desc=request.GET.getlist("sort_desc"),
        )
        return queryset.order_by(*paginator.order_by)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.filter(~Q(email="AnonymousUser")).prefetch_related("groups")

    def get_queryset(self):
        paginator = Paginator(
            sortBy=self.request.GET.getlist("sort_by"),
            sortDesc=self.request.GET.getlist("sort_desc"),
        )
        return super().get_queryset().order_by(*paginator.order_by)

    @action(
        detail=False,
        url_path="minimal",
        methods=["get"],
        permission_classes=[ChangeArchivePersmission],
    )
    def list_minimal(self, request):
        queryset = self.get_queryset().prefetch_related("groups")
        keyword = request.GET.get("search")
        if keyword:
            queryset = queryset.filter(
                Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword)
            )
        paginator = default_paginator()
        paged_list = paginator.paginate_queryset(
            request=request, queryset=queryset, view=self
        )
        return paginator.get_paginated_response(
            UserMinimalSerializer(paged_list, many=True).data
        )

    def perform_update(self, serializer):
        viewsets.ModelViewSet.perform_update(self, serializer)

    @action(["post"], detail=False)
    def activation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        user.set_password(serializer.data["new_password"])
        user.first_name = serializer.data["first_name"]
        user.last_name = serializer.data["last_name"]
        user.is_active = True
        user.save()

        PermissionService.add_to_default_group(user)

        signals.user_activated.send(
            sender=self.__class__, user=user, request=self.request
        )

        ActivityService.log(
            UserActions.account_activated,
            model_instance=user,
            user=user,
            request=request,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, url_path="permissions", methods=["get"],
    )
    def list_permissions(self, request, pk: UUID):
        try:
            if is_admin_request(request) or str(request.user.pk) == pk:
                permissions = PermissionService.get_user_permissions(pk)
                return make_success_json(permissions)
            else:
                raise PermissionDenied()
        except Exception as e:
            return make_error_json(str(e))

    @action(
        detail=False,
        url_path="assign_groups",
        methods=["post"],
        permission_classes=[IsAdminUser],
    )
    @api_validate_model(GroupAssginmentInput)
    def assign_group(self, request, data: GroupAssginmentInput):
        try:
            results = PermissionService.assign_user_to_group(**data.dict())

            ActivityService.log(
                UserActions.group_updated,
                model_instance=results.get("user"),
                request=request,
            )

            return make_success_json(dict(groups=results.get("groups")))
        except Exception as e:
            return make_error_json(str(e))

    @action(
        detail=False,
        url_path="unassign_groups",
        methods=["post"],
        permission_classes=[IsAdminUser],
    )
    @api_validate_model(GroupAssginmentInput)
    def unassign_group(self, request, data: GroupAssginmentInput):
        try:
            results = PermissionService.unassign_user_from_group(**data.dict())

            ActivityService.log(
                UserActions.group_updated,
                model_instance=results.get("user"),
                request=request,
            )

            return make_success_json(dict(groups=results.get("groups")))
        except Exception as e:
            return make_error_json(str(e))

    @action(
        detail=False,
        url_path="assign_permissions",
        methods=["post"],
        permission_classes=[IsAdminUser],
    )
    @api_validate_model(PermissionAssignmentInput)
    def assign_object_permission(self, request, data: PermissionAssignmentInput):
        try:
            permissions = PermissionService.assign_object_permissions(**data.dict())
            return make_success_json(
                dict(permissions=[p for p in permissions.all().iterator()])
            )
        except Exception as e:
            return make_error_json(str(e))

    @action(
        detail=False,
        url_path="unassign_permissions",
        methods=["post"],
        permission_classes=[IsAdminUser],
    )
    @api_validate_model(PermissionAssignmentInput)
    def unassign_object_permission(self, request, data: PermissionAssignmentInput):
        try:
            permissions = PermissionService.unassign_object_permissions(**data.dict())
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
