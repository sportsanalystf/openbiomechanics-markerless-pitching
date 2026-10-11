# OpenBiomechanics-to-OpenSim: Marker-Driven Pitching Prototype

## Overview

This project explores a workflow for connecting baseball pitching
marker trajectories with OpenSim musculoskeletal models. It includes
a synthetic-arm inverse-kinematics (IK) validation workflow and
experimental analysis of a pitching trial.

The current implementation is a **marker-driven research prototype**.
It is not yet a validated markerless motion-capture system.

## Project components

- Synthetic marker data and reproducible OpenSim smoke tests.
- Synthetic-arm inverse-kinematics generation and validation.
- Synthetic validation plots comparing recovered motion with known
  ground truth.

Real-pitch reconstruction and marker-animation outputs are experimental
work in progress and are excluded from this initial release.

## Environment

The original development environment used Windows, OpenSim 4.6,
and Python with the OpenSim Python API.

The exact Python version and package requirements may vary by script.
See `requirements-lock.txt` and the individual scripts for details.

## Synthetic validation

From PowerShell at the project root:

    $env:Path = "C:\OpenSim 4.6\bin;$env:Path"
    .\.venv\Scripts\Activate.ps1
    python .\scripts\01_synthetic_trc_smoke_test.py

Additional scripts generate synthetic arm motion, run inverse
kinematics, and compare recovered motion against synthetic ground truth.

## Experimental pitching analysis

The pitching-analysis scripts use marker trajectories and an OpenSim
model to investigate inverse kinematics and visualization.

The upstream OpenBiomechanics repository and its datasets are not
bundled in this repository. Any required source trial or upstream
resources must be obtained separately under their applicable terms.

## Limitations

The pitching IK results are experimental. Marker-to-model alignment,
marker tracking errors, model coordinate definitions, and reconstructed
motion require further validation.

In particular, large marker errors mean the resulting joint angles
must not be treated as validated biomechanical measurements or used
for clinical, player-selection, or coaching decisions without
appropriate independent validation.

The synthetic-arm tests establish a controlled software-validation
workflow; they do not establish the accuracy of the real-pitch
reconstruction.

## Data, licensing, and attribution

OpenBiomechanics is an upstream project. Its source code, datasets,
and associated assets remain subject to their respective licenses,
terms, and attribution requirements.

This repository intentionally excludes the upstream checkout and
raw source datasets. Only project code and outputs approved for
redistribution should be committed.

Review the applicable license and attribution requirements for
individual models and other third-party assets before distributing them.

## Reproducibility

Generated outputs may depend on the OpenSim version, model files,
upstream source data, and local environment. Record these dependencies
when reproducing or extending the analysis.
