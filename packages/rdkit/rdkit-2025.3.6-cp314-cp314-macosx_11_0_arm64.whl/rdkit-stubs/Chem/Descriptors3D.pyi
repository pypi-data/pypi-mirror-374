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
descList: list  # value = [('PMI1', <function <lambda> at 0x1056ee770>), ('PMI2', <function <lambda> at 0x108f86090>), ('PMI3', <function <lambda> at 0x108f86140>), ('NPR1', <function <lambda> at 0x108f861f0>), ('NPR2', <function <lambda> at 0x108f862a0>), ('RadiusOfGyration', <function <lambda> at 0x108f86350>), ('InertialShapeFactor', <function <lambda> at 0x108f86400>), ('Eccentricity', <function <lambda> at 0x108f864b0>), ('Asphericity', <function <lambda> at 0x108f86560>), ('SpherocityIndex', <function <lambda> at 0x108f86610>), ('PBF', <function <lambda> at 0x108f866c0>)]
