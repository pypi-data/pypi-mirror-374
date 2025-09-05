"""
Test module for PyTorch C++ extension.
"""

import qmb.hamiltonian


def test_import() -> None:
    """
    Test the import and availability of the PyTorch C++ extension operations.
    """
    # pylint: disable=protected-access
    extension = qmb.hamiltonian.Hamiltonian._load_module()
    _ = getattr(extension, "prepare")
