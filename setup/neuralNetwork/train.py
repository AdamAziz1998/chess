import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from tqdm import tqdm
from dataset import ChessMemmapDataset
from model import ChessModel

def train_one_epoch(model, dataloader, criterion, optimizer, device):
    model.train()
    total_loss, total_correct, total_samples = 0, 0, 0
    for x, y in tqdm(dataloader, desc="Training", leave=False):
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        logits = model(x)
        loss = criterion(logits, y)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * x.size(0)
        preds = torch.argmax(logits, dim=1)
        total_correct += (preds == y).sum().item()
        total_samples += x.size(0)
    return total_loss / total_samples, total_correct / total_samples

@torch.no_grad()
def evaluate(model, dataloader, criterion, device):
    model.eval()
    total_loss, total_correct, total_samples = 0, 0, 0
    for x, y in dataloader:
        x, y = x.to(device), y.to(device)
        logits = model(x)
        loss = criterion(logits, y)

        total_loss += loss.item() * x.size(0)
        preds = torch.argmax(logits, dim=1)
        total_correct += (preds == y).sum().item()
        total_samples += x.size(0)
    return total_loss / total_samples, total_correct / total_samples

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--meta", required=True, help="path to meta.json")
    p.add_argument("--epochs", type=int, default=10)
    p.add_argument("--batch_size", type=int, default=256)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--val_split", type=float, default=0.1)
    p.add_argument("--num_workers", type=int, default=2)
    p.add_argument("--out", default="chess_model.pt")
    args = p.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Using device:", device)

    # Load dataset
    print("Loading dataset")
    full_ds = ChessMemmapDataset(args.meta)
    n_total = len(full_ds)
    n_val = int(args.val_split * n_total)
    n_train = n_total - n_val
    train_ds, val_ds = random_split(full_ds, [n_train, n_val])

    train_loader = DataLoader(train_ds, batch_size=args.batch_size,
                              shuffle=True, num_workers=args.num_workers)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size,
                            shuffle=False, num_workers=args.num_workers)

    # Load model
    print("Loading model")
    num_classes = full_ds.meta["num_classes"]
    model = ChessModel(num_classes=num_classes).to(device)

    # Loss + optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)

    # Training loop
    print("Begin model training")
    for epoch in range(1, args.epochs + 1):
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = evaluate(model, val_loader, criterion, device)
        print(f"Epoch {epoch}/{args.epochs} | "
              f"Train loss {train_loss:.4f}, acc {train_acc:.4f} | "
              f"Val loss {val_loss:.4f}, acc {val_acc:.4f}")

    # Save model
    torch.save(model.state_dict(), args.out)
    print("Model saved to", args.out)

if __name__ == "__main__":
    main()
