# Pylele

(Pronounced as "Pie-Lay-Lay")

Python based Ukulele and other String Instrument 3D Model Generator similar to previous projects from Brian Guan:
* [Gugulele OpenSCAD](https://github.com/bguan/gugulele)
* [Gugulele OnShape](https://cad.onshape.com/documents/5d1958b45f2484ebebb64adf/w/d0b2164f9e843f6c6ce251e7/e/f0e54aef28e6154294039ef1?renderMode=0&uiState=664913bd22703c32bc251667)

The Pylele repository is currently composed of 3 subprojects:
* *pylele*: a collection of tools to design and customize ukulele and other stringed instruments. It currently only targets headless instrument. Two implementation are available:
* *B13D*: 3d design library underlying pylele. Also provide unit-testing, and lots of helping functions. The "B1" prefix is a tribute to Brian Guan who started this repository.
* *B1scad*: .scad file interpreter based on B13D. Still VERY experimental! 

Pylele ukulele generation has two main implementations:
* pylele1: first monolithic implementation that is no longer actively developed, and therefore (supposedly) stable
* pylele2: second modular implementation, that is actively developed with more options some of which a bit experimental

B13D is a portable Python 3D Modeling Library that acts as a common wrapper around the following backends:

* [CadQuery (cq)](https://github.com/CadQuery/cadquery) (Most Accurate)
* [Blender (bpy)](https://github.com/blender/blender) (*Still a little buggy...*)
* [Trimesh (tm)](https://github.com/mikedh/trimesh) (Faster)
* [SolidPython2 (sp2)](https://github.com/jeff-dh/SolidPython) (Supports .stl, .svg, .scad, and [BOSL2](https://github.com/BelfrySCAD/BOSL2) library import, fast when using manifold option)
* [manifold3d (mf)](https://github.com/elalish/manifold): (Fastests) 3d modeling library used by trimesh and openscad

Code and view generated models in your favorite development environment!

![image](https://github.com/bguan/pylele/assets/1054657/0a9001a3-1a84-4bf9-a439-4f9434c259a3)

![image](https://github.com/bguan/pylele/assets/1054657/6e3b11f1-08fd-4d8d-aaa9-e8e563bf0d08)

## Installation

### Simplest

Install with pip.

```
pip install git+https://github.com/bguan/pylele@main
pylele1 --help # first implementation, more stable
pylele2 --help # newer implementation, more options available
```

Cadquery, Trimesh and Manifold apis should be available on most systems with this method.

### Simple (for Ubuntu/Debian)

Install on Ubuntu/Debian should be as simple as running the script:

```
  ./install_dependencies.sh
  pip install -r requirements.txt
```

This was developed on Ubuntu 22.04.4.
CI is currently testing with python 3.10, 3.11, 3.12 .

### Detailed
* Python
  * **MacOS**
    * install xcode developer tools. Using admin user accout, in terminal command line shell:
      ```
      xcode-select --install
      ```
    * install Homebrew. Using admin user accout, in terminal command line shell:
      ```
      > /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
      ```
    * install Python 3.11 (Blender only support this version). Using admin user accout, in terminal command line shell:
      ```
      > brew install python@3.11
      ```
    * install Virtualenv.
      ```
      > brew install virtualenv
      ```
    * create a python 3.11 based virtual env then activate it. Using admin user accout, in terminal command line shell:
      ```
      > virtualenv --python=/opt/homebrew/bin/python3.11 venv3.11
      > . venv3.11/bin/activate
      ```
* [CadQuery](https://github.com/CadQuery/cadquery)
   * ***Note***: if you ever get error messages about bool8 missing from numpy, downgrade from numpy 2.x back to numpy 1.26.4 e.g.
     ```
     > pip install --force-reinstall numpy==1.26.4
     ```
  * Linux installation of dependencies (I tried on Intel I7 Asus laptop running Ubuntu 24.04 Noble Numbat)
    * In a terminal shell inside a python 3.11+ virtual env:
      ```
      > pip install cadquery
      > pip install PyQt5 spyder pyqtgraph logbook
      > pip install git+https://github.com/CadQuery/CQ-editor.git
      ```
  * MacOS Apple Silicon installation (I tried on M2 Macbook Air running Sonoma 14.5)
    * Due to perculiar build magic for CAD Query OCP wrapper for OCCT not yet working with pip
      (reason why CQ devs encourage using conda instead of pip, but I prefer pip for other reasons),
      I needed to download and install prebuilt wheels for caquery_ocp and nlopt
    * In a terminal shell inside a python 3.11+ virtual env:
      ```
      > wget https://github.com/biggestT/cadquery-dist-macos-arm64/releases/download/v0.0.1/cadquery_ocp-7.7.0.1-cp311-cp311-macosx_11_0_arm64.whl
      > wget https://github.com/biggestT/cadquery-dist-macos-arm64/releases/download/v0.0.1/nlopt-2.7.1-cp311-cp311-macosx_14_0_arm64.whl
      > pip install cadquery_ocp-7.7.0.1-cp311-cp311-macosx_11_0_arm64.whl
      > pip install nlopt-2.7.1-cp311-cp311-macosx_14_0_arm64.whl
      > pip install --force-reinstall numpy==1.26.4
      > pip install cadquery
      > pip install PyQt5 spyder pyqtgraph logbook
      > pip install git+https://github.com/CadQuery/CQ-editor.git
      ```
* [Blender](https://github.com/blender/blender) (*Still a little buggy...*)
  * Linux installation of dependencies (I tried on Intel I7 Asus laptop running Ubuntu 24.04 Noble Numbat)
    * In a terminal shell inside a python 3.11+ virtual env:
      ```
      > pip install bpy
      ```
  * MacOS Apple Silicon installation (I tried on M2 Macbook Air running Sonoma 14.5)
    * In a terminal shell inside a python 3.11+ virtual env:
      ```
      > pip install bpy
      ```
* [Trimesh](https://github.com/mikedh/trimesh) (*Still missing 3D text and filleting...*)
  * Linux installation of dependencies (I tried on Intel I7 Asus laptop running Ubuntu 24.04 Noble Numbat)
    * In a terminal shell inside a python 3.11+ virtual env:
      ```
      > pip install trimesh
      ```
  * MacOS Apple Silicon installation (I tried on M2 Macbook Air running Sonoma 14.5)
    * In a terminal shell inside a python 3.11+ virtual env:
      ```
      > pip install trimesh
      ```
* [SolidPython2](https://github.com/jeff-dh/SolidPython) (*Still missing filleting...*)
  * Linux installation of dependencies (I tried on Intel I7 Asus laptop running Ubuntu 24.04 Noble Numbat)
    * In a terminal shell inside a python 3.11+ virtual env:
      ```
      > sudo apt install openscad
      > pip install solidpython2
      ```
  * MacOS Apple Silicon installation (I tried on M2 Macbook Air running Sonoma 14.5)
    * In a terminal shell inside a python 3.11+ virtual env:
      ```
      > brew install openscad
      > pip install solidpython2
      ```

## Similar Projects
* [ukulele.scad](https://github.com/roadyyy/ukulele.scad)
* [ParamUKE](https://github.com/berkbig/ParamUKE)
