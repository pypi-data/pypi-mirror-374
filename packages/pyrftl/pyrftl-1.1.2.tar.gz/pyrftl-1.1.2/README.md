[![PyRFTL PyPI Version](https://img.shields.io/pypi/v/pyrftl)](https://pypi.org/project/pyrftl/)


# PyRFTL

Welcome to PyRFTL repository !

This is the official repository of *PyRFTL : an open source python tool for custom tube lens generation from off-the-shelf optics*, Becar Quentin, Montgomery Paul, Nahas Amir, and Maioli Vincent. *Optics Letters* (2025) doi: [10.1364/OL.571058](http://dx.doi.org/10.1364/OL.571058)

This Python tool is used to determine the best pair of lenses to use as a tube lens for remote refocusing or classical microscopy.


# Licensing
This software is under [GNU GPLv3 license](./LICENSES/License_GNU_GPLv3), except following files :
- copy_opm.py, schott.py and analyses_test.py are under [BSD 3-Clause License](./LICENSES/License_BSD3)


# Installation
PyRFTL necessitates the installation of Python (>3.12).
It is recommended to install [conda](https://www.anaconda.com/download/success) (Anaconda, Miniconda, ...) to create a specific environment for PyRFTL.

With Anaconda Prompt, one can use the following procedure :
- create a new environment
  ```
  conda create --name pyrftl_env python=3.12.4
  ```

- install pyrftl
  ```
  conda activate pyrftl_env
  pip install pyrftl
  ```

- (optional) To access more Schott materials (ancient materials like BK7, F3, ...), it is possible to modify the opticalglass package (not necessary if you compare new lenses) :
  1. download the Schott AGF file, which contains Schott materials information. This file is denoted below as schott-optical-glasses-preferred-and-inquiry-en.AGF. It can be downloaded on the [Schott website](https://www.schott.com/en-gb/products/optical-glass-p1000267/downloads), at datasheet *Optical Glass – Overview Glass Types (ZEMAX format)*. The AGF file is contained in the downloaded archive *schott-optical-glass-overview-zemax-format.zip*. ([Wayback Machine link](https://web.archive.org/web/20250401084236/https://www.schott.com/en-gb/products/optical-glass-p1000267/downloads))

  2. obtain conda environnement location (exemple with Anaconda Prompt) : 
     ```
     conda info
     ```
     and look for ```active env location :``` (environment can be activated with ```conda activate pyrftl_env```)

  3. in the environment directory <a name="schottclassmodification"></a> : *\Lib\site-packages\opticalglass*, replace schott.py by [src/pyrftl/rayopt/schott.py](https://gitlab.unistra.fr/opm_tools/pyrftl/-/blob/main/src/pyrftl/rayopt/schott.py) and add schott-optical-glasses-preferred-and-inquiry-en.AGF in *\Lib\site-packages\opticalglass\data*

- It is needed to have on your computer the sequential model of lenses you want to use to create pairs. Lens files should be in Zemax .zmx, CodeV .seq or RayOptics .roa format. Some can be downloaded directly from the [lenses repository](https://gitlab.unistra.fr/opm_tools/lenses), and others can be obtained on manufacturers' websites.
For some manufacturers, like Ross Optical, only zmf file can be downloaded. One can use [zmf2zmx](https://gist.github.com/ajeddeloh/0fad161538e140770308cbfc6b662b04) to split a zmf archive into zmx files. (Please note that an older Python version is needed).

- Check the system : see the [test section](#installation-check) below

- Start to use the software, see [indications](#how-to-use) below


# Installation check
To check the correct installation of the software, read the instructions in the pdf in [test directory](./test). 

# How to use
After installing the software, one can use it following these steps :
- Group all commercial lens files to use in the same directory. It can contain subfolders. 
- [GUI] In Python console, type: 
    ```
    from pyrftl.gui_main import pyrftl_gui
    pyrftl_gui()
    ```
  Then, on the displayed graphical interface, select *pair selector* and fill all necessary parameters. If needed, use *?* buttons to get explanations.
- [No GUI] To not use the graphical interface, one can set parameters in user_select_pair_successive.py, and run this file.
- Processing can take some time, advancement is shown in your IDE Python console. Do not close the GUI interface until computation is done, or results will not be exported.
- Results are exported in a csv file. When using the GUI, it is possible to see extra data of pairs. To observe a pair, use *change pair* and put the pair short name (obtained in the csv file).

# No pair is selected
In some cases, no pair is found by the system.
When it is because no pair fits the geometrical constraints, one can:
- Remove distance constraints
- Add more lenses to import
- Modify the required focal length (for remote focusing, this also implies modifying the other tube lens)
- Disable the thin lens filtering (if it was enabled)

In the case no pair has a good performance, one can:
- Remove distance constraints
- Add more lenses to import
- Reduce the spectral range
- Increase the required focal length (for remote focusing, this also implies modifying the other tube lens)
- Disable the thin lens filtering (if it was enabled)

# Issues
If you encounter some issues (which are not listed [below](#known-bugs)) or want to discuss this tool, please address them on the [Codeberg repository](https://codeberg.org/opm_tools/PyRFTL/issues).


# Others
This version of PyRFTL was tested with rayoptics 0.9.8 and PyCharm Community Edition 2024.1.1.


See [Unistra](https://gitlab.unistra.fr/opm_tools/pyrftl) and [Codeberg](https://codeberg.org/opm_tools/PyRFTL.git) repositories.

Article : [Optics Letters](http://dx.doi.org/10.1364/OL.571058)

Author Manuscript (available as of [date] after the embargo period due to copyright transfer) : [HAL]() (not yet)

Supplementary dataset : [Zenodo](https://zenodo.org/records/15780389)

Code archive : [Zenodo](https://zenodo.org/records/15780419)

Corresponding author : maioli [at] unistra.fr

# Images
Some screenshots of the software in use are shown below.

Here is the GUI when selecting desire parameters, with an helpbox.
![Image of the GUI](./demo_screenshots/tube_lens_parameters_selection.png)

Then while computing, the advancement is displayed in the IDE Python console.
![Image of the GUI](./demo_screenshots/processing.png)

When the analysis is ended, pairs can be observed in the GUI. Ray trace diagram and wavefront aberration maps can be displayed, with the wavefront aberration data returned in the Python console.
![Image of the GUI](./demo_screenshots/output_and_lens_analysis.png)

Analysis and pairs main parameters are also available in a csv text file.
![Image of the csv file](./demo_screenshots/csv.png)

# Known bugs
Here are listed some known bugs which are not yet fixed.
- The text scaling does not fully work on every pages.
- When the main windows is changed of screen, it became transparent. A temporary solution is implemented : clicking on the *cancel transparency* button resolve it.
- An optical model file .roa which is created with original opticalglass Schott class (see [above](#schottclassmodification)) cannot be opened with modified opticalglass, and vice versa.