# Figure reproduction: acute

The two reviewed figures are supplied as EPS, RGB TIFF at 600 dpi, PDF, PNG and SVG. The PNG aliases used by the manuscript retain their relative paths. Font files are not distributed; install Arial separately before reproducing the plots.

From the repository root, after installing `figure_requirements.txt`, run:

```sh
python make_nrp_figures.py --cohort acute --plot-data figures/nrp/acute_plotted_data.csv --out-dir figures/nrp
```

This mode redraws from the reviewed aggregate plotting CSV and needs no original workbooks. The source-audit mode, without `--plot-data`, requires local original exports and internal analysis JSONs; it is distinct from this portable reproduction path.

Figure 1 uses adults and matched common-support crude comparisons. Figure 2 uses all-age episodes. OPS 1-613 rates count hospital episodes with at least one coded FEES; they do not measure clinical need, unmet need or all instrumental swallowing assessments. See the accompanying legends and audited source manifest.
