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

## TO DO

- Add some kind of circuit building functionality. A class (or group of classes) that allows for stim circuits to be built iteratively. Necessary for other items on this list.
- In `circuits`:
  - Add stability experiments
  - Add XY and XZZX codes to surface code family.
- In `decoders`:
  - Finish partial decoders
  - Write implementation of Union Find (will be separate repository).
- In `noise`:
  - More noise models!
- In `utilities`:
  - Compilation to other gate sets, and enforcing gate sets. 
  - Circuit optimisation

