"""
 Descriptors derived from a molecule's 3D structure

"""
from __future__ import annotations
from rdkit.Chem.Descriptors import _isCallable
from rdkit.Chem import rdMolDescriptors
__all__: list[str] = ['CalcMolDescriptors3D', 'descList', 'rdMolDescriptors']
def CalcMolDescriptors3D(mol, confId = None):
    """
    
        Compute all 3D descriptors of a molecule
        
        Arguments:
        - mol: the molecule to work with
        - confId: conformer ID to work with. If not specified the default (-1) is used
        
        Return:
        
        dict
            A dictionary with decriptor names as keys and the descriptor values as values
    
        raises a ValueError 
            If the molecule does not have conformers
        
    """
def _setupDescriptors(namespace):
    ...
descList: list  # value = [('PMI1', <function <lambda> at 0xffff7e670400>), ('PMI2', <function <lambda> at 0xffff6fd8fa60>), ('PMI3', <function <lambda> at 0xffff6fd8fba0>), ('NPR1', <function <lambda> at 0xffff6fd8fc40>), ('NPR2', <function <lambda> at 0xffff6fd8fce0>), ('RadiusOfGyration', <function <lambda> at 0xffff6fd8fd80>), ('InertialShapeFactor', <function <lambda> at 0xffff6fd8fe20>), ('Eccentricity', <function <lambda> at 0xffff6fd8fec0>), ('Asphericity', <function <lambda> at 0xffff6fd8ff60>), ('SpherocityIndex', <function <lambda> at 0xffff6fe00040>), ('PBF', <function <lambda> at 0xffff6fe000e0>)]
