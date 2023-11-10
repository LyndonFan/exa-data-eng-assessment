from pathlib import Path

from src.extract.extract import Extractor
from src.transform.transform_factory import TransformFactory
from src.load.loader import Loader


def main(filepath: Path) -> None:
    print(f"Start processing {filepath}")
    documents = []
    if filepath.is_dir():
        for path in filepath.rglob("*.json"):
            print(f"Processing {path}")
            print("Extracting...")
            data = Extractor().extract(path)
            print("Transforming...")
            for entry in data:
                transformed = TransformFactory.transform(entry.resource)
                documents.append(transformed)
            print(f"Done for {path}")
    elif filepath.is_file() and filepath.suffix == ".json":
        print(f"Processing {filepath}")
        print("Extracting...")
        data = Extractor().extract(filepath)
        print("Transforming...")
        for entry in data:
            transformed = TransformFactory.transform(entry.resource)
            documents.append(transformed)
        print("Done")
    else:
        raise ValueError(f"Unsupported file type: {filepath}")
    print("Uploading...")
    Loader().upload(documents)
    print("Done")


if __name__ == "__main__":
    import sys

    main(Path(sys.argv[1]))
