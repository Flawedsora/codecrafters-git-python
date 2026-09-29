import hashlib
import os
import sys
import zlib


def getVals(shaVal):
    directory = shaVal[0:2]
    file = shaVal[2:]
    return (directory, file)


def init():
    os.mkdir(".git")
    os.mkdir(".git/objects")
    os.mkdir(".git/refs")
    with open(".git/HEAD", "w") as f:
        f.write("ref: refs/heads/main\n")
    print("Initialized git directory")


def catfile(flag, shaVal):
    if flag != "-p":
        raise ValueError("flag is not -p")
    (directory, file) = getVals(shaVal)
    filePath = ".git/objects/" + directory + "/" + file
    with open(filePath, "rb") as file:
        blob_data = file.read()
    decompressed = zlib.decompress(blob_data)
    header, content = decompressed.split(b"\x00", 1)
    sys.stdout.buffer.write(content)


def hashobject(flag, f):
    # The input for the SHA-1 hash is the header (blob <size>\0) + the actual contents of the file, not just the contents of the file.
    # with -w flag it should write to file
    if flag != "-w":
        raise ValueError("flag is not -w")
    with open(f, "rb") as file:
        content = file.read()
    num_bytes = len(content)
    header = f"blob {num_bytes}\x00".encode()
    store = header + content
    hasher = hashlib.sha1(store)
    directory, file = getVals(hasher.hexdigest())
    path = ".git/objects/" + directory + "/" + file
    # we want compressed data at this path
    compressed_data = zlib.compress(store)
    # we first make directory
    os.mkdir(".git/objects/" + directory)
    with open(path, "wb") as file:
        file.write(compressed_data)
    return hasher.hexdigest()


def main():
    print("Logs from your program will appear here!", file=sys.stderr)

    command = sys.argv[1]
    if command == "init":
        init()
    elif command == "cat-file":
        flag = sys.argv[2]
        shaval = sys.argv[3]
        catfile(flag, shaval)
    elif command == "hash-object":
        flag = sys.argv[2]
        file = sys.argv[3]
        hashval = hashobject(flag, file)
        print(hashval)
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
