"""
This module provides functions to combine multiple int1, int2, int4 or int8 values into a single byte.
"""

import torch


@torch.jit.script
def pack_int(tensor: torch.Tensor, size: int) -> torch.Tensor:
    """
    Combines multiple small int values into a single byte.

    Parameters
    ----------
    tensor : torch.Tensor
        The input tensor with shape ... * last_dimension.
    size : 1 | 2 | 4 | 8
        The size of the int values in bits.

    Returns
    -------
    torch.Tensor
        The packed tensor with shape ... * ((last_dimension + elements_per_byte - 1) // elements_per_byte).
    """
    assert tensor.dtype == torch.uint8
    assert size in [1, 2, 4, 8]

    # Get the shape of the input tensor
    shape = list(tensor.shape)
    # Get the size of the last dimension
    last_dim = shape.pop()
    # Get the number of elements per byte
    elements_per_byte = 8 // size

    # Calculate how many zeros need to be padded
    if last_dim % elements_per_byte != 0:
        pad = elements_per_byte - (last_dim % elements_per_byte)
        tensor = torch.nn.functional.pad(tensor, (0, pad))
        last_dim = last_dim + pad

    # Calculate the number of groups
    num_bytes = last_dim // elements_per_byte

    # Reshape the tensor to (..., num_bytes, elements_per_bytes)
    shape.append(num_bytes)
    shape.append(elements_per_byte)
    tensor = tensor.view(shape)

    # Define the weights tensor
    weights = torch.tensor([1 << i for i in range(0, 8, size)], device=tensor.device, dtype=torch.uint8)

    # Calculate the byte value for each group
    packed = torch.sum(tensor * weights, dim=-1, dtype=torch.uint8)

    assert packed.dtype == torch.uint8
    return packed


@torch.jit.script
def unpack_int(tensor: torch.Tensor, size: int, last_dim: int) -> torch.Tensor:
    """
    Unpacks bytes into multiple small int values based on the specified size.

    Parameters
    ----------
    tensor : torch.Tensor
        The packed tensor with bytes.
    size : 1 | 2 | 4 | 8
        The size of the int values in bits.
    last_dim : int
        The original size of the last dimension before packing.

    Returns
    -------
    torch.Tensor
        The unpacked tensor with shape ... * last_dim.
    """
    assert tensor.dtype == torch.uint8
    assert size in [1, 2, 4, 8]

    # Define the weights tensor and shifts tensor
    weights = torch.tensor([1 << i for i in range(8)], device=tensor.device, dtype=torch.uint8).view([8 // size, size]).sum(dim=-1, dtype=torch.uint8)
    shifts = torch.tensor(list(range(0, 8, size)), device=tensor.device, dtype=torch.uint8)

    # Calculate the unpacked values
    result = torch.bitwise_right_shift(torch.bitwise_and(tensor.unsqueeze(-1), weights), shifts)

    # Reshape the result to the original shape
    shape = list(result.shape)
    shape.append(shape.pop() * shape.pop())
    unpacked = result.view(shape)[..., :last_dim]

    assert unpacked.dtype == torch.uint8
    return unpacked
