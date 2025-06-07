import cv2
import numpy as np
import pandas as pd
from skimage.morphology import skeletonize
from skimage.filters import threshold_otsu
from skimage import img_as_ubyte
from skimage.transform import probabilistic_hough_line
import matplotlib.pyplot as plt
import math

# ── UPDATE these two lines to match your filenames ──
TREE_FNAME  = "data/tree_full.png"
SCALE_FNAME = "data/scale_full.png"
# ──────────────────────────────────────────────────

# 1) Load and threshold the scale bar to find the 0 Ma & 2000 Ma ticks
scale_img = cv2.imread(SCALE_FNAME)
if scale_img is None:
    raise FileNotFoundError(f"Could not open '{SCALE_FNAME}'.")
gray_scale = cv2.cvtColor(scale_img, cv2.COLOR_BGR2GRAY)
thresh_val = threshold_otsu(gray_scale)
binary_scale = (gray_scale < thresh_val).astype(np.uint8) * 255

# Connected components → isolate vertical tick marks (0 Ma and 2000 Ma)
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_scale, connectivity=8)
tick_positions = []
for i in range(1, num_labels):
    x, y, w, h, area = stats[i]
    if h > 10 and (h / float(w)) > 5:
        tick_positions.append(centroids[i][0])

if len(tick_positions) >= 2:
    tick_positions.sort()
    X2000_px = tick_positions[0]
    X0_px    = tick_positions[-1]
else:
    horizontal_sum = (binary_scale == 255).sum(axis=0)
    cols = np.where(horizontal_sum > (horizontal_sum.max() * 0.5))[0]
    X2000_px = float(cols[0])
    X0_px    = float(cols[-1])

scale_factor = 2000.0 / (X0_px - X2000_px)  # Ma per pixel

# 2) Load & threshold the full tree image, then skeletonize
 tree_img = cv2.imread(TREE_FNAME)
if tree_img is None:
    raise FileNotFoundError(f"Could not open '{TREE_FNAME}'.")
gray_tree = cv2.cvtColor(tree_img, cv2.COLOR_BGR2GRAY)
thresh_tree = threshold_otsu(gray_tree)
binary_tree = (gray_tree < thresh_tree).astype(np.uint8) * 255
skeleton_bool = skeletonize(binary_tree == 255)
skeleton_img  = img_as_ubyte(skeleton_bool)
cv2.imwrite("results/tree_full_skeleton.png", skeleton_img)

# 3) Detect near-horizontal line segments (include short stubs)
lines = probabilistic_hough_line(
    skeleton_img,
    threshold=10,
    line_length=5,
    line_gap=2
)

# 4) Filter by angle and record data
data = []
for (x1, y1), (x2, y2) in lines:
    dx, dy = x2 - x1, y2 - y1
    if abs(dx) < 1e-5:
        continue
    angle_deg = math.degrees(math.atan2(dy, dx))
    if abs(angle_deg) < 5.0:
        xL, yL = (x1, y1) if x1 < x2 else (x2, y2)
        length_px = math.hypot(dx, dy)
        age_Ma = round((xL - X2000_px) * scale_factor, 2)
        data.append({
            "x_left": xL,
            "y_left": yL,
            "x_right": x2 if x1 < x2 else x1,
            "y_right": y2 if y1 < y2 else y1,
            "angle": angle_deg,
            "length": length_px,
            "age_Ma": age_Ma
        })

df = pd.DataFrame(data)
df.index.name = "Seg_ID"
df.to_csv("results/tree_full_detected_segments.csv")

# 5) Overlay for visual check
plt.figure(figsize=(6, 8))
plt.imshow(skeleton_img, cmap="gray")
for seg_id, row in df.iterrows():
    plt.plot([row["x_left"], row["x_right"]], [row["y_left"], row["y_right"]], 'r-', linewidth=2)
    plt.text(row["x_left"]+2, row["y_left"]-2, str(seg_id), color="yellow", fontsize=8)
plt.axis('off')
plt.savefig("results/tree_full_overlay_detected.png", dpi=150, bbox_inches='tight')
plt.close()

print("Extraction complete. Outputs in results/ directory.")

