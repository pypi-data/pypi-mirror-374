from __future__ import annotations

from datetime import datetime
from typing import Any

from django import forms
from django.utils.translation import gettext_lazy as _
from oscar.forms.widgets import DateTimePickerInput

from .utils import GeneratorRepository


class ReportForm(forms.Form):
    generators = GeneratorRepository().get_report_generators()
    type_choices = []
    for generator in generators:
        type_choices.append((generator.code, generator.description))

    report_type = forms.ChoiceField(
        widget=forms.Select(),
        choices=type_choices,
        label=_("Report Type"),
        help_text=_("Only the offer and order reports use the selected date range"),
    )

    date_from = forms.DateTimeField(
        label=_("Date from"),
        required=False,
        widget=DateTimePickerInput,
    )

    date_to = forms.DateTimeField(
        label=_("Date to"),
        help_text=_("The report is inclusive of this date"),
        required=False,
        widget=DateTimePickerInput,
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # get any newly registered generators
        type_choices = [
            ((generator.code, generator.description)) for generator in self.generators
        ]
        self.fields["report_type"].choices = type_choices  # type:ignore[attr-defined]

    def clean(self) -> dict[str, str | datetime | None]:
        date_from = self.cleaned_data.get("date_from", None)
        date_to = self.cleaned_data.get("date_to", None)
        if (
            all([date_from, date_to])
            and self.cleaned_data["date_from"] > self.cleaned_data["date_to"]
        ):
            raise forms.ValidationError(
                _("Your start date must be before your end date")
            )
        return self.cleaned_data
