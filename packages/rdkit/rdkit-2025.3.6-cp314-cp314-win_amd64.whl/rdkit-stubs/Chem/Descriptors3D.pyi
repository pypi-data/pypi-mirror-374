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
descList: list  # value = [('PMI1', <function <lambda> at 0x000001DF2B3DA8D0>), ('PMI2', <function <lambda> at 0x000001DF2B3DAE50>), ('PMI3', <function <lambda> at 0x000001DF2B3DAF00>), ('NPR1', <function <lambda> at 0x000001DF2B3DAFB0>), ('NPR2', <function <lambda> at 0x000001DF2B3DB060>), ('RadiusOfGyration', <function <lambda> at 0x000001DF2B3DB110>), ('InertialShapeFactor', <function <lambda> at 0x000001DF2B3DB1C0>), ('Eccentricity', <function <lambda> at 0x000001DF2B3DB270>), ('Asphericity', <function <lambda> at 0x000001DF2B3DB320>), ('SpherocityIndex', <function <lambda> at 0x000001DF2B3DB3D0>), ('PBF', <function <lambda> at 0x000001DF2B3DB480>)]
