# Metazoa Node Ages

**Repository:** [https://github.com/HussainAther/metazoa-node-ages](https://github.com/HussainAther/metazoa-node-ages)

This repository contains everything needed to measure divergence ages from Gordon (2025) Figure 1.

## Repository Structure

```
metazoa-node-ages/
├── data/
│   ├── tree_full.png         ← Full-tree image (all taxa + time axis)
│   └── scale_full.png        ← 0–2000 Ma bar (if separate)
├── scripts/
│   └── extract_metazoa_ages.py  ← Python script to skeletonize & digitize
├── results/
│   ├── tree_full_skeleton.png   ← 1 px-wide skeleton
│   ├── tree_full_overlay_detected.png  ← overlay with Seg_ID labels
│   └── tree_full_detected_segments.csv ← raw pixel→Ma table
├── docs/
│   └── summary.pdf           ← 1–2 page methods & final age table
├── .gitignore
├── LICENSE
└── README.md
```

## Usage

1. **Install dependencies**

   ```bash
   conda create -n metazoa_env python=3.9
   conda activate metazoa_env
   pip install numpy opencv-python scikit-image pandas matplotlib
   ```

2. **Prepare your figures**

   * Place `tree_full.png` and `scale_full.png` into `data/`.

3. **Run the script**

   ```bash
   python scripts/extract_metazoa_ages.py
   ```

   Outputs will appear in `results/`.

4. **Verify & read ages**

   * Open `results/tree_full_overlay_detected.png` to confirm Seg\_ID → taxon mapping.
   * Inspect `results/tree_full_detected_segments.csv` for raw ages.
   * Your final “Abbrev → Age\_MY” table is in `docs/summary.pdf`.

## License

This work is licensed under the MIT License. See [LICENSE](LICENSE) for details.

