import sys
import os
import time
import brotli  # Import the Brotli library

def calculate_size_reduction(original_size, data_size):
    """Calculates the percentage reduction in file size after encoding.
    :returns reduction: float"""

    if original_size == 0:
        return float('inf')  # Handle division by zero
    reduction = ((original_size - data_size) / original_size) * 100
    return reduction

def main():
    files = ["xor.bin", "GAP5-1RF_Rev07_IV02_old.bin", "GAP5-1RF_Rev08_IV00_new.bin"]
    for file in files:
        print(f"\n\nFor file {file}:\n")

        with open(file, "rb") as infile:
            data = infile.read()

        # Compression
        start = time.time()
        compressed_data = brotli.compress(data)
        end = time.time()
        compression_time = end - start

        with open(f"compressed_{file}", "wb") as outfile:
            outfile.write(compressed_data)

        # Decompression
        start = time.time()
        decompressed_data = brotli.decompress(compressed_data)
        end = time.time()
        decompressing_time = end - start

        with open(f"decompressed_{file}", "wb") as outfile:
            outfile.write(decompressed_data)

        original_size = os.stat(file).st_size  # bytes
        compressed_size = os.stat(f"compressed_{file}").st_size  # bytes
        decompressed_size = os.stat(f"decompressed_{file}").st_size  # bytes

        reduction1 = calculate_size_reduction(original_size, compressed_size)
        reduction2 = calculate_size_reduction(original_size, decompressed_size)
        loss = reduction2
        reproducibility = 100 - loss
        print(f"Size reduction achieved by compression: {reduction1:.2f}%")
        print(f"Size reduction from original after decompression: {reduction2:.2f}%")
        print(f"Hence Reproducibility = {reproducibility:.2f}%")
        print(f"Loss = {loss:.2f}%")
        print("Compression time: ", compression_time, " s.")
        print("Decompression time: ", decompressing_time, " s.")

    print("\n\nResults:")
    print("Positive Compression: Reduction in size")
    print("Negative compression: Increment in size")
    print("Brotli is a highly efficient data compression tool")

if __name__ == "__main__":
    main()
