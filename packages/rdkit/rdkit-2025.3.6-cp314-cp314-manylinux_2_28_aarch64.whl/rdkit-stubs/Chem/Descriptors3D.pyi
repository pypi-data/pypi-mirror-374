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
descList: list  # value = [('PMI1', <function <lambda> at 0xffff80f3c250>), ('PMI2', <function <lambda> at 0xffff7284ada0>), ('PMI3', <function <lambda> at 0xffff7284ae50>), ('NPR1', <function <lambda> at 0xffff7284af00>), ('NPR2', <function <lambda> at 0xffff7284afb0>), ('RadiusOfGyration', <function <lambda> at 0xffff7284b060>), ('InertialShapeFactor', <function <lambda> at 0xffff7284b110>), ('Eccentricity', <function <lambda> at 0xffff7284b1c0>), ('Asphericity', <function <lambda> at 0xffff7284b270>), ('SpherocityIndex', <function <lambda> at 0xffff7284b320>), ('PBF', <function <lambda> at 0xffff7284b3d0>)]
