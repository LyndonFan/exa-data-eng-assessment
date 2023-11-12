from pathlib import Path

from src.extract import Extractor
from src.process import ProcessorFactory


def main(filepath: Path) -> None:
    print(f"Start processing {filepath}")
    documents = []
    if filepath.is_dir():
        for path in filepath.rglob("*.json"):
            print(f"Processing {path}")
            print("Extracting...")
            data = Extractor().extract(path)
            print(f"Done for {path}")
            documents.extend(data)
    elif filepath.is_file() and filepath.suffix == ".json":
        print(f"Processing {filepath}")
        print("Extracting...")
        data = Extractor().extract(filepath)
        documents = data
        print("Done")
    else:
        raise ValueError(f"Unsupported file type: {filepath}")
    print("Processing & Uploading...")
    ProcessorFactory.batch_process(documents)
    print("Done")


if __name__ == "__main__":
    import sys

    main(Path(sys.argv[1]))
