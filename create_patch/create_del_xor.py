"""
    Creation of xor file - del_file.bin, containing
    the difference of old and new firmware, followed by
    application of RLE on this del_bin file

    NOTE: del_file although only contains the difference, one
    drawback of XOR approach is that the del_file size is still
    equal to the old file size (non different bits are set to zero)

    To overcome this drawback, other differencing algorithms
    provided by python3 may be used.

"""

import time
import rle
import os
import psutil


def create_del_file_array(old, new):
    # Set the length to be the smaller one
    if len(old) < len(new):
        size = len(old)
    else:
        size = len(new)

    xor_byte_array = bytearray(size)

    # XOR between the files
    for i in range(size):
        xor_byte_array[i] = old[i] ^ new[i]

    return xor_byte_array


def monitor_cpu_usage():
    cpu_percent = psutil.cpu_percent()
    return cpu_percent


def main():
    with open("GAP5-1RF_Rev07_IV02_old.bin", "rb") as infile:
        old = bytearray(infile.read())

    with open("GAP5-1RF_Rev08_IV00_new.bin", "rb") as infile:
        new = bytearray(infile.read())

    del_file_array = create_del_file_array(old, new)
    with open("../del_file.bin", "wb") as outfile:
        outfile.write(del_file_array)

    # Track CPU and memory usage before compression
    cpu_before = monitor_cpu_usage()
    start = time.time()
    compressed_del = rle.run_length_encode(del_file_array)
    # Track CPU and memory usage during compression
    cpu_during_compression = monitor_cpu_usage()
    end = time.time()
    encoding_time = end - start

    with open("../compressed_del.bin", "wb") as outfile:
        outfile.write(compressed_del)

    # Track CPU and memory usage before decompression
    cpu_before_decompression = monitor_cpu_usage()
    start = time.time()
    decompressed_del = rle.run_length_decode(compressed_del)
    end = time.time()
    decoding_time = end - start

    # Track CPU and memory usage during decompression
    cpu_during_decompression = monitor_cpu_usage()
    with open("../decompressed_del.bin", "wb") as outfile:
        outfile.write(decompressed_del)

    original_size = os.stat("../del_file.bin").st_size  # bytes
    encoded_size = os.stat(f"../compressed_del.bin").st_size  # bytes
    decoded_size = os.stat(f"../decompressed_del.bin").st_size  # bytes

    reduction1 = rle.calculate_size_reduction(original_size, encoded_size)
    reduction2 = rle.calculate_size_reduction(original_size, decoded_size)
    loss = reduction2
    reproducibility = 100 - loss
    print(f"Size reduction of delta file using RLE compression: {reduction1:.2f}%")
    print(f"Size reduction from delta file after RLE decompression: {reduction2:.2f}%")
    print(f"Hence Reproducibility = {reproducibility:.2f}%")
    print(f"Loss = {loss:.2f}%")
    print("Compression time: ", encoding_time, " s.")
    print("Decompression time: ", decoding_time, " s.")
    print("CPU utilization during compression:", cpu_during_compression - cpu_before, "%")
    print("CPU utilization during decompression:", cpu_during_decompression - cpu_before_decompression, "%")

    print("Results:")
    print("Positive Compression: Reduction in size")
    print("Negative compression: Increment in size")
    print("RLE works best when there are long runs of repeating data")


if __name__ == "__main__":
    main()

