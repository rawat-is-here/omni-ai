"""
Evaluate the OmniAI model accuracy.
"""

import torch
from torch.utils.data import DataLoader
from ai.datasets import OmniDataset
from ai.model import OmniModel
import os

def evaluate(model_path="models/omni_model.pt", dataset_path="models/train.pkl"):
    print(f"--- Evaluating {model_path} on {dataset_path} ---")
    
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}")
        return
        
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}")
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Load Model
    model = OmniModel().to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()

    # Load Dataset (no augmentation during evaluation so we test the exact data)
    dataset = OmniDataset(dataset_path, augment=False)
    loader = DataLoader(dataset, batch_size=64, shuffle=False)

    total_samples = 0
    correct_root = 0
    correct_quality = 0
    correct_exact = 0

    print(f"Total samples to evaluate: {len(dataset)}")
    print("Evaluating... (this might take a few minutes on a CPU)")
    
    with torch.no_grad():
        for batch_idx, batch in enumerate(loader):
            
            if batch_idx % 100 == 0 and batch_idx > 0:
                print(f"Processed {batch_idx * 64} / {len(dataset)} samples...")

            melody = batch["melody"].to(device)
            mask = batch["mask"].to(device)
            
            true_root = batch["root"].to(device)
            true_quality = batch["quality"].to(device)

            # Forward pass
            output = model(melody, mask)
            
            # Get predictions (the index with the highest probability)
            pred_root = torch.argmax(output["root"], dim=1)
            pred_quality = torch.argmax(output["quality"], dim=1)

            # Compare predictions to ground truth
            batch_size = melody.size(0)
            total_samples += batch_size

            # Count correct roots
            root_matches = (pred_root == true_root)
            correct_root += root_matches.sum().item()

            # Count correct qualities
            quality_matches = (pred_quality == true_quality)
            correct_quality += quality_matches.sum().item()

            # Count exact matches (both root AND quality are correct)
            exact_matches = (root_matches & quality_matches)
            correct_exact += exact_matches.sum().item()

    # Calculate percentages
    root_acc = (correct_root / total_samples) * 100
    quality_acc = (correct_quality / total_samples) * 100
    exact_acc = (correct_exact / total_samples) * 100

    print("\n=== RESULTS ===")
    print(f"Root Accuracy:    {root_acc:.2f}% (Predicted the right chord letter)")
    print(f"Quality Accuracy: {quality_acc:.2f}% (Predicted Major/Minor/etc. correctly)")
    print(f"Exact Accuracy:   {exact_acc:.2f}% (Predicted BOTH correctly)")
    print("===============\n")

if __name__ == "__main__":
    # Evaluate on the original dataset
    evaluate(dataset_path="models/train.pkl")
    
    # Evaluate on the Bollywood dataset
    if os.path.exists("models/bollywood_train.pkl"):
        evaluate(dataset_path="models/bollywood_train.pkl")
