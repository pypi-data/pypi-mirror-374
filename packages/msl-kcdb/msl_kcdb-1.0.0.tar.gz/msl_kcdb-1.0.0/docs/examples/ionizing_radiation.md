# Ionizing Radiation

Example script showing how to use the [Radiation][msl.kcdb.ionizing_radiation.Radiation] class to extract information from the KCDB.

## Script

```python
--8<-- "examples/ionizing_radiation.py"
```

## Output

Running this script outputs the following, although, some values may change from what you observe when you run this script since information in the KCDB is continually changing.

```
Getting all reference data for Ionizing radiation...
  There are 1 metrology areas
  There are 3 branches
  There are 171 nuclides
  There are 45 quantities
  There are 25 mediums
  There are 33 sources
The following NMIs have capabilities to perform measurements with Beta radiation...
  NRSL/INER (Beta source): Sr-90/Y-90, 49 MBq (2001), ISO-6980
  Nuclear Malaysia (Personal dosimeter): ISO-6980, 1.08 GBq (2007), 11 cm to 50 cm distance
  Nuclear Malaysia (Personal dosimeter): ISO-6980, 418 MBq (2007), 11 cm to 50 cm distance
  BFKH (Dosimeter or customers artifact): ISO 6980, Pm-147, Kr-85, Sr-90/Y-90
  NMIJ AIST (Ionization chamber): Sr-90/Y-90, 460 MBq (2006.2), ISO 6980
  NMIJ AIST (Ionization chamber): Kr-85, 3.7 GBq (2006.2), ISO 6980
  NMIJ AIST (Ionization chamber): Pm-147, 3.7 GBq (2006.2), ISO 6980
  VNIIFTRI (Chemical dosimeters): 0.01 Gy s<SUP>-1</SUP> to 10 Gy s<SUP>-1</SUP> (source, 2.96 10<SUP>12</SUP> Bq, distance, 30 mm to 300 mm)
  VNIIFTRI (Chemical dosimeters): 0.01 Gy s<SUP>-1</SUP> to 10 Gy s<SUP>-1</SUP> (source, 2.96 10<SUP>12</SUP> Bq, distance, 30 mm to 300 mm)
  VNIIFTRI (Chemical dosimeters): 0.01 Gy s<SUP>-1</SUP> to 10 Gy s<SUP>-1</SUP> (source, 2.96 10<SUP>12</SUP> Bq, distance, 30 mm to 300 mm)
  VNIIFTRI (Chemical dosimeters): 0.01 Gy s<SUP>-1</SUP> to 10 Gy s<SUP>-1</SUP> (source, 2.96 10<SUP>12</SUP> Bq, distance, 30 mm to 300 mm)
  VNIIFTRI (Chemical dosimeters): 0.01 Gy s<SUP>-1</SUP> to 10 Gy s<SUP>-1</SUP> (source, 2.96 10<SUP>12</SUP> Bq, distance, 30 mm to 300 mm)
  VNIIFTRI (Calibrated field from Sr-90/Y-90 radionuclide sources): 0.01 Gy s<SUP>-1</SUP> to 10 Gy s<SUP>-1</SUP>
  VNIIM (Dosimeter): ISO 6980
  VNIIM (Dosimeter): ISO 6980
  VNIIM (Dosimeter): ISO 6980
  VNIIM (Dosimeter): ISO 6980
  VNIIM (Dosimeter): ISO 6980
  VNIIM (Dosimeter): ISO 6980
  VNIIM (Beta ray reference source): ISO 6980
  NPL (Ophthalmic applicators): Sr-90 or Ru-106 beta rays
  CIEMAT (Radiation protection dosemeter): Sr-90/Y-90 with ISO 6980 filter. Calibration at 30 cm. Levels on July 17, 2006.
  CIEMAT (Radiation protection dosemeter): Sr-90/Y-90 without ISO 6980 filter. Calibration at 11, 20, 30, 50 cm. Levels on July 17, 2006.
  CIEMAT (Radiation protection dosemeter): Kr-85   with ISO 6980 filter. Calibration at 30 cm. Levels on July 16, 2006.
  CIEMAT (Dosimeter): Sr-90/Y-90 with ISO 6980 filter. Calibration at 30 cm. Levels on July 17, 2006. Integration time 120 s - 23 h.
  CIEMAT (Dosimeter): Kr-85 with ISO 6980 filter. Calibration  at 30 cm. Levels on July 16, 2006. Integration time 120 s - 23 h.
  NIST (Extrapolation chambers): Sr-90/Y-90. Conform to ISO 6980 (1996) and ISO 6980-2 (2004)
  NIST (Beta sources): Sr-90/Y-90. Conform to ISO 6980 (1996) and ISO 6980-2 (2004)
  NIST (Personal dosimeter (TLD)): Sr-90/Y-90. Conform to ISO 6980 (1996) and ISO 6980-2 (2004)
  NIST (Extrapolation chambers): Kr-85. Conform to ISO 6980 (1996) and ISO 6980-2 (2004)
  NIST (Beta sources): Kr-85. Conform to ISO 6980 (1996) and ISO 6980-2 (2004)
  NIST (Personal dosimeter (TLD)): Kr-85. Conform to ISO 6980 (1996) and ISO 6980-2 (2004)
  ININ (Dosemeter): ISO 6980, Sr-90/Y-90
  ININ (Personal dosimeter): ISO 6980, Sr-90/Y-90
  LNE-LNHB (Personal dosimeter): ISO 6980, Pm-147, Kr-85, Sr-90/Y-90
  LNE-LNHB (Personal dosimeter): ISO 6980, Pm-147, Kr-85, Sr-90/Y-90
  LNE-LNHB (Dosemeter): ISO 6980, Pm-147, Kr-85, Sr-90/Y-90
  LNE-LNHB (Dosemeter): ISO 6980, Pm-147, Kr-85, Sr-90/Y-90
  LNE-LNHB (Dosemeter): ISO 6980, Pm-147, Kr-85, Sr-90/Y-90
  LNE-LNHB (Dosemeter): ISO 6980, Pm-147, Kr-85, Sr-90/Y-90
  PTB (Radiation source, ionization chamber or directional dosemeter or personal dosimeter): Beta radiation reference source: Pm-147 (0.22 MeV) to Ru-106 (3.5 MeV); conversion coefficients from absorbed dose to operational quantities based on measurements and Monte Carlo transport simulations
  KRISS (Personal dosimeter): Sr-90/Y-90, ISO 6980, 1.85 GBq (1994), 74 MBq (1994)
  KRISS (Ionization chamber): Sr-90/Y-90, ISO 6980, 1.85 GBq (1994), 74 MBq (1994)
  KRISS (Beta source): Sr-90/Y-90, ISO 6980
  KRISS (Protection level dosemeter): Sr-90/Y-90, ISO 6980, 1.85 GBq (1994), 74 MBq (1994)
  STUK (Beta dosimeters and other targets): Sr-90/Y-90 and Kr-85
```