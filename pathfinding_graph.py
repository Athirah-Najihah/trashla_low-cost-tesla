import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Load the CSV file
csv_file_path = "pathfinding_metrics.csv"  # Update this with the actual path to your file
data = pd.read_csv(csv_file_path)

# Extract data from the CSV
frames = data["Frame"].tolist()
centroid_error = data["Centroid Error"].tolist()
fps = data["FPS"].tolist()  # Assuming the FPS column exists in the CSV

# Optional: Apply a moving average for smoothing (window size can be adjusted)
window_size = 10  # Adjust this for smoothness
centroid_error_smoothed = np.convolve(centroid_error, np.ones(window_size)/window_size, mode='valid')

# Identify QR Code Detection Events
qr_code_events = data[data["Direction"] == "QR_CODE_DETECTED"]
qr_code_frames = qr_code_events["Frame"].tolist()
qr_code_labels = qr_code_events["QR Code Detected"].tolist()  # Assuming QR Code Detected column exists

# Set up a figure with two subplots
fig, ax = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

# ---- Subplot 1: Centroid Error ----
ax[0].plot(frames, centroid_error, label='Centroid Error (Raw)', color='blue', alpha=0.6, linewidth=1)
ax[0].plot(frames[window_size-1:], centroid_error_smoothed, label='Centroid Error (Smoothed)', color='green', linewidth=2)

# Highlight spikes for better analysis
spike_threshold = np.percentile(centroid_error, 95)  # Using the 95th percentile as the threshold
spike_indices = [i for i, error in enumerate(centroid_error) if error > spike_threshold]
spike_values = [centroid_error[i] for i in spike_indices]
ax[0].scatter([frames[i] for i in spike_indices], spike_values, color='red', label='Error Spike', zorder=5)

# Add QR Code Detection Events
for i, frame in enumerate(qr_code_frames):
    ax[0].axvline(x=frame, color='purple', linestyle='--', linewidth=1, alpha=0.7)
    ax[0].text(frame, max(centroid_error)*0.9, qr_code_labels[i], rotation=90, color='purple', fontsize=8, ha='center')

# Subplot 1 Labels
ax[0].set_title('Centroid Error Over Frames with QR Code Detection', fontsize=14)
ax[0].set_ylabel('Centroid Error (pixels)', fontsize=12)
ax[0].grid(alpha=0.3)
ax[0].legend()

# ---- Subplot 2: FPS Over Time ----
ax[1].plot(frames, fps, label='FPS', color='orange', linewidth=2)
ax[1].axhline(y=np.mean(fps), color='red', linestyle='--', linewidth=1, label=f'Average FPS: {np.mean(fps):.2f}')

# Subplot 2 Labels
ax[1].set_title('Frames Per Second (FPS) Over Time', fontsize=14)
ax[1].set_xlabel('Frame Number', fontsize=12)
ax[1].set_ylabel('FPS', fontsize=12)
ax[1].grid(alpha=0.3)
ax[1].legend()

# Adjust layout and show the plot
plt.tight_layout()
plt.show()