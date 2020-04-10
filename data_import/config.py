import os
import sys

import django


def setup_path():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if base_dir not in sys.path:
        sys.path.append(base_dir)


def setup_django():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hyakumori_crm.settings")
    django.setup()
