# BayesValidRox

<div align="center">
  <img src="https://git.iws.uni-stuttgart.de/inversemodeling/bayesian-validation/-/raw/master/docs/logo/BVRLogoV03_longtext.png" alt="bayesvalidrox logo"/>
</div>

An open-source, object-oriented Python package for surrogate-assisted Bayesain Validation of computational models.
This framework provides an automated workflow for surrogate-based sensitivity analysis, Bayesian calibration, and validation of computational models with a modular structure.

[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)

## Features
* Surrogate modeling with Polynomial Chaos Expansion, Gaussian Process Emulator, mixed surrogate types
* Global sensitivity analysis using Sobol Indices
* Bayesian calibration and validation with Rejection sampling or MCMC using `emcee` package
* Bayesian model comparison with model weights or confusion matrix for multi-model setting

## Resources
The following resources are useful to get started on working with BayesValidRox:
* [BayesValidRox website](https://pages.iws.uni-stuttgart.de/inversemodeling/bayesvalidrox/)
* [User guide](https://pages.iws.uni-stuttgart.de/inversemodeling/bayesvalidrox/packagedescription.html)
* [Tutorial](https://pages.iws.uni-stuttgart.de/inversemodeling/bayesvalidrox/tutorial.html)
* [Publucation](https://jodakiss.episciences.org/15337)

Important links:
* [GitLab](https://git.iws.uni-stuttgart.de/inversemodeling/bayesvalidrox)
* [Changelog](https://git.iws.uni-stuttgart.de/inversemodeling/bayesvalidrox/-/blob/master/CHANGELOG.md?ref_type=heads)

## Authors
Best to contact: [@RKohlhaas](https://git.iws.uni-stuttgart.de/RKohlhaas), [@mariafer.morales](https://git.iws.uni-stuttgart.de/mariafer.morales)

Full list of authors: 
- [@farid](https://git.iws.uni-stuttgart.de/farid)
- [@RKohlhaas](https://git.iws.uni-stuttgart.de/RKohlhaas)
- [@mariafer.morales](https://git.iws.uni-stuttgart.de/mariafer.morales)
- [@alacheim](https://git.iws.uni-stuttgart.de/alacheim)

## Installation
The best practive is to create a virtual environment and install the package inside it.

To create and activate the virtual environment run the following command in the terminal:
```bash
  python3 -m venv bayes_env
  cd bayes_env
  source bin/activate
```
You can replace `bayes_env` with your preferred name. For more information on virtual environments see [this link](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/).

Now, you can install the latest release of the package on PyPI inside the venv with:
```bash
  pip install bayesvalidrox
```
and installing the version on the master branch can be done by cloning this repo and installing:
```bash
  git clone https://git.iws.uni-stuttgart.de/inversemodeling/bayesvalidrox.git
  cd bayesvalidrox
  pip install .
```

## Requirements
python 3.10:
* numpy>=1.23.5
* pandas==1.4.4
* joblib==1.1.1
* matplotlib==3.7.3
* seaborn==0.11.1
* scipy>=1.11.1
* scikit-learn==1.3.1
* tqdm>=4.61.1
* chaospy==4.3.3
* emcee==3.0.2
* corner==2.2.1
* h5py==3.9.0
* statsmodels==0.14.2
* multiprocess==0.70.16
* datasets==2.20.0
* umbridge==1.2.4

## TexLive for Plotting with matplotlib
Here you need super user rights
```bash
sudo apt-get install dvipng texlive-latex-extra texlive-fonts-recommended cm-super
```
