# Pylele

Python based Ukulele and other String Instrument 3D Model Generator similar to my other projects:
* [Gugulele OpenSCAD](https://github.com/bguan/gugulele)
* [Gugulele OnShape](https://cad.onshape.com/documents/5d1958b45f2484ebebb64adf/w/d0b2164f9e843f6c6ce251e7/e/f0e54aef28e6154294039ef1?renderMode=0&uiState=664913bd22703c32bc251667)

Implemented by clean portable wrapper around one of the following Python 3D Modeling Library:

* [CadQuery](https://github.com/CadQuery/cadquery)
* [Blender](https://github.com/blender/blender) (*Still a little buggy...*)
* [Trimesh](https://github.com/mikedh/trimesh) - **Coming Soon!**

Code and view generated models in your favorite development environment!

![image](https://github.com/bguan/pylele/assets/1054657/0a9001a3-1a84-4bf9-a439-4f9434c259a3)

![image](https://github.com/bguan/pylele/assets/1054657/6e3b11f1-08fd-4d8d-aaa9-e8e563bf0d08)

## Dependency Installation Suggestions
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
* [Trimesh](https://github.com/mikedh/trimesh) - **Coming Soon!**
