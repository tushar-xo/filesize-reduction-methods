import os
import time
import gzip
import bz2
import brotli
import zstandard as zstd
import rle  # Ensure this module is available for RLE functions
import psutil
import matplotlib.pyplot as plt
import pandas as pd

def create_patch_file(old, new, patch_file):
    size = min(len(old), len(new))
    xor_byte_array = bytearray(size)

    for i in range(size):
        xor_byte_array[i] = old[i] ^ new[i]

    with open(patch_file, "wb") as outfile:
        outfile.write(xor_byte_array)

def compress_data(method, data):
    if method == "RLE":
        return rle.run_length_encode(data)
    elif method == "Gzip":
        return gzip.compress(data)
    elif method == "Bzip2":
        return bz2.compress(data)
    elif method == "Zstandard":
        compressor = zstd.ZstdCompressor()
        return compressor.compress(data)
    elif method == "Brotli":
        return brotli.compress(data)

def decompress_data(method, data):
    if method == "RLE":
        return rle.run_length_decode(data)
    elif method == "Gzip":
        return gzip.decompress(data)
    elif method == "Bzip2":
        return bz2.decompress(data)
    elif method == "Zstandard":
        decompressor = zstd.ZstdDecompressor()
        return decompressor.decompress(data)
    elif method == "Brotli":
        return brotli.decompress(data)

def calculate_size_reduction(original_size, compressed_size):
    if original_size == 0:
        return float('inf')
    return ((original_size - compressed_size) / original_size) * 100

def monitor_resource_usage():
    return psutil.cpu_percent(), psutil.virtual_memory().percent

def bytes_to_kilobytes(size_bytes):
    return size_bytes / 1024  # Convert bytes to kilobytes

def main():
    # Load old and new firmware
    with open("GAP5-1RF_Rev07_IV02_old.bin", "rb") as infile:
        old_firmware = bytearray(infile.read())

    with open("GAP5-1RF_Rev08_IV00_new.bin", "rb") as infile:
        new_firmware = bytearray(infile.read())

    # Create patch file
    patch_file = "del_file.bin"
    create_patch_file(old_firmware, new_firmware, patch_file)

    # Read patch file for compression
    with open(patch_file, "rb") as infile:
        del_file_array = infile.read()

    compression_results = []
    
    # Apply different compression techniques
    for method in ["RLE", "Gzip", "Bzip2", "Zstandard", "Brotli"]:
        # Monitor resource usage before compression
        cpu_before, memory_before = monitor_resource_usage()
        
        # Start time for patch file compression
        start_time = time.time()
        compressed_data = compress_data(method, del_file_array)
        compressed_size = len(compressed_data)
        original_size = len(del_file_array)

        # Track compression time
        encoding_time_patch = time.time() - start_time

        # Decompression to check reproducibility
        start_time_decompression = time.time()
        decompressed_data = decompress_data(method, compressed_data)
        decoding_time = time.time() - start_time_decompression
        decoded_size = len(decompressed_data)

        # Calculate metrics
        size_reduction_patch = calculate_size_reduction(original_size, compressed_size)
        size_reduction_decompression = calculate_size_reduction(original_size, decoded_size)

        # Store results for patch file compression
        compression_results.append({
            "method": method,
            "original_size_kb": bytes_to_kilobytes(original_size),
            "compressed_size_kb": bytes_to_kilobytes(compressed_size),
            "decoded_size_kb": bytes_to_kilobytes(decoded_size),
            "reduction_patch": size_reduction_patch,
            "reduction_decompression": size_reduction_decompression,
            "encoding_time_patch": encoding_time_patch,
            "decoding_time": decoding_time,
        })

        # Monitor resource usage before original firmware compression
        cpu_before_orig, memory_before_orig = monitor_resource_usage()
        
        # Start time for original firmware compression
        start_time_orig = time.time()
        compressed_orig = compress_data(method, old_firmware)
        compressed_size_orig = len(compressed_orig)
        original_size_orig = len(old_firmware)

        # Store results for original firmware compression
        compression_results[-1]['original_firmware_size_kb'] = bytes_to_kilobytes(original_size_orig)
        compression_results[-1]['original_firmware_compressed_size_kb'] = bytes_to_kilobytes(compressed_size_orig)

    # Create DataFrame for visualization
    df = pd.DataFrame(compression_results)

    # Visualization
    plt.figure(figsize=(15, 12))

    # Line Chart for Encoding and Decoding Times
    plt.subplot(4, 1, 1)
    plt.plot(df['method'], df['encoding_time_patch'], marker='o', label='Patch Encoding Time (s)', color='green')
    plt.plot(df['method'], df['decoding_time'], marker='o', label='Decoding Time (s)', color='red')
    plt.ylabel('Time (s)')
    plt.title('Encoding and Decoding Time Comparison')
    plt.legend()
    plt.grid()

    # Line Chart for Size Reduction
    plt.subplot(4, 1, 2)
    plt.plot(df['method'], df['reduction_patch'], marker='o', label='Size Reduction (Patch %)', color='blue')
    plt.plot(df['method'], df['reduction_decompression'], marker='o', label='Size Reduction (Decompression %)', color='orange')
    plt.ylabel('Size Reduction (%)')
    plt.title('Size Reduction Comparison')
    plt.legend()
    plt.grid()

    # Bar Chart for Original and Compressed Sizes
    plt.subplot(4, 1, 3)
    bar_width = 0.2
    index = range(len(df['method']))
    plt.bar(index, df['original_size_kb'], bar_width, label='Original Size (KB)', color='black')
    plt.bar([i + bar_width for i in index], df['compressed_size_kb'], bar_width, label='Compressed Patch Size (KB)', color='blue')
    plt.bar([i + bar_width * 2 for i in index], df['original_firmware_compressed_size_kb'], bar_width, label='Original Compressed Size (KB)', color='orange')
    plt.xticks([i + bar_width for i in index], df['method'])
    plt.ylabel('File Size (KB)')
    plt.title('File Sizes Before and After Compression')
    plt.legend()
    plt.grid()

    # Single Bar Chart for Overall Size Reduction of Patch
    plt.subplot(4, 1, 4)
    plt.bar(df['method'], df['reduction_patch'], label='Overall Size Reduction (Patch %)', color='purple')
    plt.ylabel('Overall Size Reduction (%)')
    plt.title('Overall Size Reduction for Patching')
    plt.legend()
    plt.grid()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
