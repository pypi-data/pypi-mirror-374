# NetworkX Arxiv Generators [![CI](https://github.com/YanYablonovskiy/networkx-arxiv-generators/actions/workflows/ci.yml/badge.svg)](https://github.com/YanYablonovskiy/networkx-arxiv-generators/actions/workflows/ci.yml)

Advanced graph generation models for [NetworkX](https://github.com/networkx/networkx), implementing algorithms from mathematical literature (with arxiv citations), and published
in reputable peer-reviewed journals, or presented at established conferences, symposiums and seminars.

## Current state  

Currently the project is in a scaffolding state, with the first goal of generating uniform power law graphs as in [Uniform generation of random graphs with power-law degree sequences](https://arxiv.org/abs/1709.02674). These results were presented at
[SODA '18: Proceedings of the Twenty-Ninth Annual ACM-SIAM Symposium on Discrete Algorithms](https://dl.acm.org/doi/10.5555/3174304.3175419) .

To begin, this requires results from the seminal paper B.D. McKay and N.C. Wormald, Uniform generation of random regular graphs of moderate degree, 
J. Algorithms 11 (1990), 52–67.

Currently in progress, located in `src/nx_arxivgen/generators/mckay_wormald.py` .

## Install
Once published:
```bash
pip install networkx-arxiv-generators
```

## Quickstart

```python
import networkx as nx
import matplotlib.pyplot as plt
from nx_arxivgen.generators.mckay_wormald import mckay_wormald_simple_graph, mckay_random_graph_encoding

test_deg_seq = [1, 1, 2, 3, 3, 2, 6, 6,7,8,6,1,2,3,4,5,6,7,8,9,10]

test = mckay_wormald_simple_graph(test_deg_seq, debug=True)
nx.draw_spring(test, with_labels=True)
plt.show()

sample_graph = nx.generators.binomial_graph(20, 0.5)

print(mckay_random_graph_encoding(sample_graph))
```
An example of a graph generated this way, with the degree sequence 
```
[10, 1, 0, 4, 3, 3, 2, 1, 10, 8, 1, 9, 6, 0, 0, 1, 3, 3, 8, 9, 0, 8, 3, 10, 8, 6, 3, 7, 9, 4]
```
The nodes of degree 0 are 2, 13, 14 and 20.
<img width="593" height="449" alt="image" src="https://github.com/user-attachments/assets/20cdd3ef-0153-40d6-9a15-fc186e7eb8c6" /> 

## Goals

- Faithful implementations of arxiv models with clear citations, existing in reputable publications.
- Deterministic seeding and reproducibility, wherever relevant by the context of the research paper.
- Tests, docs, and examples for each model.

## Citing

If you use this package, please cite it. See `CITATION.cff`. Each model’s docstring cites its originating paper(s).
