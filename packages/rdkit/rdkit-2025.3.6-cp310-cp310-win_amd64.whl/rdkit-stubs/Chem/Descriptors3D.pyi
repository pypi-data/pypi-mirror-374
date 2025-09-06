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
descList: list  # value = [('PMI1', <function <lambda> at 0x00000197E689AD40>), ('PMI2', <function <lambda> at 0x00000197EE90F640>), ('PMI3', <function <lambda> at 0x00000197EE90F6D0>), ('NPR1', <function <lambda> at 0x00000197EE90F760>), ('NPR2', <function <lambda> at 0x00000197EE90F7F0>), ('RadiusOfGyration', <function <lambda> at 0x00000197EE90F880>), ('InertialShapeFactor', <function <lambda> at 0x00000197EE90F910>), ('Eccentricity', <function <lambda> at 0x00000197EE90F9A0>), ('Asphericity', <function <lambda> at 0x00000197EE90FA30>), ('SpherocityIndex', <function <lambda> at 0x00000197EE90FAC0>), ('PBF', <function <lambda> at 0x00000197EE90FB50>)]
