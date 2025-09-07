## Install from Python Package Index (PyPI)

Selected releases are uploaded to PyPI as packaged binaries for common platforms and Python versions. You can install _pbf_ with
```
pip install pbf
```
If there is no precompiled package for your platform, a manual attempt to compile _pbf_ from source will be made.

You can take a look at the [example scripts](https://gitlab.com/hpfem/code/pbf/-/tree/master/examples?ref_type=heads) or the [test scripts](https://gitlab.com/hpfem/code/pbf/-/tree/master/tests?ref_type=heads). Make sure to select the version corresponding to your local installation, since the master branch may include recent changes that haven't made it into a new version yet. 

A good starting point may be this [transient heat conduction](https://gitlab.com/hpfem/code/pbf/-/blob/master/examples/thermal_metrics.py?ref_type=heads) example with a custom postprocessor to extract data like cooling rates or time above melting. Alternatively, [steady-state heat conduction](https://gitlab.com/hpfem/code/pbf/-/blob/master/examples/steadystate_thermal.py?ref_type=heads) can provide a quick and cheap estimate of the melt pool dimensions and the temperature field in its proximity. However, the nonlinear iterations may be a bit less robust due to the apparent heat capacity formulation.

Disclaimer: everything is experimental and subject to change :)

## Compile from source

This is intended mostly for development on _pbf_. Clone the repository recursively:
```
git clone --recursive https://gitlab.com/hpfem/code/mlhp.git
```
Create a build project using CMake and compile `pymlhpbf`. You will find pbf.py in the /bin subfolder of your build tree.
