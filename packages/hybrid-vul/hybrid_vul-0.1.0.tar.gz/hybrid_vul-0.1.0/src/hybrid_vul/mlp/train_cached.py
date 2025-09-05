import os
import time
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report


def _train_one(mode: str, feature_path: str):
    """Train and evaluate on a single cached feature file. Returns (report, durations_dict)."""
    if not feature_path or not os.path.exists(feature_path):
        print(f"❌ Feature file not found for {mode}: {feature_path}")
        return None, {"AST Extraction": 0.0, "CodeBERT Encoding": 0.0, "MLP Training": 0.0}

    print(f"\n✅ Loading cached features from: {feature_path} for {mode}")
    data = np.load(feature_path)
    X, y = data["X"], data["y"]

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train MLP
    print(f"[{mode}] Training MLPClassifier...")
    start_train = time.time()
    clf = MLPClassifier(hidden_layer_sizes=(1024, 64), max_iter=500, random_state=42)
    clf.fit(X_train, y_train)
    duration_mlp = round(time.time() - start_train, 2)

    # Evaluate
    y_pred = clf.predict(X_test)
    print(f"\n=== {mode} Evaluation ===")
    print(classification_report(y_test, y_pred, digits=4))

    return clf, {
        "AST Extraction": 0.0,        # already cached
        "CodeBERT Encoding": 0.0,     # already cached
        "MLP Training": duration_mlp,
    }


def _plot_gantt(stage_times: dict, out_png: str, show: bool):
    base_time = datetime(2025, 7, 27, 10, 0, 0)
    records = []

    for device, stages in stage_times.items():
        curr_time = base_time
        for stage, duration in stages.items():
            end = curr_time + timedelta(seconds=duration)
            records.append({
                "Device": device,
                "Stage": stage,
                "Start": curr_time,
                "End": end,
                "Duration": duration
            })
            curr_time = end + timedelta(seconds=3)

    if not records:
        print("No records to plot; skipping Gantt chart.")
        return

    df = pd.DataFrame(records)

    colors = {
        "AST Extraction": "#87CEEB",
        "CodeBERT Encoding": "#FFA500",
        "MLP Training": "#32CD32"
    }

    fig, ax = plt.subplots(figsize=(14, 7))
    yticks, yticklabels = [], []

    for i, row in df.iterrows():
        y = i * 1.5
        duration = (row['End'] - row['Start']).total_seconds()
        ax.barh(y, duration, left=row['Start'], height=1.1, color=colors.get(row['Stage'], 'gray'))
        ax.text(row['Start'] + timedelta(seconds=duration / 2), y,
                f"{row['Duration']}s", ha='center', va='center',
                fontsize=8, color='black',
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.8))
        yticks.append(y)
        yticklabels.append(f"{row['Device']} - {row['Stage']}")

    ax.set_yticks(yticks)
    ax.set_yticklabels(yticklabels)
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.set_title("Gantt Chart: MLP Training Timeline Using Cached Features (CPU vs GPU)", fontsize=14)
    ax.set_xlabel("Time")
    ax.set_ylabel("Task")
    ax.grid(True, axis='x', linestyle='--', alpha=0.5)

    handles = [plt.Rectangle((0, 0), 1, 1, color=color) for color in colors.values()]
    labels = list(colors.keys())
    ax.legend(handles, labels, title="Pipeline Stage", loc="upper right")

    plt.tight_layout()
    plt.savefig(out_png)
    if show:
        plt.show()
    plt.close(fig)
    print(f"Saved Gantt chart to: {out_png}")


def run_cached_pipeline(features_cpu: str = "features_cpu.npz",
                        features_gpu: str = "features_gpu.npz",
                        out_png: str = "gantt_mlp_training_from_cache.png",
                        show: bool = True):
    stage_times = {}

    # CPU
    _, cpu_times = _train_one("CPU", features_cpu)
    if cpu_times:
        stage_times["CPU"] = cpu_times

    # GPU (CUDA)
    _, gpu_times = _train_one("CUDA", features_gpu)
    if gpu_times:
        stage_times["CUDA"] = gpu_times

    _plot_gantt(stage_times, out_png=out_png, show=show)


def main():
    # Optional direct run (not used when invoked via CLI entry point)
    print("hybrid-vul CLI is working")
    run_cached_pipeline()


if __name__ == "__main__":
    main()
