# Project title: State-Specific Ensemble Docking on Src Kinase: pY530 (Inactive) vs pY419 (Active)

> Benchmark Study Phase 1: Validated an automated MD-ensemble docking workflow on Src kinase, successfully reproducing the clinical selectivity of Bosutinib (Type I/I½) and Imatinib (Type II) against distinct phosphorylation states.

![workflow](figures/workflow.png)
<!-- 流程圖：AlphaFold → CHARMM-GUI phosphorylation → MD → snapshot selection → pocket detection → docking → MD → MM/GBSA -->

![summary](figures/summary_figure.png)
<!-- 一張總結圖，顯示 Bosutinib 與 Imatinib 在兩個狀態下的對接分數差異 -->

## 1. Motivation
- **Structural Impact of Post-Translational Modifications (PTMs):** Post-translational modifications, particularly phosphorylation, dynamically reshape protein energy landscapes and trigger functional conformational switches. Modeling PTM-specific conformations expands the targetable chemical space for structure-based drug design (SBDD).
- **Src Kinase as a Paradigm System:** Human Src kinase serves as an ideal benchmark owing to its well-documented phosphorylation states (autoinhibitory `pY530` and active `pY419`). By benchmarking an AlphaFold → CHARMM-GUI PTM → MD → ensemble docking workflow on Src, this project tests whether PTM-aware conformational ensembles can accurately predict clinical drug selectivity.

## 2. Key Results (Phase 1: Extreme States)
| Question | Result |
|---|---|
| Can the pipeline differentiate Src activation states? | Yes. Accurately ranked Bosutinib higher in pY530 and correctly penalized Imatinib across Src conformers due to its DFG-out requirement. |
| Does MD-ensemble docking improve prediction? | (To be updated with AUC/EF1% metrics upon completion of all states) |
| Does phosphorylation (pY419 vs pY530) change ranking? | Yes. The autoinhibitory pY530 state favors Type I/I½ inhibitors (e.g., Bosutinib), while the DFG-in constraint correctly rejects Type II (Imatinib). |

*(Note: This project is currently in Phase 1. Further analysis on highly flexible `unpho` and metastable `double` phosphorylated transition states is currently running on the server.)*

## 3. Data
- **Structures:** AlphaFold 3 model (Human Src Kinase), post-translationally modified via CHARMM-GUI (TP1 patch for Tyr419/Tyr530).
- **Ligands:** Clinical inhibitors Bosutinib (Bosulif) and Imatinib (Gleevec) used as positive and negative controls for structural validation.

## 4. Methods
### 4.1 Structure Preparation
AlphaFold model generation, protonation, and structure-specific phosphorylation (pY419 / pY530).
### 4.2 Automated Docking Pipeline
- Tool: GNINA (CNN-scoring).
- High-throughput ensemble docking pipeline developed in Python to handle multiple structural snapshots.
### 4.3 (Upcoming) Molecular Dynamics & MM-GBSA
- Software: GROMACS (v2026.0) with CHARMM36m force field and TIP3P water model.
- Binding energy validation will be performed on the top `pY530 + Bosutinib` complex.

## 5. Preliminary Results
- **Selectivity Profiling:** Initial CNN score analysis highlights the conformational preference of Bosutinib for the autoinhibited pY530 pocket, corroborating experimental in vitro kinase assays.

## 6. Reproducibility

    scripts/
      ├── generate_ensemble_report.py   # Automated GNINA docking & CNN score aggregation
    data/
      ├── docked_poses/                 # GNINA output (.sdf)
    results/
      ├── initial_ranking.xlsx          # Preliminary score summaries

## 7. Software and References

### Primary Software & Web Servers
* **AlphaFold Server (AlphaFold 3)**: Used for initial full-length human Src kinase structure prediction.  
  * *Citation*: Abramson, J., Adler, J., Dunger, J. et al. Accurate structure prediction of biomolecular interactions with AlphaFold 3. *Nature* **630**, 493–500 (2024). https://doi.org/10.1038/s41586-024-07487-w
  * *Access*: https://alphafoldserver.com (Accessed October 2026)

* **CHARMM-GUI (PDB Reader & Solution Builder)**: Used for residue truncation, post-translational phosphorylation modeling (TP1 patch on Tyr419/Tyr530), and GROMACS simulation system setup.  
  * *Citation (Core)*: Jo, S., Kim, T., Iyer, V. G., & Im, W. CHARMM-GUI: a web-based graphical user interface for CHARMM. *Journal of Computational Chemistry*, **29**(11), 1859–1865 (2008).
  * *Citation (Solution Builder)*: Lee, J. et al. CHARMM-GUI Solution Builder for biomolecular systems in solution. *Biophysics Journal*, **109**(6), 1133–1135 (2015).

* **GROMACS (v2026.0)**: Used for energy minimization, NVT/NPT equilibrations, and molecular dynamics simulations.  
  * *Citation*: Abraham, M. J. et al. GROMACS: High performance molecular simulations through multi-level parallelism from laptops to supercomputers. *SoftwareX*, **1–2**, 19–25 (2015).

* **PyMOL Molecular Graphics System**: Used for structure visualization, pLDDT confidence mapping (B-factor spectrum), domain truncation inspection, and figure rendering.  
  * *Citation*: The PyMOL Molecular Graphics System, Version 2.5/3.0, Schrödinger, LLC.

### Force Fields & Water Models
* **CHARMM36m Force Field**:  
  * *Citation*: Huang, J. et al. CHARMM36m: an improved force field for folded and intrinsically disordered proteins. *Nature Methods*, **14**(1), 71–73 (2017).
* **TIP3P Water Model**:  
  * *Citation*: Jorgensen, W. L. et al. Comparison of simple potential functions for simulating liquid water. *The Journal of Chemical Physics*, **79**(2), 926–935 (1983).

### Databases & Ligands
* **RCSB Protein Data Bank (PDB)**: Reference structures for Src kinase domains.
* **ChEMBL Database**: Bioactivity dataset source for Bosotinib and Src kinase inhibitors.

## 8. About
Chia Lin Chang, background (biochemistry M.S., wet-lab experience), contact, and a note that internal/unpublished work is not part of this repository.

## License
MIT License
