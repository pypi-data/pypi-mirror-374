"""Search the "Chemistry and Biology" metrology domain of the KCDB."""

from msl.kcdb import ChemistryBiology

chem_bio = ChemistryBiology()

#
# Get all reference data for the "Chemistry and Biology" metrology domain
#
print(f"Getting all reference data for {chem_bio.DOMAIN.name}...")
countries = chem_bio.countries()
print(f"  There are {len(countries)} countries")
analytes = chem_bio.analytes()
print(f"  There are {len(analytes)} analytes")
categories = chem_bio.categories()
print(f"  There are {len(categories)} categories")

#
# Find all analytes that are related to "boron"
#
print("All analytes related to 'boron'...")
boron_analytes = chem_bio.filter(analytes, "boron")
for analyte in boron_analytes:
    print(f"  {analyte}")

#
# Search the "Chemistry and Biology" database for NMIs that are capable of
# performing measurements with "boron" analytes and print some information
# about each NMI
#
print("All NMIs that have capabilities with 'boron' analytes...")
for analyte in boron_analytes:
    result = chem_bio.search(analyte=analyte)
    for data in result.data:
        print(f"  {data.nmi_code} ({data.category_value}): {data.nmi_service_code}")
