import time
import gzip
import bsdiff4
import rle
import os
import psutil


def monitor_cpu_usage():
    cpu_percent = psutil.cpu_percent()
    return cpu_percent


def main():
    with open("GAP5-1RF_Rev07_IV02_old.bin", "rb") as infile:
        old = bytes(infile.read())

    with open("GAP5-1RF_Rev08_IV00_new.bin", "rb") as infile:
        new = bytes(infile.read())

    # Track CPU and memory usage before compression
    cpu_before = monitor_cpu_usage()
    start = time.time()

    del_file_array = bsdiff4.diff(old, new)
    print("Length of patch file: ", len(del_file_array))

    with open("../del_file.bin", "wb") as outfile:
        outfile.write(del_file_array)

    # Track CPU and memory usage during compression
    cpu_during_compression = monitor_cpu_usage()
    end = time.time()
    encoding_time = end - start

    del_size = os.stat("../del_file.bin").st_size  # bytes
    original_size = os.stat("GAP5-1RF_Rev07_IV02_old.bin").st_size  # bytes

    reduction1 = rle.calculate_size_reduction(original_size, del_size)
    print(f"Size reduction of delta file using bsdiff4 compression: {reduction1:.2f}%")
    print("Compression time: ", encoding_time, " s.")
    print("CPU utilization during compression:", cpu_during_compression - cpu_before, "%")

    # Applying patch now
    with open("sample_old.bin", 'rb') as old_file:
        old = bytes(old_file.read())

    patched_bytes = bsdiff4.patch(old, del_file_array)
    print("Length of old file in bytes: ", len(old))
    print("Length of new patched file after applying patch on old file: ", len(patched_bytes))
    print("Length of new file which we already had: ", len(new))


if __name__ == "__main__":
    main()