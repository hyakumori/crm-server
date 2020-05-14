from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser


@api_view(["POST"])
@permission_classes([IsAdminUser])
def setup(request):
    """
    Single endpoint to setup system
    :param request:
    :return:
    """
    # create super user
    # setup groups
    # setup templates
    # setup tags
    pass
