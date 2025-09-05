"""Send a request to the KCDB server.

The [ChemistryBiology][msl.kcdb.chemistry_biology.ChemistryBiology],
[Physics][msl.kcdb.general_physics.Physics] and
[Radiation][msl.kcdb.ionizing_radiation.Radiation] classes all
inherit from the [KCDB][msl.kcdb.kcdb.KCDB] class so, typically, there should
be no reason to instantiate the [KCDB][msl.kcdb.kcdb.KCDB] class directly.
"""

# We could use a third-party package like "requests" or "httpx" but since the
# KCDB API is so basic (e.g., no authentication is required, trivial GET parameters),
# the builtin urllib module is sufficient.

from __future__ import annotations

import json as _json
import re
from http.client import HTTPException
from typing import TYPE_CHECKING, TypeVar
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from ._version import __version__
from .types import (
    Country,
    Domain,
    IndividualService,
    MetrologyArea,
    NonIonizingQuantity,
    ReferenceData,
    ResultsQuickSearch,
    Service,
    SubService,
)

if TYPE_CHECKING:
    from collections.abc import Iterable
    from http.client import HTTPResponse
    from typing import Any

HEADERS: dict[str, str] = {
    "User-Agent": f"msl-kcdb/{__version__}",
    "Accept": "application/json",
    "Content-Type": "application/json",
}


T = TypeVar("T", bound=ReferenceData)


def check_page_info(page: int, page_size: int) -> None:
    """Check that the page information for a request is valid."""
    if page < 0:
        msg = f"Invalid page value, {page}. Must be >= 0"
        raise ValueError(msg)

    if page_size < 1 or page_size > KCDB.MAX_PAGE_SIZE:
        msg = f"Invalid page size, {page_size}. Must be in the range [1, {KCDB.MAX_PAGE_SIZE}]"
        raise ValueError(msg)


def to_countries(countries: str | Country | Iterable[str | Country]) -> list[str]:
    """Convert the input into a list of countries."""
    if isinstance(countries, str):
        return [countries]
    if isinstance(countries, Country):
        return [countries.label]
    return [c if isinstance(c, str) else c.label for c in countries]


def to_label(obj: str | ReferenceData) -> str:
    """Convert the input into a string."""
    if isinstance(obj, str):
        return obj
    return obj.label


def to_physics_code(obj: str | Service | SubService | IndividualService) -> str:
    """Convert the input into a string."""
    if isinstance(obj, str):
        return obj
    return obj.physics_code


def _request(
    *,
    url: str,
    method: str,
    json: dict[str, bool | int | str | list[str]] | None = None,
    params: dict[str, int | str] | None = None,
    timeout: float | None = 30,
) -> Response:
    """Send a request."""
    if params:
        # The KCDB API values are either an integer or a domain-code string
        # (which does not contain spaces and only letters A-Z or a hyphen),
        # so there is no need to convert the key-value pairs to be URL safe,
        # using urllib.parse.quote_plus(), since they already are safe.
        url += "?" + "&".join(f"{key}={value}" for key, value in params.items())

    data = _json.dumps(json).encode("utf-8") if json else None

    try:
        with urlopen(Request(url, headers=HEADERS, data=data, method=method), timeout=timeout) as response:  # noqa: S310
            return Response(response)
    except HTTPError as e:
        return Response(e)
    except OSError as e:
        if "timed out" not in str(e):
            raise

    msg = f"No reply from KCDB server after {timeout} seconds"
    raise TimeoutError(msg)


class Response:
    """A response from the KCDB server."""

    def __init__(self, response: HTTPResponse | HTTPError) -> None:
        """A response from the KCDB server.

        Args:
            response: The server's response to an HTTP request.
        """
        self._url: str = response.url
        self._code: int = 0 if response.status is None else response.status
        self._reason: str = response.reason
        self._data: bytes = response.read()

    @property
    def data(self) -> bytes:
        """The response body from the server."""
        return self._data

    def json(self) -> Any:  # noqa: ANN401
        """The JSON response body from the server."""
        return _json.loads(self._data)

    @property
    def ok(self) -> bool:
        """Whether the status code of the response is `HTTP 200 OK`."""
        return self._code == 200  # noqa: PLR2004

    def raise_for_status(self) -> None:
        """Raise an [HTTPException][http.client.HTTPException] only if the server returned an error."""
        typ: str = ""
        if 400 <= self._code < 500:  # noqa: PLR2004
            typ = "Client"
        elif 500 <= self._code < 600:  # noqa: PLR2004
            typ = "Server"

        if typ:
            msg = f"{typ} Error {self._code}: reason={self._reason!r}, url={self._url!r}"
            raise HTTPException(msg)

    @property
    def status_code(self) -> int:
        """The status code of the response."""
        return self._code


class KCDB:
    """KCDB base class."""

    BASE_URL: str = "https://www.bipm.org/api/kcdb"
    """The base url to the KCDB API."""

    MAX_PAGE_SIZE: int = 10_000
    """The maximum number of elements that can be returned in a single KCDB request."""

    DOMAIN: Domain = Domain(code="UNKNOWN", name="UNKNOWN")

    def __init__(self, timeout: float | None = 30) -> None:
        """Initialise the KCDB base class.

        Args:
            timeout: The maximum number of seconds to wait for a response from the KCDB server.
        """
        self._timeout: float | None
        self.timeout = timeout

    def __repr__(self) -> str:  # pyright: ignore[reportImplicitOverride]
        """Return the object representation."""
        return f"{self.__class__.__name__}(code={self.DOMAIN.code!r}, name={self.DOMAIN.name!r})"

    def countries(self) -> list[Country]:
        """Return all countries.

        Returns:
            A list of [Country][msl.kcdb.types.Country]'s.
        """
        response = self.get(f"{KCDB.BASE_URL}/referenceData/country")
        response.raise_for_status()
        return [Country(**data) for data in response.json()["referenceData"]]

    def domains(self) -> list[Domain]:
        """Return all KCDB domains.

        Returns:
            A list of [Domain][msl.kcdb.types.Domain]s.
        """
        response = self.get(f"{KCDB.BASE_URL}/referenceData/domain")
        response.raise_for_status()
        return [Domain(**data) for data in response.json()["domains"]]

    @staticmethod
    def filter(data: Iterable[T], pattern: str, *, flags: int = 0) -> list[T]:
        """Filter the reference data based on a pattern search.

        Args:
            data: An iterable of a [ReferenceData][msl.kcdb.types.ReferenceData] subclass.
            pattern: A [regular-expression](https://regexone.com/) pattern to use to filter results.
                Uses the `label` and `value` attributes of each item in `data` to perform the filtering.
            flags: Pattern flags passed to [re.compile][].

        Returns:
            The filtered reference data.
        """
        regex = re.compile(pattern, flags=flags)
        return [item for item in data if regex.search(item.value) or regex.search(item.label)]

    def get(
        self,
        url: str,
        *,
        json: dict[str, bool | int | str | list[str]] | None = None,
        params: dict[str, int | str] | None = None,
    ) -> Response:
        """Send a GET request to the KCDB server.

        Args:
            url: The URL for the request.
            json: A JSON-serializable object to include in the body of the request.
            params: Query parameters to include in the URL.

        Returns:
            The response.
        """
        return _request(url=url, method="GET", json=json, params=params, timeout=self._timeout)

    def metrology_areas(self) -> list[MetrologyArea]:
        """Return all metrology areas.

        Returns:
            A list of [MetrologyArea][msl.kcdb.types.MetrologyArea]s.
        """
        response = self.get(
            f"{KCDB.BASE_URL}/referenceData/metrologyArea",
            params={"domainCode": self.DOMAIN.code},
        )
        response.raise_for_status()
        return [MetrologyArea(domain=self.DOMAIN, **data) for data in response.json()["referenceData"]]

    def non_ionizing_quantities(self) -> list[NonIonizingQuantity]:
        """Return all non-Ionizing Radiation quantities.

        Returns:
            A list of [NonIonizingQuantity][msl.kcdb.types.NonIonizingQuantity]'s.
        """
        response = self.get(f"{KCDB.BASE_URL}/referenceData/quantity")
        response.raise_for_status()
        return [
            NonIonizingQuantity(id=d["id"], label="", value=d["value"])
            for d in response.json()["referenceData"]
            if d["label"] is None
        ]

    def post(
        self,
        url: str,
        *,
        json: dict[str, bool | int | str | list[str]] | None = None,
        params: dict[str, int | str] | None = None,
    ) -> Response:
        """Send a POST request to the KCDB server.

        Args:
            url: The URL for the request.
            json: A JSON-serializable object to include in the body of the request.
            params: Query parameters to include in the URL.

        Returns:
            The response.
        """
        return _request(url=url, method="POST", json=json, params=params, timeout=self._timeout)

    def quick_search(
        self,
        *,
        excluded_filters: Iterable[str] | None = None,
        included_filters: Iterable[str] | None = None,
        keywords: str | None = None,
        page: int = 0,
        page_size: int = 100,
        show_table: bool = False,
    ) -> ResultsQuickSearch:
        """Perform a quick search.

        Args:
            excluded_filters: Excluded filters. _Example:_ `["cmcServices.AC current", "cmcServices.AC power"]`
            included_filters: Included filters. _Example:_ `["cmcDomain.CHEM-BIO", "cmcBranches.Dimensional metrology"]`
            keywords: Search keywords in elasticsearch format. _Example:_ `"phase OR test"`
            page: Page number requested (0 means first page).
            page_size: Maximum number of elements in a page (maximum value is 10000).
            show_table: Set to `True` to return table data.

        Returns:
            The CMC quick-search results.
        """
        check_page_info(page, page_size)

        request: dict[str, bool | str | int | list[str]] = {
            "page": page,
            "pageSize": page_size,
            "showTable": show_table,
        }

        if excluded_filters:
            request["excludedFilters"] = list(excluded_filters)

        if included_filters:
            request["includedFilters"] = list(included_filters)

        if keywords:
            request["keywords"] = keywords

        response = self.post(
            f"{KCDB.BASE_URL}/cmc/searchData/quickSearch",
            json=request,
        )
        response.raise_for_status()
        return ResultsQuickSearch(response.json())

    @property
    def timeout(self) -> float | None:
        """The timeout value, in seconds, to use for a KCDB request.

        Returns:
            The maximum number of seconds to wait for a response from the KCDB server. If `None`, there is no timeout.
        """
        return self._timeout

    @timeout.setter
    def timeout(self, value: float | None) -> None:
        if value is None or value < 0:
            self._timeout = None
        else:
            self._timeout = float(value)
