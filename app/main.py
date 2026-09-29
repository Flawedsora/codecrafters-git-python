import os
import sys
import zlib


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
    directory = shaVal[0:2]
    file = shaVal[2:]
    filePath = ".git/objects/" + directory + "/" + file
    with open(filePath, "rb") as file:
        blob_data = file.read()
    decompressed = zlib.decompress(blob_data)
    header, content = decompressed.split(b"\x00", 1)
    sys.stdout.buffer.write(content)


def main():
    print("Logs from your program will appear here!", file=sys.stderr)

    command = sys.argv[1]
    if command == "init":
        init()
    elif command == "cat-file":
        flag = sys.argv[2]
        shaval = sys.argv[3]
        catfile(flag, shaval)
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
