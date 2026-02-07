import hashlib

def book_id(path: str) -> str:
    return hashlib.md5(path.encode("utf-8")).hexdigest()