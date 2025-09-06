# 🔬 PySEE — Interactive, Reproducible Bioinformatics Visualization for Python

[![Version](https://img.shields.io/badge/version-0.1.1-blue.svg)](https://github.com/Linnnnberg/PySEE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CI](https://github.com/Linnnnberg/PySEE/workflows/CI/badge.svg)](https://github.com/Linnnnberg/PySEE/actions)

**PySEE** is an open-source project bringing **iSEE-style linked dashboards** to the **Python bioinformatics ecosystem**.

If you use **AnnData / Scanpy / MuData / Zarr**, you know the struggle of wiring up UMAP plots, violin plots, QC panels, and genome browsers by hand. R has [Shiny](https://shiny.posit.co/) and [iSEE](https://bioconductor.org/packages/release/bioc/html/iSEE.html).

👉 **PySEE fills that gap in Python**: a lightweight, notebook-first toolkit for **interactive exploration + reproducible code export**.

---

## ✨ Features

### ✅ MVP (v0.1) - COMPLETED
- **AnnData support** out of the box with comprehensive validation
- **Four linked panels**:
  - UMAP/t-SNE/PCA embedding (interactive scatter plots)
  - Gene expression violin/box/strip plots with grouping
  - Gene expression heatmaps with hierarchical clustering
  - Quality control metrics with filtering thresholds
- **Linked selection**: brushing propagates across all panels
- **Reproducible code export**: selections → Python snippet
- **Notebook-first UX** (Jupyter/VS Code, no server setup needed)
- **Interactive visualizations** with Plotly backend
- **Data validation** and preprocessing utilities
- **CLI interface** for command-line usage

### 🚀 v0.2 - IN DEVELOPMENT
- ✅ **Heatmap Panel**: Gene expression matrices with clustering
- ✅ **QC Metrics Panel**: Data quality assessment and filtering
- 🔄 **Dot Plot Panel**: Marker gene visualization (planned)
- 🔄 **Advanced Selection Tools**: Lasso, polygon selection (planned)
- 🧬 Genome browser panels (IGV / JBrowse)
- 🧩 Spatial viewer (Vitessce) and imaging viewer (napari)
- ☁️ Cloud-scale rendering (Datashader, Zarr-backed data)
- 🎛️ Plugin system for custom panels
- 🌍 Deployment as shareable web apps (FastAPI/Dash backend)

---

## 🚀 Why PySEE?

- **Python-native**: integrates directly with AnnData, Scanpy, scvi-tools, PyTorch
- **Linked & interactive**: selections propagate across panels
- **Reproducible**: every UI action can export a Python snippet
- **Complementary**: works alongside projects like [OLAF](https://arxiv.org/abs/2504.03976) (LLM-based bioinformatics) and [OLSA](https://github.com/openlifescience-ai) (AI benchmarks) as the **visual exploration layer**

---

## 📊 Quickstart

### Installation

```bash
# Clone the repository
git clone https://github.com/Linnnnberg/PySEE.git
cd PySEE

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### System Requirements

**Local Development:**
- **Minimum**: 8 GB RAM (small datasets only)
- **Recommended**: 16 GB RAM (small + medium datasets)
- **Optimal**: 32 GB RAM (all datasets including large)

**Cloud/Server (Recommended for Large Datasets):**
- **Google Colab**: Free tier (12 GB RAM) - medium datasets
- **Google Colab Pro**: 25 GB RAM - large datasets
- **AWS/GCP**: 32+ GB RAM - very large datasets

#### Dataset Size Guidelines

| Dataset Size | Cells | Memory | Local (16GB) | Cloud/Server |
|--------------|-------|--------|--------------|--------------|
| Small        | 3K    | 350 MB | ✅ Perfect   | ✅ Perfect   |
| Medium       | 68K   | 8.5 GB | ⚠️ Caution   | ✅ Perfect   |
| Large        | 100K+ | 15+ GB | ❌ Not recommended | ✅ Recommended |

#### Check Your System

Run the system requirements checker:

```bash
python check_system_requirements.py
```

#### Cloud Deployment

For large datasets, use cloud instead of complex local memory strategies:

```python
# Google Colab example
!pip install pysee scanpy
import scanpy as sc
from pysee import PySEE

adata = sc.datasets.pbmc68k_reduced()  # 68K cells, works great in cloud
app = PySEE(adata)
# ... add panels and analyze
```

# Install PySEE in development mode
pip install -e .
```

### Basic Usage

```python
import scanpy as sc
from pysee import PySEE, UMAPPanel, ViolinPanel, HeatmapPanel, QCPanel

# Load and preprocess data
adata = sc.datasets.pbmc3k()
sc.pp.pca(adata)
sc.pp.neighbors(adata)
sc.tl.umap(adata)
sc.tl.leiden(adata)

# Create PySEE dashboard
app = PySEE(adata, title="My Analysis")

# Add UMAP panel
app.add_panel(
    "umap",
    UMAPPanel(
        panel_id="umap",
        embedding="X_umap",
        color="leiden",
        title="UMAP Plot"
    )
)

# Add violin panel
app.add_panel(
    "violin",
    ViolinPanel(
        panel_id="violin",
        gene="CD3D",  # T-cell marker
        group_by="leiden",
        title="Gene Expression"
    )
)

# Add heatmap panel
app.add_panel(
    "heatmap",
    HeatmapPanel(
        panel_id="heatmap",
        title="Gene Expression Heatmap"
    )
)

# Add QC panel
app.add_panel(
    "qc",
    QCPanel(
        panel_id="qc",
        title="Quality Control Metrics"
    )
)

# Link panels: selections propagate across all panels
app.link(source="umap", target="violin")
app.link(source="umap", target="heatmap")

# Render panels
umap_fig = app.render_panel("umap")
violin_fig = app.render_panel("violin")
heatmap_fig = app.render_panel("heatmap")
qc_fig = app.render_panel("qc")

# Display in Jupyter notebook
umap_fig.show()
violin_fig.show()
heatmap_fig.show()
qc_fig.show()

# Export reproducible code
print(app.export_code())
```

### Command Line Usage

```bash
# Run with sample data
python example.py

# Use CLI with your own data
pysee your_data.h5ad --umap-color leiden --violin-gene CD3D --violin-group leiden

# Export code instead of running dashboard
pysee your_data.h5ad --export-code > my_analysis.py
```

---

## 📚 Documentation

### Core Components

- **`PySEE`**: Main dashboard class that manages panels and interactions
- **`AnnDataWrapper`**: Data handling and validation for AnnData objects
- **`BasePanel`**: Abstract base class for all visualization panels
- **`UMAPPanel`**: Interactive scatter plots for dimensionality reduction
- **`ViolinPanel`**: Gene expression distribution plots with grouping

### Panel Types

#### UMAP Panel
```python
UMAPPanel(
    panel_id="umap",
    embedding="X_umap",  # or "X_pca", "X_tsne", etc.
    color="leiden",      # column in adata.obs for coloring
    title="UMAP Plot"
)
```

#### Violin Panel
```python
ViolinPanel(
    panel_id="violin",
    gene="CD3D",         # gene name to visualize
    group_by="leiden",   # column in adata.obs for grouping
    title="Gene Expression"
)
```

### Linking Panels
```python
# Link UMAP selections to violin plot
app.link(source="umap", target="violin")

# Multiple links
app.link("umap", "heatmap")
app.link("umap", "qc_plot")
```

### Code Export
```python
# Export current dashboard state as Python code
code = app.export_code()
print(code)

# Save to file
with open("my_analysis.py", "w") as f:
    f.write(code)
```

---

## 🧪 Examples

### Example 1: Basic Analysis
```python
# See example.py for a complete working example
python example.py
```

### Example 2: Custom Configuration
```python
# Create panels with custom settings
umap_panel = UMAPPanel(
    panel_id="custom_umap",
    embedding="X_pca",
    color="total_counts",
    title="PCA Plot"
)
umap_panel.set_point_size(5)
umap_panel.set_opacity(0.8)

violin_panel = ViolinPanel(
    panel_id="custom_violin",
    gene="MS4A1",  # B-cell marker
    group_by="leiden",
    title="B-cell Marker"
)
violin_panel.set_plot_type("box")
violin_panel.set_show_points(True)
```

---

## 🛠️ Development

### Project Structure
```
pysee/
├── core/           # Core dashboard and data handling
├── panels/         # Visualization panels
├── cli/            # Command-line interface
├── utils/          # Utility functions
└── __init__.py     # Package initialization
```

### Running Tests
```bash
# Run basic functionality test
python test_pysee.py

# Run example with real data
python example.py
```

### CI/CD Pipeline
PySEE uses GitHub Actions for automated testing and quality assurance:

- **Fast CI**: ~3 minutes with optimized dependencies
- **Multi-Python Support**: Tests on Python 3.9, 3.10, 3.11, 3.12
- **Quality Checks**: flake8, black, mypy, pytest
- **Automated Testing**: All commits and PRs are automatically tested
- **Build Verification**: Package builds and installs correctly

### Contributing

PySEE follows a **feature branch workflow** with protected main branch and automated CI/CD.

**Quick Start:**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and test locally
4. Submit a pull request to `develop` branch
5. Address review feedback
6. Wait for approval and merge

**Detailed Workflow:** See [GIT_WORKFLOW.md](GIT_WORKFLOW.md) for complete development guidelines.

**Version Strategy:** See [VERSION_STRATEGY.md](VERSION_STRATEGY.md) for release and versioning guidelines.

**Requirements:**
- All PRs must pass CI checks before merging
- Code must be reviewed by at least one maintainer
- Follow conventional commit message format
- Include tests for new features

---

## 📋 Roadmap

### v0.2 (Next Release)
- [ ] Heatmap panel for gene expression matrices
- [ ] QC metrics panel for data quality assessment
- [ ] Dot plot panel for marker gene visualization
- [ ] Enhanced selection tools (lasso, polygon selection)
- [ ] Jupyter widget integration

### v0.3 (Future)
- [ ] Genome browser integration (IGV.js)
- [ ] Spatial transcriptomics viewer (Vitessce)
- [ ] Plugin system for custom panels
- [ ] Web deployment capabilities
- [ ] Cloud-scale data support

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Inspired by [iSEE](https://bioconductor.org/packages/release/bioc/html/iSEE.html) for R
- Built on [Scanpy](https://scanpy.readthedocs.io/) and [AnnData](https://anndata.readthedocs.io/)
- Visualization powered by [Plotly](https://plotly.com/python/)

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Linnnnberg/PySEE/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Linnnnberg/PySEE/discussions)
- **Documentation**: [GitHub Wiki](https://github.com/Linnnnberg/PySEE/wiki)
