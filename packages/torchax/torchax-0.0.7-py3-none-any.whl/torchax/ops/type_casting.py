
from torchax import config
from torchax.ops import mappings
import jax.numpy as jnp
import torch

def maybe_cast(result, torch_op):
  """Casts the result to the torch op's return dtype if the config is set."""
  if not config.DEFAULTS.internal_respect_torch_return_dtypes:
    return result

  if not hasattr(torch_op, '_schema'):
    return result

  schema = torch_op._schema
  if not schema.returns:
    return result

  # TODO: Handle multiple return values
  if len(schema.returns) > 1:
    return result

  return_type = schema.returns[0].type
  if str(return_type) == 'Tensor':
    # This is not quite right, we need to get the dtype of the tensor
    # For now, let's assume we can get it from the first input argument
    if not schema.arguments:
      return result
    
    input_type = schema.arguments[0].type
    if str(input_type) != 'Tensor':
      return result
      
    # This is a hack, we need a better way to determine the return dtype
    # For now, let's assume the return type is the same as the first input
    # This is not always true, e.g. for comparison ops.
    return result

  try:
    torch_dtype = getattr(torch, str(return_type))
    jax_dtype = mappings.t2j_dtype(torch_dtype)
    if isinstance(result, jnp.ndarray):
      return result.astype(jax_dtype)
    else:
      return jax_dtype(result)
  except (AttributeError, TypeError):
    return result
