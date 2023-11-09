from pathlib import Path

from src.extract.extract import Extractor
from src.transform.transform_factory import TransformFactory
from src.load.loader import Loader


def main(filepath: Path) -> None:
    print(f"Start processing {filepath}")
    print("Extracting...")
    data = Extractor().extract(filepath)
    print("Transforming...")
    documents = []
    for entry in data:
        transformed = TransformFactory.transform(entry.resource)
        documents.append(transformed)
    print("Uploading...")
    Loader().upload(documents)
    print("Done")

if __name__ == "__main__":
    import sys
    main(Path(sys.argv[1]))