from django.core.exceptions import ImproperlyConfigured
from oscar.apps.dashboard.reports import utils
from oscar.apps.dashboard.reports.reports import ReportGenerator


class GeneratorRepository(utils.GeneratorRepository):
    generators: list[type[ReportGenerator]]

    @classmethod
    def register(cls, ReportGeneratorSubclass: type[ReportGenerator]) -> None:
        if ReportGeneratorSubclass in cls.generators:
            raise ImproperlyConfigured(
                "The class %s is already registered" % ReportGeneratorSubclass
            )
        cls.generators.append(ReportGeneratorSubclass)
