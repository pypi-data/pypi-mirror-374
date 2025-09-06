import hashlib


def sha256_file(filename: str) -> str:

    sha256hash = hashlib.sha256()

    with open(filename, "rb") as f:

        while True:

            data = f.read(1048576)
            if not data:
                break
            sha256hash.update(data)

    return sha256hash.hexdigest()

