# OpenBiomechanics-to-OpenSim prototype

## Environment
- OS: Windows
- OpenSim: 4.6
- Python: 3.13
- Python API: opensim==4.6

## Synthetic smoke test
Run from the project root in PowerShell:

    $env:Path = "C:\OpenSim 4.6\bin;$env:Path"
    .\.venv\Scripts\Activate.ps1
    python .\scripts\01_synthetic_trc_smoke_test.py

The smoke test creates synthetic marker data and verifies that OpenSim
can read it. It does not use OpenBiomechanics source data.

## Data license
Do not use OpenBiomechanics data until the applicable license and any
professional-sports restrictions have been clarified in writing.
