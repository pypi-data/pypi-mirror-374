# SED Extractor

SED Extractor is a tool from the [CADE](https://cade.irap.omp.eu) project.

It allows to extract a **Spectral Energy Distribution** from Healpix, WCS or mixture of Healpix and WCS files, in a specific
region of the sky. This tool guarantees the photometric accuracy, by using the [drizzlib library](https://cade.irap.omp.eu/dokuwiki/doku.php?id=drizzlib).

The current library is available in Python3.

If all files are in the Healpix format, mixing Allsky and Partial Healpix, use the 'mask' keyword if possible (with the
file having the less observed pixels) in order to restrict the area to find the common pixels and to significantly
reduce time computing.

If you use the SED Extractor for your research, please include the following acknowledgement in your publications:

“We acknowledge the use of the SED Extractor software provided by the Centre d'Analyse de Données Etendues (CADE), a
service of IRAP-UPS/CNRS (http://cade.irap.omp.eu, Paradis et al., 2012, A&A, 543, 103).”
