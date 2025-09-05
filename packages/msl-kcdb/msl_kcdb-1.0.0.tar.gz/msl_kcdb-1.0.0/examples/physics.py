"""Search the "General Physics" metrology domain of the KCDB."""

from __future__ import annotations

from typing import TYPE_CHECKING

from msl.kcdb import Physics

if TYPE_CHECKING:
    from msl.kcdb.types import ResultPhysics


physics = Physics()

#
# Generate a list of all possible branches for the "General Physics" metrology domain
#
print(f"Get some reference data for {physics.DOMAIN.name}...")
metrology_areas = physics.metrology_areas()
print(f"  There are {len(metrology_areas)} metrology areas")
branches = [b for ma in metrology_areas for b in physics.branches(ma)]
print(f"  There are {len(branches)} branches")

#
# Search the "General Physics" database for NMIs that are capable of performing fibre-optic measurements
#
results: list[ResultPhysics] = []
for branch in physics.filter(branches, "Fibre optics"):
    page = 0
    while True:
        # Here, the `page_size` value is made relatively small to show how you can write
        # code that loops until all CMCs are returned. However, you could increase the
        # `page_size` value to avoid querying the KCDB database multiple times.
        result = physics.search(branch.metrology_area, branch=branch, page=page, page_size=50)
        if result.number_of_elements == 0:
            break
        results.extend(result.data)
        page += 1

#
# Print the results using the `nmi_code` attribute of each result as the sorting parameter
#
print(f"There are {len(results)} results from NMIs with fibre-optic capabilities...")
for r in sorted(results, key=lambda r: r.nmi_code):
    print(f"  {r.nmi_code}: {r.kcdb_code}, {r.individual_service_value}")
