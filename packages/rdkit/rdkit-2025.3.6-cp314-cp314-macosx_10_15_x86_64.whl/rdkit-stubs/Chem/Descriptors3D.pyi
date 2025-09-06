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
descList: list  # value = [('PMI1', <function <lambda> at 0x10cc5e770>), ('PMI2', <function <lambda> at 0x10ee510c0>), ('PMI3', <function <lambda> at 0x10ee51170>), ('NPR1', <function <lambda> at 0x10ee51220>), ('NPR2', <function <lambda> at 0x10ee512d0>), ('RadiusOfGyration', <function <lambda> at 0x10ee51380>), ('InertialShapeFactor', <function <lambda> at 0x10ee51430>), ('Eccentricity', <function <lambda> at 0x10ee514e0>), ('Asphericity', <function <lambda> at 0x10ee51590>), ('SpherocityIndex', <function <lambda> at 0x10ee51640>), ('PBF', <function <lambda> at 0x10ee516f0>)]
