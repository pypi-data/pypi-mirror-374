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
descList: list  # value = [('PMI1', <function <lambda> at 0x0000028670150360>), ('PMI2', <function <lambda> at 0x00000286701509A0>), ('PMI3', <function <lambda> at 0x0000028670150AE0>), ('NPR1', <function <lambda> at 0x0000028670150B80>), ('NPR2', <function <lambda> at 0x0000028670150C20>), ('RadiusOfGyration', <function <lambda> at 0x0000028670150CC0>), ('InertialShapeFactor', <function <lambda> at 0x0000028670150D60>), ('Eccentricity', <function <lambda> at 0x0000028670150E00>), ('Asphericity', <function <lambda> at 0x0000028670150EA0>), ('SpherocityIndex', <function <lambda> at 0x0000028670150F40>), ('PBF', <function <lambda> at 0x0000028670150FE0>)]
