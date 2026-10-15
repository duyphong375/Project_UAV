#!/usr/bin/env python3
"""
KVC UAV Project - Export PyTorch YOLO model (.pt) to ONNX format
Target: Embedded NPU / FPGA GoAI / PC ONNX Runtime

Parameters optimized for hardware synthesis & Gowin GoAI:
- format: onnx
- imgsz: 640 (fixed static 640x640)
- dynamic: False (FPGA requires fixed tensor dimensions [1, 3, 640, 640])
- simplify: True (uses onnxslim to fold constants and remove redundant layers)
- opset: 12 (wide compatibility with embedded NPU compilers)
"""

import sys
import argparse
from pathlib import Path

def export_to_onnx(
    pt_path: str = "ai_training/weights/yolo11n_2class_best.pt",
    imgsz: int = 640,
    opset: int = 12,
    simplify: bool = True
):
    model_path = Path(pt_path)
    if not model_path.exists():
        print(f"Error: Model file '{pt_path}' does not exist.")
        sys.exit(1)

    print(f"[1/3] Loading PyTorch model from: {model_path}")
    from ultralytics import YOLO
    model = YOLO(str(model_path))
    print(f"      Classes: {model.names}")
    print(f"      Task: {model.task}")

    print(f"[2/3] Exporting to ONNX (imgsz={imgsz}, opset={opset}, dynamic=False, simplify={simplify})...")
    exported_path = model.export(
        format="onnx",
        imgsz=imgsz,
        dynamic=False,
        simplify=simplify,
        opset=opset,
    )
    print(f"      Export successful: {exported_path}")

    print("[3/3] Verifying exported ONNX model...")
    import onnx
    import onnxruntime as ort
    import numpy as np

    onnx_model = onnx.load(exported_path)
    onnx.checker.check_model(onnx_model)
    
    inputs = [(i.name, [d.dim_value for d in i.type.tensor_type.shape.dim]) for i in onnx_model.graph.input]
    outputs = [(o.name, [d.dim_value for d in o.type.tensor_type.shape.dim]) for o in onnx_model.graph.output]
    print(f"      Opset: {onnx_model.opset_import[0].version}")
    print(f"      Inputs: {inputs}")
    print(f"      Outputs: {outputs}")

    session = ort.InferenceSession(exported_path)
    dummy_input = np.zeros((1, 3, imgsz, imgsz), dtype=np.float32)
    res = session.run(None, {inputs[0][0]: dummy_input})
    print(f"      ONNXRuntime test inference OK! Output shape: {res[0].shape}")
    print(f"\n[DONE] ONNX model ready for FPGA Gowin GoAI quantization at: {exported_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export YOLO PyTorch model to FPGA-optimized ONNX")
    parser.add_argument("--weights", type=str, default="ai_training/weights/yolo11n_2class_best.pt", help="Path to .pt weights")
    parser.add_argument("--imgsz", type=int, default=640, help="Input image dimension (default: 640)")
    parser.add_argument("--opset", type=int, default=12, help="ONNX opset version (default: 12)")
    args = parser.parse_args()

    export_to_onnx(pt_path=args.weights, imgsz=args.imgsz, opset=args.opset)
