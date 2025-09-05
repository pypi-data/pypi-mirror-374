# Density Aware SMOTE

![PyPI version](https://img.shields.io/pypi/v/density-aware-smote?color=blue)
![Python versions](https://img.shields.io/pypi/pyversions/density-aware-smote)
![License](https://img.shields.io/github/license/nbeeeel/Improved-Oversampling-Density-Aware-Smote)

A Python package implementing **Density Aware SMOTE**, developed in the [**Improved-Oversampling-Density-Aware-Smote** repository](https://github.com/nbeeeel/Improved-Oversampling-Density-Aware-Smote).  
This method enhances SMOTE by generating synthetic samples based on **local data density**, reducing oversampling in sparse regions and preserving valuable patterns in dense areas.

---

##  Features
- Density-aware oversampling tuned for local distribution  
- Flexible sampling strategy: `auto`, ratio float, or custom class counts  
- Custom neighbor selection: `random`, `nearest`, `farthest`  
- Seamless integration with scikit-learn pipelines  
- Built-in visuals: class distribution, synthetic samples, decision boundaries  

---

##  Installation

```bash
pip install density-aware-smote
