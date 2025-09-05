"""Search the Chemistry and Biology database."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .kcdb import KCDB, check_page_info, to_countries, to_label
from .types import Analyte, Category, Domain, ResultsChemistryBiology

if TYPE_CHECKING:
    from collections.abc import Iterable
    from datetime import date

    from .types import Country, MetrologyArea


class ChemistryBiology(KCDB):
    """Chemistry and Biology class."""

    DOMAIN: Domain = Domain(code="CHEM-BIO", name="Chemistry and Biology")
    """The Chemistry and Biology domain."""

    def analytes(self) -> list[Analyte]:
        """Return all Chemistry and Biology analytes.

        Returns:
            A list of [Analyte][msl.kcdb.types.Analyte]s.
        """
        response = self.get(f"{KCDB.BASE_URL}/referenceData/analyte")
        response.raise_for_status()
        return [Analyte(**data) for data in response.json()["referenceData"]]

    def categories(self) -> list[Category]:
        """Return all Chemistry and Biology categories.

        Returns:
            A list of [Category][msl.kcdb.types.Category]'s.
        """
        response = self.get(f"{KCDB.BASE_URL}/referenceData/category")
        response.raise_for_status()
        return [Category(**data) for data in response.json()["referenceData"]]

    def search(
        self,
        *,
        analyte: str | Analyte | None = None,
        category: str | Category | None = None,
        countries: str | Country | Iterable[str | Country] | None = None,
        keywords: str | None = None,
        metrology_area: str | MetrologyArea = "QM",
        page: int = 0,
        page_size: int = 100,
        public_date_from: str | date | None = None,
        public_date_to: str | date | None = None,
        show_table: bool = False,
    ) -> ResultsChemistryBiology:
        """Perform a Chemistry and Biology search.

        Args:
            analyte: Analyte label. _Example:_ `"antimony"`
            category: Category label. _Example:_ `"5"`
            countries: Country label(s). _Example:_ `["CH", "FR", "JP"]`
            keywords: Search keywords in elasticsearch format. _Example:_ `"phase OR multichannel OR water"`
            metrology_area: Metrology area label. _Example:_ `"QM"`
            page: Page number requested (0 means first page).
            page_size: Maximum number of elements in a page (maximum value is 10000).
            public_date_from: Minimal publication date. _Example:_ `"2005-01-31"`
            public_date_to: Maximal publication date. _Example:_ `"2020-06-30"`
            show_table: Set to `True` to return table data.

        Returns:
            The CMC results for Chemistry and Biology.
        """
        check_page_info(page, page_size)

        request: dict[str, bool | int | str | list[str]] = {
            "page": page,
            "pageSize": page_size,
            "showTable": show_table,
        }

        request["metrologyAreaLabel"] = to_label(metrology_area)

        if analyte is not None:
            request["analyteLabel"] = to_label(analyte)

        if category:
            request["categoryLabel"] = to_label(category)

        if countries:
            request["countries"] = to_countries(countries)

        if keywords:
            request["keywords"] = keywords

        if public_date_from:
            request["publicDateFrom"] = str(public_date_from)

        if public_date_to:
            request["publicDateTo"] = str(public_date_to)

        response = self.post(
            f"{KCDB.BASE_URL}/cmc/searchData/chemistryAndBiology",
            json=request,
        )
        response.raise_for_status()
        return ResultsChemistryBiology(response.json())
