""" Pypi setup for pylele """
from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf8') as fh:
    long_description = fh.read()

setup(
    name='pylele',
    version='0.2.0',
    license='Apache 2.0',
    author="Brian Guan, Marco Merlin",
    author_email='brian@guan.us, marcomerli@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    description="Python based Ukulele and other String Instrument 3D Model Generator.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/bguan/pylele',
    keywords='python ukulele guitar',
    install_requires=[
        "numpy==1.26.4",
        "nlopt==2.7.1",
        "cadquery==2.4.0",
        "bpy==4.0.0; python_version < '3.11'",
        "fake-bpy-module-4.0; python_version < '3.11'",
        "bpy==4.1.0; python_version == '3.11'",
        "fake-bpy-module-4.1; python_version == '3.11'",
        "trimesh==4.4.8",
        "mathutils",
        "manifold3d",
        "pillow",
        "shapely",
        "scipy",
        "networkx",
        "pyglet<2",
        "fonttools",
        "solidpython2",
        "numpy-stl",
        "packaging",
        "json-tricks",
        "openpyxl",
        "prettytable",
        # b1scad dependencies
        "sly",
        "svg2dxf @ git+https://github.com/multigcs/svg2dxf@main"
      ],
    entry_points={
        "console_scripts": [
            "pylele1=pylele.pylele1.main:pylele_main",
            "pylele2=pylele.pylele2.all_assembly:main",
            "stl2glb=b13d.conversion.stl2glb:stl2glb",
            "stlascii2stlbin=b13d.conversion.stlascii2stlbin:stlascii2stlbin",
            "scad2stl=b13d.conversion.scad2stl:scad2stl_main",
            "scad2csg=b13d.conversion.scad2csg:scad2csg",
            "b1scad=b1scad.scad2py:b1scad",
        ],
    },
)

project_urls={
    "Source": "https://github.com/bguan/pylele",
    "Tracker": "https://github.com/bguan/pylele/issues"
}
