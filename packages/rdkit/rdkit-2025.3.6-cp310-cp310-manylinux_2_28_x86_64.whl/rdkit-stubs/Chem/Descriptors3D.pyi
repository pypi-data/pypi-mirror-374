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
descList: list  # value = [('PMI1', <function <lambda> at 0x7f84a96908b0>), ('PMI2', <function <lambda> at 0x7f8498df5f30>), ('PMI3', <function <lambda> at 0x7f8498df5fc0>), ('NPR1', <function <lambda> at 0x7f8498df6050>), ('NPR2', <function <lambda> at 0x7f8498df60e0>), ('RadiusOfGyration', <function <lambda> at 0x7f8498df6170>), ('InertialShapeFactor', <function <lambda> at 0x7f8498df6200>), ('Eccentricity', <function <lambda> at 0x7f8498df6290>), ('Asphericity', <function <lambda> at 0x7f8498df6320>), ('SpherocityIndex', <function <lambda> at 0x7f8498df63b0>), ('PBF', <function <lambda> at 0x7f8498df6440>)]
