from kombu.utils.imports import symbol_by_name

from django.core.checks import run_checks
import django


class Corn(object):
    name = ''
    namespace = ''

    def __init__(self, name):
        self.name = name

    def config_from_object(self, obj, namespace='CORN'):
        self.namespace = namespace
        self._conf = symbol_by_name(obj)

    def django_setup(self):
        django.setup()

    def validate_models(self):
        self.django_setup()
        run_checks()
