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
descList: list  # value = [('PMI1', <function <lambda> at 0xffffbc37c8b0>), ('PMI2', <function <lambda> at 0xffffaefc1f30>), ('PMI3', <function <lambda> at 0xffffaefc1fc0>), ('NPR1', <function <lambda> at 0xffffaefc2050>), ('NPR2', <function <lambda> at 0xffffaefc20e0>), ('RadiusOfGyration', <function <lambda> at 0xffffaefc2170>), ('InertialShapeFactor', <function <lambda> at 0xffffaefc2200>), ('Eccentricity', <function <lambda> at 0xffffaefc2290>), ('Asphericity', <function <lambda> at 0xffffaefc2320>), ('SpherocityIndex', <function <lambda> at 0xffffaefc23b0>), ('PBF', <function <lambda> at 0xffffaefc2440>)]
