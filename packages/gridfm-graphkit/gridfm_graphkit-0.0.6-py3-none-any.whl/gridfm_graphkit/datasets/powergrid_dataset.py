from gridfm_graphkit.datasets.normalizers import Normalizer, BaseMVANormalizer
from gridfm_graphkit.datasets.transforms import (
    AddEdgeWeights,
    AddNormalizedRandomWalkPE,
)

import os.path as osp
import os
import torch
from torch_geometric.data import Data, Dataset
import pandas as pd
from tqdm import tqdm
from typing import Optional, Callable


class GridDatasetDisk(Dataset):
    """
    A PyTorch Geometric `Dataset` for power grid data stored on disk.
    This dataset reads node and edge CSV files, applies normalization,
    and saves each graph separately on disk as a processed file.
    Data is loaded from disk lazily on demand.

    Args:
        root (str): Root directory where the dataset is stored.
        norm_method (str): Identifier for normalization method (e.g., "minmax", "standard").
        node_normalizer (Normalizer): Normalizer used for node features.
        edge_normalizer (Normalizer): Normalizer used for edge features.
        pe_dim (int): Length of the random walk used for positional encoding.
        mask_dim (int, optional): Number of features per-node that could be masked.
        transform (callable, optional): Transformation applied at runtime.
        pre_transform (callable, optional): Transformation applied before saving to disk.
        pre_filter (callable, optional): Filter to determine which graphs to keep.
    """

    def __init__(
        self,
        root: str,
        norm_method: str,
        node_normalizer: Normalizer,
        edge_normalizer: Normalizer,
        pe_dim: int,
        mask_dim: int = 6,
        transform: Optional[Callable] = None,
        pre_transform: Optional[Callable] = None,
        pre_filter: Optional[Callable] = None,
    ):
        self.norm_method = norm_method
        self.node_normalizer = node_normalizer
        self.edge_normalizer = edge_normalizer
        self.pe_dim = pe_dim
        self.mask_dim = mask_dim
        self.length = None

        super().__init__(root, transform, pre_transform, pre_filter)

        # Load normalization stats if available
        node_stats_path = osp.join(
            self.processed_dir,
            f"node_stats_{self.norm_method}.pt",
        )
        edge_stats_path = osp.join(
            self.processed_dir,
            f"edge_stats_{self.norm_method}.pt",
        )
        if osp.exists(node_stats_path) and osp.exists(edge_stats_path):
            self.node_stats = torch.load(node_stats_path, weights_only=False)
            self.edge_stats = torch.load(edge_stats_path, weights_only=False)
            self.node_normalizer.fit_from_dict(self.node_stats)
            self.edge_normalizer.fit_from_dict(self.edge_stats)

    @property
    def raw_file_names(self):
        return ["pf_node.csv", "pf_edge.csv"]

    @property
    def processed_done_file(self):
        return f"processed_{self.norm_method}_{self.mask_dim}_{self.pe_dim}.done"

    @property
    def processed_file_names(self):
        return [self.processed_done_file]

    def download(self):
        pass

    def process(self):
        node_df = pd.read_csv(osp.join(self.raw_dir, "pf_node.csv"))
        edge_df = pd.read_csv(osp.join(self.raw_dir, "pf_edge.csv"))

        # Check the unique scenarios available
        scenarios = node_df["scenario"].unique()
        # Ensure node and edge data match
        if not (scenarios == edge_df["scenario"].unique()).all():
            raise ValueError("Mismatch between node and edge scenario values.")

        # normalize node attributes
        cols_to_normalize = ["Pd", "Qd", "Pg", "Qg", "Vm", "Va"]
        to_normalize = torch.tensor(
            node_df[cols_to_normalize].values,
            dtype=torch.float,
        )
        self.node_stats = self.node_normalizer.fit(to_normalize)
        node_df[cols_to_normalize] = self.node_normalizer.transform(
            to_normalize,
        ).numpy()

        # normalize edge attributes
        cols_to_normalize = ["G", "B"]
        to_normalize = torch.tensor(
            edge_df[cols_to_normalize].values,
            dtype=torch.float,
        )
        if isinstance(self.node_normalizer, BaseMVANormalizer):
            self.edge_stats = self.edge_normalizer.fit(
                to_normalize,
                self.node_normalizer.baseMVA,
            )
        else:
            self.edge_stats = self.edge_normalizer.fit(to_normalize)
        edge_df[cols_to_normalize] = self.edge_normalizer.transform(
            to_normalize,
        ).numpy()

        # save stats
        node_stats_path = osp.join(
            self.processed_dir,
            f"node_stats_{self.norm_method}.pt",
        )
        edge_stats_path = osp.join(
            self.processed_dir,
            f"edge_stats_{self.norm_method}.pt",
        )
        torch.save(self.node_stats, node_stats_path)
        torch.save(self.edge_stats, edge_stats_path)

        # Create groupby objects for scenarios
        node_groups = node_df.groupby("scenario")
        edge_groups = edge_df.groupby("scenario")

        for scenario_idx in tqdm(scenarios):
            # NODE DATA
            node_data = node_groups.get_group(scenario_idx)
            x = torch.tensor(
                node_data[
                    ["Pd", "Qd", "Pg", "Qg", "Vm", "Va", "PQ", "PV", "REF"]
                ].values,
                dtype=torch.float,
            )
            y = x[:, : self.mask_dim]

            # EDGE DATA
            edge_data = edge_groups.get_group(scenario_idx)
            edge_attr = torch.tensor(edge_data[["G", "B"]].values, dtype=torch.float)
            edge_index = torch.tensor(
                edge_data[["index1", "index2"]].values.T,
                dtype=torch.long,
            )

            # Create the Data object
            graph_data = Data(
                x=x,
                edge_index=edge_index,
                edge_attr=edge_attr,
                y=y,
                scenario_id=scenario_idx,
            )
            pe_pre_transform = AddEdgeWeights()
            graph_data = pe_pre_transform(graph_data)
            pe_transform = AddNormalizedRandomWalkPE(
                walk_length=self.pe_dim,
                attr_name="pe",
            )
            graph_data = pe_transform(graph_data)
            torch.save(
                graph_data,
                osp.join(
                    self.processed_dir,
                    f"data_{self.norm_method}_{self.mask_dim}_{self.pe_dim}_index_{scenario_idx}.pt",
                ),
            )
        with open(osp.join(self.processed_dir, self.processed_done_file), "w") as f:
            f.write("done")

    def len(self):
        if self.length is None:
            files = [
                f
                for f in os.listdir(self.processed_dir)
                if f.startswith(
                    f"data_{self.norm_method}_{self.mask_dim}_{self.pe_dim}_index_",
                )
                and f.endswith(".pt")
            ]
            self.length = len(files)
        return self.length

    def get(self, idx):
        file_name = osp.join(
            self.processed_dir,
            f"data_{self.norm_method}_{self.mask_dim}_{self.pe_dim}_index_{idx}.pt",
        )
        if not osp.exists(file_name):
            raise IndexError(f"Data file {file_name} does not exist.")
        data = torch.load(file_name, weights_only=False)
        if self.transform:
            data = self.transform(data)
        return data

    def change_transform(self, new_transform):
        """
        Temporarily switch to a new transform function, used when evaluating different tasks.

        Args:
            new_transform (Callable): The new transform to use.
        """
        self.original_transform = self.transform
        self.transform = new_transform

    def reset_transform(self):
        """
        Reverts the transform to the original one set during initialization, usually called after the evaluation step.
        """
        if self.original_transform is None:
            raise ValueError(
                "The original transform is None or the function change_transform needs to be called before",
            )
        self.transform = self.original_transform
