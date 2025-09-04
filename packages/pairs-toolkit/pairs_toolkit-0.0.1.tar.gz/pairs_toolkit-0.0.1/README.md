# PAIRS-toolkit


**A modular Python toolkit to model, analyze, and compare pairwise velocities and dispersions.**

Developed by the PAIRS team (missing link)

---

## Features

- Predict mean pairwise velocity $v_{12}(r,a)$ and dispersion (coming soon!)
- Compare theoretical predictions to simulations
- Run parameter inference using MCMC or external tools (to be implemented: Cobaya)

---

## Project Structure

- src/model/              # Core model code
- main/                   # Scripts to run the full pipeline
- tests/                  # Unit tests
- data/                   # Input files and examples

---

##  Installation (work in progress)

```bash
git clone https://github.com/PAIRS-team/pairs-toolkit.git
cd pairs-toolkit
pip install -r requirements.txt
```


## Running the Code (work in progress)

To compute pairwise velocities:

``` python -m main.run_pipeline ```

## Tests (in progress)

```
pip install -r requirements-dev.txt
pytest tests/
```

##  Contributing

We’re excited to collaborate! Please:
	•	Use feature branches for development
	•	Write clear commit messages and PRs
	•	Open issues for bugs, questions, or ideas

## Citation

If you use this code, please cite the papers:

* Jaber M., Hellwing W.~A., Garcia-Farieta J.~E., Gupta S., Bilicki M., 2024, PhRvD, 109, 123528. doi:10.1103/PhysRevD.109.123528
* ...

## Authors (under construction)

* Mariana Jaber, [https://github.com/MarianaJBr][gh-mjaber], [INSPIRE Profile][inspire-mjaber]
* Antonela Taverna, [https://github.com/antotaverna][gh-antotaverna], [ORCID Profile][orcid-antotaverna]

  Initial developer:
* Jorge Farieta,  [https://github.com/jegarfa][gh-jorge], 

<!-- Links -->

[miniconda-site]: https://docs.conda.io/en/latest/miniconda.html

[conda-guide]: https://docs.conda.io/projects/conda/en/latest/user-guide/index.html

[poetry-url]: https://python-poetry.org/

[pypi-url]: https://pypi.org/

[conda-forge-url]: https://conda-forge.org/

[repo-url]: https://github.com/oarodriguez/cosmostat

[gh-mjaber]: https://github.com/MarianaJBr

[inspire-mjaber]: https://inspirehep.net/authors/1707914

[gh-antotaverna]: https://github.com/antotaverna

[orcid-antotaverna]: https://orcid.org/0000-0003-1864-005X

[gh-jorge]: https://github.com/jegarfa

