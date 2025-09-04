<div align="center">

# JVP Flash Attention

<a href="https://pytorch.org/get-started/locally/"><img alt="PyTorch" src="https://img.shields.io/badge/PyTorch-ee4c2c?logo=pytorch&logoColor=white"></a>

</div>


## Description

Flash Attention Triton kernel with support for second-order derivatives, such as Jacobian-Vector Products (JVPs) and Hessian-Vector Products (HVPs)

## Installation

Using `pip`, one can install `jvp_flash_attention` as follows.

```bash
# Install package
pip install jvp_flash_attention

# [OPTIONAL, for development] Install package and pre-commit hooks
pip install -e .
pre-commit install
```

## Usage

Once installed, one can use `jvp_flash_attention` in place of PyTorch's `scaled_dot_product_attention` as follows.

```python
import torch.nn.functional as F

from torch.nn.attention import SDPBackend, sdpa_kernel
from jvp_flash_attention.jvp_attention import attention as jvp_attention

with sdpa_kernel(SDPBackend.MATH):
  # Regular attention
  # x = F.scaled_dot_product_attention(
  #     q,
  #     k,
  #     v,
  #     attn_mask=attn_mask,
  #     dropout_p=attn_dropout_p if self.training else 0.0,
  # )

  # Flash attention
  x = jvp_attention(
      q,
      k,
      v,
      # attn_mask=attn_mask,  # NOTE: Attention masking is not yet supported
  )
```

Contributions or enhancements are welcome!

## Tests

If you want to run the unit tests verifying the correctness of the JVP Flash Attention Triton kernel, run the following command(s).

```bash
python tests/test_jvp_attention.py --dtype {float16,bfloat16,float32}
```

In principle, the kernel should support ROCm systems as well, though it has not yet been tested on them. macOS is currently unsupported.

Results for `float16`:
```
==========================================================================================
BENCHMARK SUMMARY
==========================================================================================
Seq Len    Causal   Method     Time (ms)    Mem (MB)     TFLOP/s      Max Error    Grad Check
------------------------------------------------------------------------------------------
32         False    sdpa       0.551        0.64           0.0 TFLOP/s baseline     N/A       
32         False    jvp_attn   0.483        0.22           0.0 TFLOP/s 1.95e-03     ✓         

32         True     sdpa       1.067        0.65           0.0 TFLOP/s baseline     N/A       
32         True     jvp_attn   0.465        0.22           0.0 TFLOP/s 1.95e-03     ✓         

64         False    sdpa       0.552        1.41           0.0 TFLOP/s baseline     N/A       
64         False    jvp_attn   0.469        0.43           0.0 TFLOP/s 9.77e-04     ✓         

64         True     sdpa       0.875        1.42           0.0 TFLOP/s baseline     N/A       
64         True     jvp_attn   0.469        0.43           0.0 TFLOP/s 1.95e-03     ✓         

128        False    sdpa       0.533        3.28           0.0 TFLOP/s baseline     N/A       
128        False    jvp_attn   0.467        0.86           0.1 TFLOP/s 9.77e-04     ✓         

128        True     sdpa       0.860        3.35           0.0 TFLOP/s baseline     N/A       
128        True     jvp_attn   0.494        0.86           0.0 TFLOP/s 1.95e-03     ✓         

256        False    sdpa       0.538        9.69           0.2 TFLOP/s baseline     N/A       
256        False    jvp_attn   0.473        1.72           0.4 TFLOP/s 9.77e-04     ✓         

256        True     sdpa       0.870        9.94           0.0 TFLOP/s baseline     N/A       
256        True     jvp_attn   0.468        1.72           0.2 TFLOP/s 1.95e-03     ✓         

512        False    sdpa       0.575        31.88          0.6 TFLOP/s baseline     N/A       
512        False    jvp_attn   0.466        3.45           1.5 TFLOP/s 4.88e-04     ✓         

512        True     sdpa       0.914        32.88          0.2 TFLOP/s baseline     N/A       
512        True     jvp_attn   0.467        3.45           0.7 TFLOP/s 1.95e-03     ✓         

1024       False    sdpa       1.291        113.77         1.1 TFLOP/s baseline     N/A       
1024       False    jvp_attn   0.463        6.89           5.9 TFLOP/s 4.88e-04     ✓         

1024       True     sdpa       1.467        117.77         0.5 TFLOP/s baseline     N/A       
1024       True     jvp_attn   0.470        6.89           2.9 TFLOP/s 1.95e-03     ✓         

2048       False    sdpa       3.669        427.54         1.5 TFLOP/s baseline     N/A       
2048       False    jvp_attn   0.462        13.79         23.7 TFLOP/s 2.44e-04     ✓         

2048       True     sdpa       4.287        443.54         0.6 TFLOP/s baseline     N/A       
2048       True     jvp_attn   0.463        13.79         11.8 TFLOP/s 1.95e-03     ✓   
```

Results for `bfloat16`:
```
==========================================================================================
BENCHMARK SUMMARY
==========================================================================================
Seq Len    Causal   Method     Time (ms)    Mem (MB)     TFLOP/s      Max Error    Grad Check
------------------------------------------------------------------------------------------
32         False    sdpa       0.527        0.64           0.0 TFLOP/s baseline     N/A       
32         False    jvp_attn   0.461        0.22           0.0 TFLOP/s 1.56e-02     ✓         

32         True     sdpa       0.854        0.65           0.0 TFLOP/s baseline     N/A       
32         True     jvp_attn   0.462        0.22           0.0 TFLOP/s 1.56e-02     ✓         

64         False    sdpa       0.671        1.41           0.0 TFLOP/s baseline     N/A       
64         False    jvp_attn   0.459        0.43           0.0 TFLOP/s 7.81e-03     ✓         

64         True     sdpa       0.846        1.42           0.0 TFLOP/s baseline     N/A       
64         True     jvp_attn   0.459        0.43           0.0 TFLOP/s 1.56e-02     ✓         

128        False    sdpa       0.539        3.28           0.0 TFLOP/s baseline     N/A       
128        False    jvp_attn   0.463        0.86           0.1 TFLOP/s 7.81e-03     ✓         

128        True     sdpa       0.860        3.35           0.0 TFLOP/s baseline     N/A       
128        True     jvp_attn   0.484        0.86           0.0 TFLOP/s 1.56e-02     ✓         

256        False    sdpa       0.530        9.69           0.2 TFLOP/s baseline     N/A       
256        False    jvp_attn   0.468        1.72           0.4 TFLOP/s 3.91e-03     ✓         

256        True     sdpa       0.856        9.94           0.0 TFLOP/s baseline     N/A       
256        True     jvp_attn   0.468        1.72           0.2 TFLOP/s 1.56e-02     ✓         

512        False    sdpa       0.573        31.88          0.6 TFLOP/s baseline     N/A       
512        False    jvp_attn   0.469        3.45           1.5 TFLOP/s 3.91e-03     ✓         

512        True     sdpa       0.869        32.88          0.2 TFLOP/s baseline     N/A       
512        True     jvp_attn   0.468        3.45           0.7 TFLOP/s 1.56e-02     ✓         

1024       False    sdpa       1.290        113.77         1.1 TFLOP/s baseline     N/A       
1024       False    jvp_attn   0.462        6.89           5.9 TFLOP/s 3.91e-03     ✓         

1024       True     sdpa       1.466        117.77         0.5 TFLOP/s baseline     N/A       
1024       True     jvp_attn   0.461        6.89           3.0 TFLOP/s 1.56e-02     ✓         

2048       False    sdpa       3.673        427.54         1.5 TFLOP/s baseline     N/A       
2048       False    jvp_attn   0.462        13.79         23.7 TFLOP/s 1.95e-03     ✓         

2048       True     sdpa       4.286        443.54         0.6 TFLOP/s baseline     N/A       
2048       True     jvp_attn   0.452        13.79         12.1 TFLOP/s 3.12e-02     ✓   
```

Results for `float32`:
```
==========================================================================================
BENCHMARK SUMMARY
==========================================================================================
Seq Len    Causal   Method     Time (ms)    Mem (MB)     TFLOP/s      Max Error    Grad Check
------------------------------------------------------------------------------------------
32         False    sdpa       0.456        0.51           0.0 TFLOP/s baseline     N/A       
32         False    jvp_attn   0.454        0.43           0.0 TFLOP/s 7.22e-03     ✓         

32         True     sdpa       0.779        0.51           0.0 TFLOP/s baseline     N/A       
32         True     jvp_attn   0.458        0.43           0.0 TFLOP/s 6.18e-03     ✓         

64         False    sdpa       0.460        1.09           0.0 TFLOP/s baseline     N/A       
64         False    jvp_attn   0.462        0.86           0.0 TFLOP/s 7.03e-03     ✓         

64         True     sdpa       0.787        1.11           0.0 TFLOP/s baseline     N/A       
64         True     jvp_attn   0.462        0.86           0.0 TFLOP/s 6.18e-03     ✓         

128        False    sdpa       0.460        2.81           0.0 TFLOP/s baseline     N/A       
128        False    jvp_attn   0.461        1.72           0.1 TFLOP/s 5.07e-03     ✓         

128        True     sdpa       0.782        2.88           0.0 TFLOP/s baseline     N/A       
128        True     jvp_attn   0.472        1.72           0.0 TFLOP/s 6.18e-03     ✓         

256        False    sdpa       0.457        8.75           0.2 TFLOP/s baseline     N/A       
256        False    jvp_attn   0.465        3.44           0.4 TFLOP/s 3.67e-03     ✓         

256        True     sdpa       0.798        9.00           0.1 TFLOP/s baseline     N/A       
256        True     jvp_attn   0.465        3.44           0.2 TFLOP/s 5.78e-03     ✓         

512        False    sdpa       0.530        30.01          0.6 TFLOP/s baseline     N/A       
512        False    jvp_attn   0.469        6.88           1.5 TFLOP/s 2.88e-03     ✓         

512        True     sdpa       0.784        31.01          0.2 TFLOP/s baseline     N/A       
512        True     jvp_attn   0.460        6.88           0.7 TFLOP/s 5.13e-03     ✓         

1024       False    sdpa       1.207        110.02         1.1 TFLOP/s baseline     N/A       
1024       False    jvp_attn   0.467        13.77          5.9 TFLOP/s 2.61e-03     ✓         

1024       True     sdpa       1.379        115.02         0.5 TFLOP/s baseline     N/A       
1024       True     jvp_attn   0.465        13.77          2.9 TFLOP/s 5.61e-03     ✓         

2048       False    sdpa       3.435        420.04         1.6 TFLOP/s baseline     N/A       
2048       False    jvp_attn   0.496        27.54         22.1 TFLOP/s 1.56e-03     ✓         

2048       True     sdpa       4.051        436.04         0.7 TFLOP/s baseline     N/A       
2048       True     jvp_attn   0.486        27.54         11.3 TFLOP/s 6.47e-03     ✓   
```

## License

This project is covered under the **MIT License**.

## Citing this work

If you use the code associated with this package or otherwise find this work useful, please use GitHub's `Cite this repository` feature or the BibTeX below.

```bibtex
@software{Morehead_JVP_Flash_Attention_2025,
  author = {Morehead, Alex},
  doi = {10.5281/zenodo.17050188},
  license = {MIT},
  month = sep,
  title = {{JVP Flash Attention}},
  url = {https://github.com/amorehead/jvp_flash_attention},
  version = {0.0.1},
  year = {2025}
}
```

## Acknowledgements

`jvp_flash_attention` builds upon the contributions and insights from the following sources:

- [flash-attention](https://github.com/Dao-AILab/flash-attention)
  - [JVP Triton kernel thread](https://github.com/Dao-AILab/flash-attention/issues/1672)
    - [benjamin-dinkelmann](https://gist.github.com/benjamin-dinkelmann)
    - *[Birch-san](https://github.com/Birch-san)*
    - [dabeschte](https://github.com/dabeschte)
    - [IsaacYQH](https://gist.github.com/IsaacYQH)
    - [KohakuBlueleaf](https://github.com/KohakuBlueleaf)
    - [leon](https://github.com/leon532)
    - [limsanky](https://github.com/limsanky)
    - [lucidrains](https://github.com/lucidrains)
    - [Peterande](https://gist.github.com/Peterande)
    - *[Ryu1845](https://github.com/Ryu1845)*
    - [tridao](https://github.com/tridao)

We thank each and every contributor!
