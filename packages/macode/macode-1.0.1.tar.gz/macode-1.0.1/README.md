# MaCoDE (accepted to AAAI 2025!)

**MaCoDE** is a novel distributional learning method by redefining the consecutive multi-class classification task of Masked Language Modeling (MLM) as histogram-based non-parametric conditional density estimation. 

> For a detailed method explanations, check our paper! [(link)](https://ojs.aaai.org/index.php/AAAI/article/view/33685)

### 1. Installation
Install using pip:
```
pip install macode
```

### 2. Usage
```python
from macode import macode
macode.MaCoDE # MaCoDE model
```
- See [example.ipynb](example.ipynb) for detailed example and its results with `whitewine` dataset.
  - Link for download `whitewine` dataset: [https://archive.ics.uci.edu/dataset/186/wine+quality](https://archive.ics.uci.edu/dataset/186/wine+quality)

#### Example
```python
import warnings
warnings.filterwarnings('ignore')

"""device setting"""
import torch
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
device

"""load dataset and specify column types"""
import pandas as pd
data = pd.read_csv('./whitewine.csv', delimiter=";")
columns = list(data.columns)
columns.remove("quality")
assert data.isna().sum().sum() == 0
continuous_features = columns
categorical_features = ["quality"]
integer_features = []

### the target column should be the last column
data = data[continuous_features + categorical_features] 
# len(data)

"""training, test, synthetic datasets"""
data[categorical_features] = data[categorical_features].apply(
    lambda col: col.astype('category').cat.codes + 1) # pre-processing

train = data.iloc[:4000]
test = data.iloc[4000:]
train = train.reset_index(drop=True)
test = test.reset_index(drop=True)

"""MaCoDE"""
from macode import macode

macode = macode.MaCoDE(
    data=train, # the observed tabular dataset
    continuous_features=continuous_features, # the list of continuous columns of data
    categorical_features=categorical_features, # the list of categorical columns of data
    integer_features=integer_features, # the list of integer-type columns of data
    
    seed=42, # seed for repeatable results
    bins=10, # the number of bins for discretization
    dim_transformer=512, # the embedding size (input dimension size of transformer)
    num_transformer_heads=8, # the number of heads in transformer
    num_transformer_layer=1, # the number of layers in transformer
    
    epochs=10, # the number of epochs (for quick checking)
    batch_size=1024, # the batch size
    lr=0.001, # learning rate
    device=device,
)

"""training"""
macode.train()

"""generate synthetic data"""
syndata = macode.generate_data(n=len(train), tau=1.)
syndata

"""Evaluate Synthetic Data Quality"""
from synthetic_eval import evaluation

target = "quality"
results = evaluation.evaluate(
    syndata, train, test, 
    target, continuous_features, categorical_features, device
)

"""print results"""
for x, y in results._asdict().items():
    print(f"{x}: {y:.3f}")
```
- See [example_missing.ipynb](example_missing.ipynb) for detailed example for missing data imputation.
- For synthetic data quality evaluation (`synthetic_eval`), please refer to [https://pypi.org/project/synthetic-eval](https://pypi.org/project/synthetic-eval).

### 3. Citation
If you use this code or package, please cite our associated paper: (The final camera-ready version manuscript will be available soon.)
```bibtex
@inproceedings{an2025masked,
  title={Masked Language Modeling Becomes Conditional Density Estimation for Tabular Data Synthesis},
  author={An, Seunghwan and Woo, Gyeongdong and Lim, Jaesung and Kim, ChangHyun and Hong, Sungchul and Jeon, Jong-June},
  booktitle={Proceedings of the AAAI Conference on Artificial Intelligence},
  volume={39},
  number={15},
  pages={15356--15364},
  year={2025}
}
```
