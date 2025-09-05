# Physics

Example script showing how to use the [Physics][msl.kcdb.general_physics.Physics] class to extract information from the KCDB.

## Script

```python
--8<-- "examples/physics.py"
```

## Output

Running this script outputs the following, although, some values may change from what you observe when you run this script since information in the KCDB is continually changing.

```
Get some reference data for General physics...
  There are 7 metrology areas
  There are 32 branches
There are 122 results from NMIs with fibre-optic capabilities...
  BelGIM: COOMET-PR-BY-000007P6-1, Fibre optic power meter
  BelGIM: COOMET-PR-BY-000007P5-1, Fibre optic power meter
  CENAM: SIM-PR-MX-00000GET-1, Fibre optic power meter
  CENAM: SIM-PR-MX-00000GEK-2, Length, optical fibre
  CENAM: SIM-PR-MX-00000GEH-4, Optical spectrum analyser
  CMI: EURAMET-PR-CZ-000008P7-1, Fibre optic source
  CMI: EURAMET-PR-CZ-000008P8-1, Optical spectrum analyser
  CMI: EURAMET-PR-CZ-000008P9-1, Wavelength meter
  CMS: APMP-PR-TW-00000LD2-1, Fibre optic power meter
  CMS: APMP-PR-TW-00000LD1-1, Fibre optic power meter
  DFM: EURAMET-PR-DK-000004ZP-1, Fibre optic source
  DFM: EURAMET-PR-DK-000004ZQ-1, Optical spectrum analyser
  DFM: EURAMET-PR-DK-000004ZR-1, Optical spectrum analyser
  DFM: EURAMET-PR-DK-000004ZV-1, Fibre optic power meter
  DFM: EURAMET-PR-DK-000004ZO-1, Fibre optic source
  IO-CSIC: EURAMET-PR-ES-00000BZ0-1, Fibre optic power meter
  IO-CSIC: EURAMET-PR-ES-00000BYR-2, Dispersion slope, optical fibre
  IO-CSIC: EURAMET-PR-ES-00000BYE-4, Dispersion, optical fibre
  IO-CSIC: EURAMET-PR-ES-00000BYC-2, Optical spectrum analyser
  IO-CSIC: EURAMET-PR-ES-00000BYF-3, Zero dispersion wavelength, optical fibre
  IO-CSIC: EURAMET-PR-ES-00000BYQ-3, Dispersion, optical fibre
  IO-CSIC: EURAMET-PR-ES-00000BZK-1, Fibre optic power meter
  IO-CSIC: EURAMET-PR-ES-00000BYB-4, Fibre optic source
  IO-CSIC: EURAMET-PR-ES-00000BYD-2, Optical spectrum analyser
  KRISS: APMP-PR-KR-000009CO-3, Optical spectrum analyser
  KRISS: APMP-PR-KR-000009DE-3, Length, optical fibre
  KRISS: APMP-PR-KR-000009CR-1, Loss, optical fibre component
  KRISS: APMP-PR-KR-000009DF-2, Length, optical fibre
  KRISS: APMP-PR-KR-000009CP-6, Optical spectrum analyser
  KRISS: APMP-PR-KR-000009DC-4, Fibre optic power meter
  KRISS: APMP-PR-KR-000009DD-3, Fibre optic power meter
  KRISS: APMP-PR-KR-000009CQ-2, Spectral attenuation, optical fibre
  LAMETRO-ICE: SIM-PR-CR-00000NFW-2, Optical spectrum analyser
  LAMETRO-ICE: SIM-PR-CR-00000NFX-2, Distance scale deviation, OTDR
  LAMETRO-ICE: SIM-PR-CR-00000NG1-2, Location offset, OTDR
  LAMETRO-ICE: SIM-PR-CR-00000NG2-2, Fibre optic power meter
  LAMETRO-ICE: SIM-PR-CR-00000NFV-2, Fibre optic source
  LNE: EURAMET-PR-FR-00000CLU-2, Fibre optic power meter
  LNE: EURAMET-PR-FR-00000CLA-3, Optical spectrum analyser
  LNE: EURAMET-PR-FR-00000CLS-2, Fibre optic power meter
  LNE: EURAMET-PR-FR-00000CLT-2, Fibre optic power meter
  LNE: EURAMET-PR-FR-00000CL9-3, Fibre optic source
  METAS: EURAMET-PR-CH-00000DQA-1, Fibre optic source
  METAS: EURAMET-PR-CH-00000DQB-1, Fibre optic source
  METAS: EURAMET-PR-CH-00000DQE-1, Wavelength meter
  METAS: EURAMET-PR-CH-00000DQG-1, Loss, optical fibre component
  METAS: EURAMET-PR-CH-00000DQM-1, Location offset, OTDR
  METAS: EURAMET-PR-CH-00000DQV-1, Fibre optic power meter
  METAS: EURAMET-PR-CH-00000DQY-2, Dispersion slope, optical fibre
  METAS: EURAMET-PR-CH-00000DQ9-1, Fibre optic source
  METAS: EURAMET-PR-CH-00000DQD-1, Wavelength meter
  METAS: EURAMET-PR-CH-00000DQF-1, Spectral attenuation, optical fibre
  METAS: EURAMET-PR-CH-00000DQL-1, Location offset, OTDR
  METAS: EURAMET-PR-CH-00000DQW-1, Fibre optic power meter
  METAS: EURAMET-PR-CH-00000DQH-2, Dispersion, optical fibre
  METAS: EURAMET-PR-CH-00000DQI-2, Zero dispersion wavelength, optical fibre
  METAS: EURAMET-PR-CH-00000DQC-1, Optical spectrum analyser
  METAS: EURAMET-PR-CH-00000DQJ-1, Length, optical fibre
  METAS: EURAMET-PR-CH-00000DQK-1, Length, optical fibre
  METAS: EURAMET-PR-CH-00000DQX-2, Dispersion, optical fibre
  MIKES-Aalto: EURAMET-PR-FI-000005K4-1, Fibre optic source
  MIKES-Aalto: EURAMET-PR-FI-000005K5-1, Optical spectrum analyser
  MIKES-Aalto: EURAMET-PR-FI-000005L8-1, Fibre optic power meter
  MIKES-Aalto: EURAMET-PR-FI-000005L9-1, Fibre optic power meter
  NIM: APMP-PR-CN-00000KAZ-1, Fibre optic power meter
  NIM: APMP-PR-CN-00000KB1-1, Fibre optic source
  NIM: APMP-PR-CN-00000KB0-2, Fibre optic power meter
  NIM: APMP-PR-CN-00000KB2-1, Optical spectrum analyser
  NIM: APMP-PR-CN-00000KB3-1, Optical spectrum analyser
  NIS: AFRIMETS-PR-EG-00000N9Q-1, Fibre optic source
  NIS: AFRIMETS-PR-EG-00000N9S-1, Optical spectrum analyser
  NIS: AFRIMETS-PR-EG-00000P1H-1, Wavelength standard
  NIS: AFRIMETS-PR-EG-00000N9R-1, Fibre optic source
  NIST: SIM-PR-US-00000A2N-2, Fibre optic power meter
  NMC, A*STAR: APMP-PR-SG-0000098Y-1, Optical spectrum analyser
  NMC, A*STAR: APMP-PR-SG-0000099P-1, Fibre optic power meter
  NMC, A*STAR: APMP-PR-SG-0000098Z-1, Optical spectrum analyser
  NMC, A*STAR: APMP-PR-SG-0000099Q-1, Fibre optic power meter
  NMC, A*STAR: APMP-PR-SG-0000099R-1, Fibre optic power meter
  NMIJ AIST: APMP-PR-JP-000005SY-1, Fibre optic power meter
  NMIJ AIST: APMP-PR-JP-000005SU-2, Fibre optic power meter
  NMIJ AIST: APMP-PR-JP-000005SV-2, Fibre optic power meter
  NMIJ AIST: APMP-PR-JP-000005SX-2, Fibre optic power meter
  NMIJ AIST: APMP-PR-JP-000005SZ-1, Fibre optic power meter
  NMIJ AIST: APMP-PR-JP-000005T0-1, Fibre optic power meter
  NMIJ AIST: APMP-PR-JP-000005ST-2, Fibre optic power meter
  NMIJ AIST: APMP-PR-JP-000005SW-2, Fibre optic power meter
  NMIM: APMP-PR-MY-00000830-1, Fibre optic power meter
  NMIM: APMP-PR-MY-0000082Z-1, Fibre optic power meter
  NMISA: AFRIMETS-PR-ZA-000006FJ-1, Fibre optic source
  NMISA: AFRIMETS-PR-ZA-000006FK-1, Optical spectrum analyser
  NMISA: AFRIMETS-PR-ZA-000006FL-1, Fibre optic power meter
  NPL: EURAMET-PR-GB-000008SJ-2, Fibre optic power meter
  NPL: EURAMET-PR-GB-000008SI-2, Fibre optic power meter
  NPL: EURAMET-PR-GB-000008SH-2, Fibre optic power meter
  PTB: EURAMET-PR-DE-00000C10-2, Fibre optic power meter
  PTB: EURAMET-PR-DE-00000C03-6, Fibre optic source
  PTB: EURAMET-PR-DE-00000C04-2, Fibre optic source
  RISE: EURAMET-PR-SE-00000AYY-1, Optical spectrum analyser
  RISE: EURAMET-PR-SE-00000AYZ-1, Optical spectrum analyser
  RISE: EURAMET-PR-SE-00000AZ2-1, Fibre optic source
  RISE: EURAMET-PR-SE-00000AZN-1, Fibre optic power meter
  RISE: EURAMET-PR-SE-00000AZO-1, Fibre optic power meter
  RISE: EURAMET-PR-SE-00000AZ1-1, Fibre optic source
  RISE: EURAMET-PR-SE-00000AZP-1, Fibre optic power meter
  RISE: EURAMET-PR-SE-00000AYX-1, Fibre optic source
  RISE: EURAMET-PR-SE-00000AZ0-1, Optical spectrum analyser
  SMU: EURAMET-PR-SK-0000054W-1, Fibre optic source
  SMU: EURAMET-PR-SK-0000054X-1, Optical spectrum analyser
  VNIIOFI: COOMET-PR-RU-00000DLD-1, Dispersion, optical fibre
  VNIIOFI: COOMET-PR-RU-00000DLF-1, Zero dispersion wavelength, optical fibre
  VNIIOFI: COOMET-PR-RU-00000DLG-1, Dispersion slope, optical fibre
  VNIIOFI: COOMET-PR-RU-00000DN5-1, Fibre optic power meter
  VNIIOFI: COOMET-PR-RU-00000NTK-1, Measuring instrument
  VNIIOFI: COOMET-PR-RU-00000DLC-1, Dispersion, optical fibre
  VNIIOFI: COOMET-PR-RU-00000DLE-1, Zero dispersion wavelength, optical fibre
  VNIIOFI: COOMET-PR-RU-00000DLH-1, Dispersion slope, optical fibre
  VNIIOFI: COOMET-PR-RU-00000DN4-1, Fibre optic power meter
  VNIIOFI: COOMET-PR-RU-00000N9K-1, Wavelength meter
  VNIIOFI: COOMET-PR-RU-00000N95-1, Fibre optic source
  VNIIOFI: COOMET-PR-RU-00000N9J-1, Optical spectrum analyser
  VNIIOFI: COOMET-PR-RU-00000N9L-1, Optical fibre
```