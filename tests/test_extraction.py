import subprocess
import pandas as pd
import os
import shutil
from pathlib import Path

def test_extract_metazoa_ages(tmp_path, capsys):
    # Setup directory structure
    repo_dir = tmp_path / "metazoa-node-ages"
    data_dir = repo_dir / "data"
    scripts_dir = repo_dir / "scripts"
    results_dir = repo_dir / "results"
    data_dir.mkdir(parents=True)
    scripts_dir.mkdir()
    results_dir.mkdir()

    # Copy test images from repository data/ to tmp_path/data/
    # (Assumes test runner has access to original data files)
    src_tree = Path(__file__).parent.parent / "data" / "tree_full.png"
    src_scale = Path(__file__).parent.parent / "data" / "scale_full.png"
    dst_tree = data_dir / "tree_full.png"
    dst_scale = data_dir / "scale_full.png"
    shutil.copy(src_tree, dst_tree)
    shutil.copy(src_scale, dst_scale)

    # Copy extraction script into scripts/
    src_script = Path(__file__).parent.parent / "scripts" / "extract_metazoa_ages.py"
    dst_script = scripts_dir / "extract_metazoa_ages.py"
    shutil.copy(src_script, dst_script)

    # Run the extraction script
    completed = subprocess.run(
        ["python", str(dst_script)],
        cwd=repo_dir,
        capture_output=True,
        text=True
    )
    # Check script ran without errors
    assert completed.returncode == 0, f"Script failed: {completed.stderr}"

    # Check output files exist
    csv_path = results_dir / "tree_full_detected_segments.csv"
    overlay_path = results_dir / "tree_full_overlay_detected.png"
    skeleton_path = results_dir / "tree_full_skeleton.png"
    assert csv_path.exists(), "Detected segments CSV was not created"
    assert overlay_path.exists(), "Overlay image was not created"
    assert skeleton_path.exists(), "Skeleton image was not created"

    # Load CSV and verify columns
    df = pd.read_csv(csv_path)
    expected_cols = {"Seg_ID", "x_left", "y_left", "x_right", "y_right", "angle", "length", "age_Ma"}
    assert set(df.columns) >= expected_cols, f"CSV missing expected columns: {expected_cols - set(df.columns)}"

    # Verify at least one segment detected
    assert not df.empty, "No segments were detected in the CSV"

    # Optionally verify age_Ma values are within [0, 2000]
    assert df['age_Ma'].between(0, 2000).all(), "Some ages are out of expected range"

    print("All extraction tests passed.")

