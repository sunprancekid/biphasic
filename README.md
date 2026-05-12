# biphasic
contains model files and programs for febio simulations

## installation

### linux / macos
1. download and install febio software suite from [installation package](https://febio.org) or [source code](https://github.com/febiosoftware).
	- to check installation success, run `febio --version` from command line.
2. install python package management tool [miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install/overview).
3. download and install visualization software [plotfig](https://github.com/sunprancekid/plotfig).
4. update conda environment: `conda ...`
5. add local python code to envionrment:
	- febio software management: run `conda develope -e programs/python/` 
	- visualization software: run `conda develope -e path/to/plotfig/`


## useage

### beam bending and harmonic oscillation

see `projects.fitting.gen_pe_sweep` and `projects.fitting.gen_ve_sweep`.

- [ ] add `feb` models to `programs/python/febio/feb`.
- [ ] create protocol for poroelastic modulation of beam bending in `projects`.

### sensitivity study for poro- and viscoelastic models

- [ ] add scaling results to `results` for poro- and visco-elastic model parameters studies.

### fitting poro and visco-elastic model parameters to stress-strain data

- [ ] create object for html-style optimization files.
- [ ] update `projects.fitting` with protocol.
