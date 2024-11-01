#!/usr/bin/env python3

"""
    Pylele Tests
"""

import unittest
from api.pylele_api import test_api, DEFAULT_TEST_DIR

import os
import csv
from json_tricks import load

import os
import csv
from json_tricks import load

import os
import csv
from json_tricks import load

def json_to_csv(directory, output_csv):
    """
    Recursively searches for JSON files in the specified directory and its subdirectories,
    extracts data from files with '_rpt.json' in their filename using json-tricks,
    and saves it to a CSV file with separate columns for each subdirectory level.

    Parameters:
    - directory (str): Path to the root directory to search for JSON files.
    - output_csv (str): Path to the output CSV file.
    """
    rows = []
    headers = set()

    # Walk through the directory structure
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('_rpt.json'):
                file_path = os.path.join(root, file)
                try:
                    # Read JSON data from file using json-tricks
                    with open(file_path, 'r') as f:
                        data = load(f)  # Load JSON with json-tricks
                    
                    # Extract subdirectory path relative to root directory
                    subdirectory_path = os.path.relpath(root, directory)
                    subdirectories = subdirectory_path.split(os.sep)
                    
                    # Flatten JSON data to a single row dictionary
                    row = {}
                    for key, value in data.items():
                        row[key] = value
                        headers.add(key)  # Keep track of all column headers

                    # Add columns for each directory level
                    for i, subdir in enumerate(subdirectories):
                        col_name = f"subdir_level_{i + 1}"
                        row[col_name] = subdir
                        headers.add(col_name)
                    
                    # Add filename as a column
                    # row["filename"] = file
                    # headers.add("filename")
                    
                    rows.append(row)
                
                except (ValueError, IOError) as e:
                    print(f"Error reading {file_path}: {e}")

    # Sort headers so that subdir columns come first, followed by filename, then JSON keys
    sorted_headers = sorted([h for h in headers if h.startswith("subdir_level_")])
    sorted_headers.append("filename")
    sorted_headers.extend(sorted([h for h in headers if not h.startswith("subdir_level_") and h != "filename"]))
    
    # Write to CSV file
    with open(output_csv, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=sorted_headers)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Data saved to {output_csv}")

class PyleleTestMethods(unittest.TestCase):
    """Pylele Test Class"""

    ## API
    def test_mock_api(self):
        """Test Mock API"""
        test_api(api="mock")

    def test_cadquery_api(self):
        """Test Cadquery API"""
        test_api(api="cadquery")

    def test_blender_api(self):
        """Test Blender API"""
        test_api(api="blender")

    def test_trimesh_api(self):
        """Test Trimesh API"""
        test_api(api="trimesh")

    def test_solid2_api(self):
        """Test SolidPython2 API"""
        test_api(api="solid2")

    def test_manifold_api(self):
        """Test Manifold API"""
        test_api(api="manifold")

    ## Solid Parts
    from parts.tube import test_tube, test_tube_mock
    from parts.screw import test_screw, test_screw_mock
    from parts.import3d import test_import3d
    from parts.scad_example import test_scad_example
    from parts.rounded_box import test_rounded_box, test_rounded_box_mock

    ## Pylele Individual Parts
    from pylele2.pylele_frets import test_frets, test_frets_mock
    from pylele2.pylele_fretboard import test_fretboard, test_fretboard_mock
    from pylele2.pylele_fretboard_dots import (
        test_fretboard_dots,
        test_fretboard_dots_mock,
    )
    from pylele2.pylele_fretboard_spines import (
        test_fretboard_spines,
        test_fretboard_spines_mock,
    )
    from pylele2.pylele_fretboard_joint import (
        test_fretboard_joint,
        test_fretboard_joint_mock,
    )
    from pylele2.pylele_top import test_top, test_top_mock
    from pylele2.pylele_strings import test_strings, test_strings_mock
    from pylele2.pylele_nut import test_nut, test_nut_mock
    from pylele2.pylele_spines import test_spines, test_spines_mock
    from pylele2.pylele_head import test_head, test_head_mock
    from pylele2.pylele_neck_joint import test_neck_joint, test_neck_joint_mock
    from pylele2.pylele_neck import test_neck, test_neck_mock
    from pylele2.pylele_bridge import test_bridge, test_bridge_mock
    from pylele2.pylele_guide import test_guide, test_guide_mock
    from pylele2.pylele_chamber import test_chamber, test_chamber_mock
    from pylele2.pylele_peg import test_peg, test_peg_mock
    from pylele2.pylele_worm import test_worm, test_worm_mock
    from pylele2.pylele_tuners import test_tuners, test_tuners_mock
    from pylele2.pylele_body import test_body, test_body_mock
    from pylele2.pylele_texts import test_texts, test_texts_mock
    from pylele2.pylele_rim import test_rim, test_rim_mock
    from pylele2.pylele_worm_key import test_worm_key, test_worm_key_mock
    from pylele2.pylele_tail import test_tail, test_tail_mock
    from pylele2.pylele_brace import test_brace, test_brace_mock
    from pylele2.pylele_soundhole import test_soundhole, test_soundhole_mock
    from pylele2.pylele_neck_bend import test_neck_bend, test_neck_bend_mock

    ## Assemblies
    from pylele2.pylele_fretboard_assembly import (
        test_fretboard_assembly,
        test_fretboard_assembly_mock,
    )
    from pylele2.pylele_neck_assembly import test_neck_assembly, test_neck_assembly_mock
    from pylele2.pylele_top_assembly import test_top_assembly, test_top_assembly_mock
    from pylele2.pylele_bottom_assembly import (
        test_bottom_assembly,
        test_bottom_assembly_mock,
    )
    from pylele2.pylele_all_assembly import test_all_assembly, test_all_assembly_mock

    def test_report(self):
        """ Generate Test Report """
        print("# Generate Test Report")
        json_to_csv(DEFAULT_TEST_DIR, os.path.join(DEFAULT_TEST_DIR,"test_report.csv"))

if __name__ == "__main__":
    unittest.main()
