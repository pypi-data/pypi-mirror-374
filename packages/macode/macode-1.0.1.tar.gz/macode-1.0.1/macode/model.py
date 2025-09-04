#%%
from collections import namedtuple

import torch
import torch.nn as nn


#%% 
class Embedding(nn.Module):
    def __init__(
        self, 
        EncodedInfo: namedtuple,  # information of the dataset
        bins: int = 10,  # the number of bins for discretization
        dim_transformer: int = 512,  # the embedding size (input dimension size of transformer)
        device="cpu",
    ):
        super().__init__()
        self.EncodedInfo = EncodedInfo
        self.device = device

        self.ContEmbed = nn.ModuleList()
        for _ in range(EncodedInfo.num_continuous_features):
            self.ContEmbed.append(
                nn.Embedding(
                    bins + 1, dim_transformer
                ).to(device) # including [MASK] token
            )

        self.DiscEmbed = nn.ModuleList()
        for num_category in EncodedInfo.num_categories:
            self.DiscEmbed.append(
                nn.Embedding(
                    num_category + 1, dim_transformer
                ).to(device) # including [MASK] token
            )

        self.init_weights()
        
    def init_weights(self):
        for layer in self.ContEmbed:
            nn.init.kaiming_uniform_(layer.weight) 
        for layer in self.DiscEmbed:
            nn.init.kaiming_uniform_(layer.weight) 


    def forward(self, batch):
        # continuous
        continuous = batch[:, :self.EncodedInfo.num_continuous_features].long()
        continuous_embedded = torch.stack(
            [self.ContEmbed[i](continuous[:, i]) for i in range(continuous.size(1))]
        ).transpose(0, 1) # [batch, num_continuous, dim_transformer]
        
        # discrete
        categorical = batch[:, self.EncodedInfo.num_continuous_features:].long()
        categorical_embedded = torch.stack(
            [self.DiscEmbed[i](categorical[:, i]) for i in range(categorical.size(1))]
        ).transpose(0, 1) # [batch, num_categories, dim_transformer]

        # [batch, num_continuous_features + len(num_categories), dim_transformer]
        embedded = torch.cat([continuous_embedded, categorical_embedded], dim=1)
        return embedded
    
    
#%%
class OutLinearLayer(nn.Module):
    def __init__(
        self, 
        EncodedInfo: namedtuple,  # information of the dataset
        bins: int = 10,  # the number of bins for discretization
        dim_transformer: int = 512,  # the embedding size (input dimension size of transformer)
        device="cpu",
    ):
        super().__init__()
        
        self.outlinear = nn.ModuleList()
        for _ in range(EncodedInfo.num_continuous_features):
            self.outlinear.append(
                nn.Linear(
                    dim_transformer, bins
                ).to(device)
            )
        for num_category in EncodedInfo.num_categories:
            self.outlinear.append(
                nn.Linear(
                    dim_transformer, num_category
                ).to(device)
            )

        self.init_weights()

    def init_weights(self):
        for layer in self.outlinear:
            nn.init.kaiming_uniform_(layer.weight) 
    
    def forward(self, x):
        return [
            self.outlinear[i](x[:, i, :]) for i in range(len(self.outlinear))
        ] 
    
    
#%%
class Model(nn.Module):
    def __init__(
        self,
        EncodedInfo: namedtuple,  # information of the dataset
        bins: int = 10,  # the number of bins for discretization
        dim_transformer: int = 512,  # the embedding size (input dimension size of transformer)
        num_transformer_heads: int = 8,  # the number of heads in transformer
        num_transformer_layer: int = 1,  # the number of layers in transformer
        device="cpu",
    ):
        super().__init__()
        self.EncodedInfo = EncodedInfo
        self.device = device
        
        self.embedding = Embedding(
            EncodedInfo, bins, dim_transformer, device).to(device)

        transformer_layer = nn.TransformerEncoderLayer(
            d_model=dim_transformer, 
            nhead=num_transformer_heads, 
            dropout=0., # fixed value
            activation='gelu',
            batch_first=True).to(device)
        self.transformer = nn.TransformerEncoder(
            transformer_layer, num_transformer_layer)
        
        self.dynamic_linear = OutLinearLayer(
            EncodedInfo, bins, dim_transformer, device)

    def forward(self, batch):
        x = self.embedding(batch)
        x = self.transformer(x)
        pred = self.dynamic_linear(x)
        return pred

    
#%%