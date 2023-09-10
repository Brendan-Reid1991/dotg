# dotg
## _It's a preliminary name!_
A small package for running quantum error correction simulations in stim. At the moment only quantum memory experiments are available, but I plan to add stability experiments in soon. 

Originally planned to be a specific implementation of Union Find, I realised I needed a package to test any new decoder on, and existing decoders to compare it to. So I built this. 

The module tree is as such:
```
dotg/
├─ experiments/
├─ src/
│  ├─ dotg/
│  │  ├─ circuits
│  │  ├─ decoders
│  │  ├─ noise
│  │  ├─ utilities/
|  │  │  ├─ stim_assets
├─ tests/
├─ coverage.sh
├─ pyproject.toml
```

The package can be built with [`poetry`](https://python-poetry.org) using `poetry install`. 
