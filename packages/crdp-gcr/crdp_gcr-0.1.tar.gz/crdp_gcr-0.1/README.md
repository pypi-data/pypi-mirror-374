# crdp-gcr

Cython implementation of Ramer-Douglas-Peucker algorithm, identical to [crdp](https://pypi.org/project/crdp/0.0.2/) but modified to run as a google cloud function.

## Usage
```
pip instal crdp-gcr
```

```python
In [1]: from crdp import rdp

In [2]: rdp([[1,1],[2,3],[3,3],[4,4]], 0.8)
Out[2]: [[1, 1], [4, 4]]

In [3]: rdp([[1,1],[2,3],[3,3],[4,4]], 0.7)
Out[3]: [[1, 1], [2, 3], [4, 4]]
```

All credit to [Bi Ran](https://github.com/biran0079), author of the original code