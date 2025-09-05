#!/usr/bin/env python
"""
Module documentation goes here.

Created at 20:22, 26 Apr, 2022
"""

__author__ = 'J.P. Morrissey'
__copyright__ = 'Copyright 2022-2025'
__maintainer__ = 'J.P. Morrissey'
__email__ = 'morrissey.jp@gmail.com'
__status__ = 'Development'

# Standard Library


# Imports
import numpy as np

# Local Sources
from vtkio.reader import read_vtkxml_data


from ..src.vtkio.reader.readers import UnifiedXMLReader, UnifiedHDF5Reader

#%% test xml polydata reading
plate_data = read_vtkxml_data('../TestData/vtp/plate_vectors.vtp')
map_data = read_vtkxml_data('../TestData/vtp/map.vtp')
poly_verts_data = read_vtkxml_data('../TestData/vtp/polytest.vtp')
lines_data = read_vtkxml_data('../TestData/vtp/ibm_with_data.vtp')
cow_data = read_vtkxml_data('../TestData/vtp/cow.vtp')

#%%text new xml polydata reader
xml_reader = UnifiedXMLReader('../TestData/vtp/plate_vectors.vtp')
xml_reader.read()
print(xml_reader)
print(xml_reader.data)
print(xml_reader.data.point_data.keys())
print(xml_reader.data.cell_data.keys())
print(xml_reader.data.field_data.keys())