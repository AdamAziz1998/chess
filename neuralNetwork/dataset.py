import json
import numpy as np
import torch
from torch.utils.data import Dataset

class ChessMemmapDataset(Dataset):
    def __init__(self, meta_path):
        with open(meta_path, 'r') as f:
            meta = json.load(f)
        self.meta = meta
        self.x_path = meta['x_path']
        self.y_path = meta['y_path']
        self.shape_x = tuple(meta['shape_x'])
        self.shape_y = tuple(meta['shape_y'])
        self.dtype_x = np.uint8 if meta['dtype_x'] == 'uint8' else np.float32
        self.dtype_y = np.int32 if meta['dtype_y'] == 'int32' else np.int64
        self._X = None
        self._y = None

    def _ensure_open(self):
        # open memmap lazily (important for multi-worker DataLoader)
        if self._X is None:
            self._X = np.memmap(self.x_path, dtype=self.dtype_x, mode='r', shape=self.shape_x)
            self._y = np.memmap(self.y_path, dtype=self.dtype_y, mode='r', shape=self.shape_y)

    def __len__(self):
        return self.shape_x[0]

    def __getitem__(self, idx):
        self._ensure_open()
        # convert to float32 for model
        x = torch.tensor(self._X[idx].astype(np.float32), dtype=torch.float32)
        y = torch.tensor(int(self._y[idx]), dtype=torch.long)
        return x, y