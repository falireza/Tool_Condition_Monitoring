"""
This code performs Savitzky-Golay smoothing, detects peaks, detects breaking points between the peaks, identifies patterns.
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks, savgol_filter

# File path for the intact tool data
file_path = r"processed_data\chamfer_fractured_processed.csv"

def savgol_peak_finder(data_path):
    tool_data = pd.read_csv(data_path)
    # Apply Savitzky-Golay filter to smooth the data
    window_length = 111  # Window length for smoothing (must be an odd number)
    polyorder = 2       # Degree of polynomial for smoothing
    smoothed_pixels = savgol_filter(tool_data['Sum of Pixels'], window_length=window_length, polyorder=polyorder)

    # Plot both original and smoothed data
    plt.figure(figsize=(10,6))
    plt.plot(tool_data['Degree'], tool_data['Sum of Pixels'], label="Original Sum of Pixels", color='blue')
    plt.plot(tool_data['Degree'], smoothed_pixels, label="Smoothed Sum of Pixels", color='orange')
    plt.title("Original and Smoothed, Intact Tool Data")
    plt.xlabel("Degree")
    plt.ylabel("Sum of Pixels")
    plt.grid(True)
    plt.legend()
    plt.show()


    distance = 30 # Minimum horizontal distance between peaks
    significant_peaks, _ = find_peaks(smoothed_pixels, distance=distance)

    peak_degrees = tool_data['Degree'].iloc[significant_peaks].values
    peak_values = smoothed_pixels[significant_peaks]

    # Create a DataFrame to display the peak degrees and values
    peaks_df = pd.DataFrame({
        'Peak Degree': peak_degrees,
        'Peak Value (Sum of Pixels)': peak_values
    })

    print("Peaks detected:")
    print(peaks_df)

    # Define patterns as breaking-point to breaking-point
    minima = []

    for i in range(len(significant_peaks)):
        # If not the last peak, find minima between successive peaks
        if i < len(significant_peaks) - 1:
            segment = smoothed_pixels[significant_peaks[i]:significant_peaks[i + 1]]
        else:
            # For the wrap-around case (last peak to first peak)
            segment = np.concatenate([smoothed_pixels[significant_peaks[i]:], smoothed_pixels[:significant_peaks[0]]])

        # Find the minimum value's index in the current segment
        min_index_in_segment = np.argmin(segment)
        
        # Adjust index based on the segment being part of the overall signal
        if i < len(significant_peaks) - 1:
            minima.append(significant_peaks[i] + min_index_in_segment)
        else:
            minima.append((significant_peaks[i] + min_index_in_segment) % len(smoothed_pixels))

    # Define patterns based on the minima, with wrap-around case
    pattern_boundaries = []
    for i in range(len(significant_peaks)):
        if i < len(significant_peaks) - 1:
            start = significant_peaks[i]
            end = significant_peaks[i + 1]
        else:
            # wrap-around case
            start = significant_peaks[i]
            end = significant_peaks[0]

        pattern_boundaries.append((start, end))


    # Plot the smoothed data with significant peaks and boundaries
    plt.figure(figsize=(10,6))
    plt.plot(tool_data['Degree'], smoothed_pixels, label="Smoothed Sum of Pixels", color='orange')

    colors = ['green', 'red', 'blue', 'purple', 'yellow']

    for i, (start, end) in enumerate(pattern_boundaries):
        if start < end:
            plt.axvspan(tool_data['Degree'][start], tool_data['Degree'][end], color=colors[i % len(colors)], alpha=0.3)
        else:
            # For the wrap-around case
            plt.axvspan(tool_data['Degree'][start], tool_data['Degree'].iloc[-1], color=colors[i % len(colors)], alpha=0.3)
            plt.axvspan(tool_data['Degree'][0], tool_data['Degree'][end], color=colors[i % len(colors)], alpha=0.3)

    plt.title("Segmented the pattern")
    plt.xlabel("Degree")
    plt.ylabel("Sum of Pixels")
    plt.grid(True)
    plt.legend()
    plt.show()

    # Show the start and end degrees of the significant peak-to-peak patterns
    pattern_boundaries_df = pd.DataFrame(pattern_boundaries, columns=['Pattern Start (Degree)', 'Pattern End (Degree)'])
    print(pattern_boundaries_df)

    return smoothed_pixels, pattern_boundaries

# ...existing code...

if __name__ == "__main__":
    savgol_peak_finder(file_path)