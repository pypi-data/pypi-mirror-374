# Space Packet Parser

[![Conda](https://img.shields.io/conda/vn/lasp/space_packet_parser?color=42B029&logo=anaconda&logoColor=white)](https://anaconda.org/lasp/space_packet_parser)
[![PyPI](https://img.shields.io/pypi/v/space_packet_parser?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/space-packet-parser/)
[![DOI](https://zenodo.org/badge/612253190.svg)](https://doi.org/10.5281/zenodo.7735001)

[![Test Status](https://github.com/lasp/space_packet_parser/actions/workflows/tests.yml/badge.svg)](https://github.com/lasp/space_packet_parser/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/lasp/space_packet_parser/graph/badge.svg?token=VUFIN94O05)](https://codecov.io/gh/lasp/space_packet_parser)

**Documentation:** [https://space-packet-parser.readthedocs.io/en/latest/](https://space-packet-parser.readthedocs.io/en/latest/)

| **Stable ReadTheDocs Build** | [![Stable Docs](https://readthedocs.org/projects/space-packet-parser/badge/?version=stable)](https://app.readthedocs.org/projects/space-packet-parser/builds/?version__slug=stable)   |
|------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Latest ReadTheDocs Build** | [!["Latest Docs"](https://readthedocs.org/projects/space-packet-parser/badge/?version=latest)](https://app.readthedocs.org/projects/space-packet-parser/builds/?version__slug=latest) |


Space Packet Parser is a package for decoding CCSDS telemetry packets according to an XTCE packet structure definition.
It is based on the UML model of the XTCE spec and aims to support all but the most esoteric elements of the
XTCE telemetry packet specification.

Resources:
- [XTCE (Green Book - Informational Report)](https://public.ccsds.org/Pubs/660x2g2.pdf)
- [XTCE Element Description (Green Book - Informational Report)](https://public.ccsds.org/Pubs/660x1g2.pdf)
- [XTCE (Blue Book - Recommended Standard)](https://public.ccsds.org/Pubs/660x0b2.pdf)

## Installation
From PyPI
```bash
pip install space_packet_parser
```

From Anaconda (distributed on the `lasp` channel):
```bash
conda install -c lasp space_packet_parser
```

## Proud Member of the Python in Heliophysics Community (PyHC)

[<img src="https://heliopython.org/img/PyHC%20header%20logo%20500x500.png" alt="PyHC" height="70"/>](https://heliopython.org)

## Missions using Space Packet Parser

[<img src="https://imap.princeton.edu/sites/g/files/toruqf7171/files/imap-mark-hor-multicolor-dark.png" alt="IMAP" height="70"/>](https://imap.princeton.edu/)
[<img src="https://clarreo-pathfinder.larc.nasa.gov/wp-content/uploads/sites/133/2019/08/clarreo_pathfinder_mission_patch_design_v4_decal_1_24_17.png" alt="CLARREO" height="140"/>](https://clarreo-pathfinder.larc.nasa.gov/)
[<img src="https://lasp.colorado.edu/libera/files/2021/02/Libera-Logo-HiRes.png" alt="Libera" height="70"/>](https://lasp.colorado.edu/libera/)
[<img src="https://lasp.colorado.edu/ctim/files/2023/01/CTIM_LOGO_350x100_centered_transparent.png" alt="CTIM-FD" height="70"/>](https://lasp.colorado.edu/ctim/)
[<img src="https://mms.gsfc.nasa.gov/images/promotional_materials/mms_decal_rgb_4in_trabk_72dpi.png" alt="MMS-FEEPS" height="140"/>](https://lasp.colorado.edu/mms/sdc/public/)
