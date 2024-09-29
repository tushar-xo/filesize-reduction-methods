import os
import time
import gzip
import bz2
import brotli
import zstandard as zstd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def calculate_size_reduction(original_size, data_size):
    if original_size == 0:
        return float('inf')  # Handle division by zero
    return ((original_size - data_size) / original_size) * 100

def run_zstandard(file):
    with open(file, "rb") as infile:
        data = infile.read()

    start = time.time()
    compressor = zstd.ZstdCompressor()
    compressed_data = compressor.compress(data)
    compression_time = time.time() - start

    start = time.time()
    decompressor = zstd.ZstdDecompressor()
    decompressed_data = decompressor.decompress(compressed_data)
    decompression_time = time.time() - start

    original_size = os.stat(file).st_size
    compressed_size = len(compressed_data)
    decompressed_size = len(decompressed_data)

    return {
        "file": os.path.basename(file),
        "method": "Zstandard",
        "compression_time": compression_time,
        "decompression_time": decompression_time,
        "original_size": original_size,
        "compressed_size": compressed_size,
        "decompressed_size": decompressed_size,
        "size_reduction": calculate_size_reduction(original_size, compressed_size),
    }

def run_gzip(file):
    with open(file, "rb") as infile:
        data = infile.read()

    start = time.time()
    compressed_data = gzip.compress(data)
    compression_time = time.time() - start

    start = time.time()
    decompressed_data = gzip.decompress(compressed_data)
    decompression_time = time.time() - start

    original_size = os.stat(file).st_size
    compressed_size = len(compressed_data)
    decompressed_size = len(decompressed_data)

    return {
        "file": os.path.basename(file),
        "method": "Gzip",
        "compression_time": compression_time,
        "decompression_time": decompression_time,
        "original_size": original_size,
        "compressed_size": compressed_size,
        "decompressed_size": decompressed_size,
        "size_reduction": calculate_size_reduction(original_size, compressed_size),
    }

def run_bzip2(file):
    with open(file, "rb") as infile:
        data = infile.read()

    start = time.time()
    compressed_data = bz2.compress(data)
    compression_time = time.time() - start

    start = time.time()
    decompressed_data = bz2.decompress(compressed_data)
    decompression_time = time.time() - start

    original_size = os.stat(file).st_size
    compressed_size = len(compressed_data)
    decompressed_size = len(decompressed_data)

    return {
        "file": os.path.basename(file),
        "method": "Bzip2",
        "compression_time": compression_time,
        "decompression_time": decompression_time,
        "original_size": original_size,
        "compressed_size": compressed_size,
        "decompressed_size": decompressed_size,
        "size_reduction": calculate_size_reduction(original_size, compressed_size),
    }

def run_brotli(file):
    with open(file, "rb") as infile:
        data = infile.read()

    start = time.time()
    compressed_data = brotli.compress(data)
    compression_time = time.time() - start

    start = time.time()
    decompressed_data = brotli.decompress(compressed_data)
    decompression_time = time.time() - start

    original_size = os.stat(file).st_size
    compressed_size = len(compressed_data)
    decompressed_size = len(decompressed_data)

    return {
        "file": os.path.basename(file),
        "method": "Brotli",
        "compression_time": compression_time,
        "decompression_time": decompression_time,
        "original_size": original_size,
        "compressed_size": compressed_size,
        "decompressed_size": decompressed_size,
        "size_reduction": calculate_size_reduction(original_size, compressed_size),
    }

def main():
    # Original file names
    original_files = ["xor.bin", "GAP5-1RF_Rev07_IV02_old.bin", "GAP5-1RF_Rev08_IV00_new.bin"]
    results = []

    for file in original_files:
        results.append(run_zstandard(file))
        results.append(run_gzip(file))
        results.append(run_bzip2(file))
        results.append(run_brotli(file))
        results.append({})  # Append an empty dict for gap

    df = pd.DataFrame(results)

    # Drop rows with NaN values
    df.dropna(inplace=True)

    # Rename files for graphing
    df['display_file'] = df['file'].replace({
        "GAP5-1RF_Rev07_IV02_old.bin": "old.bin",
        "GAP5-1RF_Rev08_IV00_new.bin": "new.bin"
    })

    # Save results to CSV
    df.to_csv('compression_results.csv', index=False)

    # Plotting results
    plt.figure(figsize=(12, 12))

    # Pie Chart for Total Compression Time by Method
    plt.subplot(2, 2, 1)
    compression_times = df.groupby('method')['compression_time'].sum()
    wedges, texts = plt.pie(compression_times, startangle=90)
    
    # Creating a legend with percentages outside
    plt.title('Total Compression Time by Method', fontsize=14)
    percentage_labels = [f'{w:.1f}%' for w in 100 * compression_times / compression_times.sum()]
    plt.legend(wedges, [f"{method} ({pct})" for method, pct in zip(compression_times.index, percentage_labels)], title="Compression Techniques", loc='upper left', bbox_to_anchor=(1, 1))

    # Line Chart for Size Reduction
    plt.subplot(2, 2, 2)
    for method in df['method'].unique():
        subset = df[df['method'] == method]
        plt.plot(subset['display_file'], subset['size_reduction'], marker='o', label=method)

    plt.ylabel('Size Reduction (%)')
    plt.title('Compression Size Reduction Comparison', fontsize=14)
    plt.xticks(rotation=45)
    plt.grid()
    plt.legend(title='Compression Method', loc='upper left')

    # Additional Graphs for Decompression Time and Size Comparison
    plt.subplot(2, 2, 3)
    decompression_times = df.groupby('method')['decompression_time'].sum()
    plt.bar(decompression_times.index, decompression_times, color='orange')
    plt.ylabel('Total Decompression Time (s)')
    plt.title('Decompression Time by Method', fontsize=14)
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.subplot(2, 2, 4)
    size_comparisons = df.groupby('method')['original_size'].mean()
    plt.bar(size_comparisons.index, size_comparisons, color='green')
    plt.ylabel('Average Original Size (bytes)')
    plt.title('Average Original Size by Method', fontsize=14)
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
