import os
import argparse
from pathlib import Path
from ultralytics import YOLO
import torch

def train_yolo(dataset_type, epochs=200, imgsz=416, batch=2, device=None):
    # Setup paths
    project_root = Path(__file__).resolve().parent.parent
    notebooks_dir = project_root / "notebooks"
    
    if dataset_type == "roboflow":
        data_yaml = notebooks_dir / "dataset" / "roboflow" / "data.yaml"
        name = "mvp_roboflow"
    elif dataset_type == "kaggle":
        data_yaml = notebooks_dir / "dataset" / "kaggle" / "data.yaml"
        name = "mvp_kaggle"
    else:
        raise ValueError("Invalid dataset type. Choose 'roboflow' or 'kaggle'.")

    if not data_yaml.exists():
        print(f"Error: data.yaml not found at {data_yaml}")
        return

    # Device detection
    if device is None:
        device = '0' if torch.cuda.is_available() else 'cpu'
    
    print(f"Using device: {device}")
    print(f"Training on dataset: {dataset_type}")
    print(f"Config: {data_yaml}")

    # Load model
    model_path = notebooks_dir / "models" / "yolo11n.pt"
    if not model_path.parent.exists():
        model_path.parent.mkdir(parents=True)
    
    model = YOLO(model_path if model_path.exists() else "yolo11n.pt")

    # Start training
    results = model.train(
        data=str(data_yaml),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        name=name,
        device=device,
        project=str(notebooks_dir / "outputs"),
        exist_ok=True
    )
    
    print(f"Training completed. Results saved in {notebooks_dir / 'outputs' / name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train YOLOv11 outside of Jupyter Notebook.")
    parser.add_argument("--dataset", type=str, default="roboflow", choices=["roboflow", "kaggle"], help="Dataset to use")
    parser.add_argument("--epochs", type=int, default=200, help="Number of epochs")
    parser.add_argument("--imgsz", type=int, default=416, help="Image size")
    parser.add_argument("--batch", type=int, default=2, help="Batch size")
    parser.add_argument("--device", type=str, default=None, help="Device (cpu or 0)")

    args = parser.parse_args()
    
    train_yolo(
        dataset_type=args.dataset,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device
    )
