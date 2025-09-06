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
descList: list  # value = [('PMI1', <function <lambda> at 0x7f4f35cb04a0>), ('PMI2', <function <lambda> at 0x7f4f2533ba60>), ('PMI3', <function <lambda> at 0x7f4f2533bba0>), ('NPR1', <function <lambda> at 0x7f4f2533bc40>), ('NPR2', <function <lambda> at 0x7f4f2533bce0>), ('RadiusOfGyration', <function <lambda> at 0x7f4f2533bd80>), ('InertialShapeFactor', <function <lambda> at 0x7f4f2533be20>), ('Eccentricity', <function <lambda> at 0x7f4f2533bec0>), ('Asphericity', <function <lambda> at 0x7f4f2533bf60>), ('SpherocityIndex', <function <lambda> at 0x7f4f253b0040>), ('PBF', <function <lambda> at 0x7f4f253b00e0>)]
