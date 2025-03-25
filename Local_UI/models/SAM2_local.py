import os
import sys
import numpy as np
import torch
import matplotlib.pyplot as plt
from PIL import Image

# if using Apple MPS, fall back to CPU for unsupported ops
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..',"sam2")))


def select_device():
    """
    Selects the device for computation based on availability of CUDA or MPS.
    """
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    return device


def set_cuda_parameters (device) :
    """
    Set CUDA parameters for the device.
    Args:
        device: The device to set parameters for (CUDA or MPS).
    """
    if device.type == "cuda":
        # use bfloat16 for the entire notebook
        torch.autocast("cuda", dtype=torch.bfloat16).__enter__()
        # turn on tfloat32 for Ampere GPUs (https://pytorch.org/docs/stable/notes/cuda.html#tensorfloat-32-tf32-on-ampere-devices)
        if torch.cuda.get_device_properties(0).major >= 8:
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
    elif device.type == "mps":
        print(
            "\nSupport for MPS devices is preliminary. SAM 2 is trained with CUDA and might \n"
            "give numerically different outputs and sometimes degraded performance on MPS. \n"
            "See e.g. https://github.com/pytorch/pytorch/issues/84936 for a discussion."
        )


def show_mask(mask, ax, obj_id=None, random_color=False):
    if random_color:
        color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
    else:
        cmap = plt.get_cmap("tab10")
        cmap_idx = 0 if obj_id is None else obj_id
        color = np.array([*cmap(cmap_idx)[:3], 0.6])
    h, w = mask.shape[-2:]
    mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    ax.imshow(mask_image)


def show_points(coords, labels, ax, marker_size=200):
    pos_points = coords[labels==1]
    neg_points = coords[labels==0]
    ax.scatter(pos_points[:, 0], pos_points[:, 1], color='green', marker='*', s=marker_size, edgecolor='white', linewidth=1.25)
    ax.scatter(neg_points[:, 0], neg_points[:, 1], color='red', marker='*', s=marker_size, edgecolor='white', linewidth=1.25)


def show_box(box, ax):
    x0, y0 = box[0], box[1]
    w, h = box[2] - box[0], box[3] - box[1]
    ax.add_patch(plt.Rectangle((x0, y0), w, h, edgecolor='green', facecolor=(0, 0, 0, 0), lw=2))


def extract_frames_from_video (video_path, frame_dir):
    """
    Extract frames from a video file and save them as JPEG images.
    
    Args:
        video_path (str): Path to the input video file.
        frame_dir (str): Directory where extracted frames will be saved.
    """
    import cv2
    os.makedirs(frame_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_name = os.path.join(frame_dir, f"{frame_idx}.jpg")
        cv2.imwrite(frame_name, frame)
        frame_idx += 1
    cap.release()
    

def scan_dir_for_frames (frame_dir, interval : int = 1):
    """
    Scan a directory for JPEG frames and return a sorted list of frame names.
    
    Args:
        frame_dir (str): Directory containing JPEG frames.
        interval (int) Defaults to 1 : select every `interval`-th frame.
        
    Returns:
        list: Sorted list of JPEG frame names.
    """
    frame_names = [
        p for p in os.listdir(frame_dir)
        if os.path.splitext(p)[-1] in [".jpg", ".jpeg", ".JPG", ".JPEG"]
    ]
    frame_names.sort(key=lambda p: int(os.path.splitext(p)[0]))
    frame_names = frame_names[::interval]
    return frame_names