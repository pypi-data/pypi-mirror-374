"""Search the "Ionizing Radiation" metrology domain of the KCDB."""

from msl.kcdb import Radiation

radiation = Radiation()

#
# Get all reference data for the "Ionizing Radiation" metrology domain
#
print(f"Getting all reference data for {radiation.DOMAIN.name}...")
metrology_areas = radiation.metrology_areas()
print(f"  There are {len(metrology_areas)} metrology areas")
branches = [b for ma in metrology_areas for b in radiation.branches(ma)]
print(f"  There are {len(branches)} branches")
nuclides = radiation.nuclides()
print(f"  There are {len(nuclides)} nuclides")
quantities = [q for b in branches for q in radiation.quantities(b)]
print(f"  There are {len(quantities)} quantities")
mediums = [m for b in branches for m in radiation.mediums(b)]
print(f"  There are {len(mediums)} mediums")
sources = [s for b in branches for s in radiation.sources(b)]
print(f"  There are {len(sources)} sources")

#
# Search the "Ionizing Radiation" database for NMIs that are capable of
# performing measurements with a source of "Beta radiation" and print
# some information about each NMI
#
print("The following NMIs have capabilities to perform measurements with Beta radiation...")
for source in radiation.filter(sources, "Beta"):
    # Here, we request the maximum number of elements that can be returned
    # by the KCDB server within a single request
    results = radiation.search(branch=source.branch, source=source, page_size=radiation.MAX_PAGE_SIZE)
    for data in results.data:
        print(f"  {data.nmi_code} ({data.instrument}): {data.radiation_specification}")
