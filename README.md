# Pulse-Spectra-Processor 🔬
**A specialized hyperspectral data analysis tool developed for NTHU Pulse Lab.**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B.svg)](https://streamlit.io/)

## 🌟 Project Overview
This project provides a robust, web-based interface for processing raw hyperspectral data generated in the **NTHU Pulse Lab**. It automates the tedious normalization process, removes background noise, and provides high-quality visualizations for laser-material interaction research.

## 🛠️ Core Features
- **Dynamic Background Normalization**: Automatically identifies and averages background signals to normalize measurement data.
- **Signal Denoising**: Integrated Savitzky-Golay filter to smooth spectral noise while preserving peak characteristics.
- **Interactive Visualization**: Real-time plotting using Plotly with customizable axis labels and chart styles.
- **Robust Data Export**: One-click stable CSV export with UTF-8-SIG encoding for seamless Excel integration.

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- pip (Python package installer)

### Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/YourUsername/Pulse-Spectra-Processor.git](https://github.com/YourUsername/Pulse-Spectra-Processor.git)
   cd Pulse-Spectra-Processor
Install dependencies:

Bash
pip install -r requirements.txt
Run the application:

Bash
streamlit run app.py
📊 Data Pipeline
Upload: Import raw CSV data from the spectrometer.

Configure: Define the number of background columns.

Process: Execute normalization and optional filtering.

Export: Download processed data for further AI training or analysis.

🎓 Academic Context
This tool was developed as part of undergraduate research in AI-assisted laser processing at National Tsing Hua University. It aims to bridge the gap between raw experimental data and high-level analytical models.

Author: KUO, YAO-JUNG (Nelson)
Affiliation: National Tsing Hua University, IPE (PME & CS)
