import hashlib
import os
import sys
import zlib


def getVals(blobshaVal):
    directory = blobshaVal[0:2]
    file = blobshaVal[2:]
    return (directory, file)


def init():
    os.mkdir(".git")
    os.mkdir(".git/objects")
    os.mkdir(".git/refs")
    with open(".git/HEAD", "w") as f:
        f.write("ref: refs/heads/main\n")
    print("Initialized git directory")


def catfile(flag, blobshaVal):
    if flag != "-p":
        raise ValueError("flag is not -p")
    (directory, file) = getVals(blobshaVal)
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
    os.makedirs(".git/objects/" + directory, exist_ok=True)
    with open(path, "wb") as file:
        file.write(compressed_data)
    return hasher.hexdigest()


def lstree(flag, treeshaVal):
    if flag != "--name-only":
        raise ValueError("flag is not --name-only")
    (directory, file) = getVals(treeshaVal)
    filePath = ".git/objects/" + directory + "/" + file
    with open(filePath, "rb") as file:
        blob_data = file.read()
    decompressed = zlib.decompress(blob_data)
    header, entries = decompressed.split(b"\x00", 1)
    obj_type, size = header.split(b" ")
    i = 0
    while i < len(entries):
        null = entries.index(b"\x00", i)
        mode_name = entries[i:null]
        mode, name = mode_name.split(b" ", 1)
        # convert those raw bytes to print so first convert to string TQ ai
        print(name.decode())
        sha = entries[null + 1 : null + 1 + 20]
        i = null + 21


def writetree(base="."):
    # fxn return hash
    entries = []
    items = sorted(os.listdir(base))
    for item in items:
        if item == ".git":
            continue
        full_path = os.path.join(base, item)
        if os.path.isfile(full_path):
            mode = "100644"
            hVal = hashobject("-w", full_path)
        elif os.path.isdir(full_path):
            mode = "40000"
            hVal = writetree(full_path)
        else:
            continue
        raw_hash = bytes.fromhex(hVal)
        entry = mode.encode() + b" " + item.encode() + b"\0" + raw_hash
        entries.append(entry)
    # All entries of this directory are collected now
    tree_content = b"".join(entries)
    # Header based on size of tree content
    size = len(tree_content)
    header = f"tree {size}\0".encode()
    # Complete Git tree object
    store = header + tree_content
    # SHA-1 of complete object
    tree_hash = hashlib.sha1(store).hexdigest()
    # Store in .git/objects/XX/YYYY...
    directory = tree_hash[:2]
    filename = tree_hash[2:]
    object_dir = os.path.join(".git", "objects", directory)
    os.makedirs(object_dir, exist_ok=True)
    path = os.path.join(object_dir, filename)
    with open(path, "wb") as f:
        f.write(zlib.compress(store))
    return tree_hash


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
    elif command == "ls-tree":
        fflag = sys.argv[2]
        tree_sha = sys.argv[3]
        lstree(fflag, tree_sha)
    elif command == "write-tree":
        print(writetree("."))

    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
