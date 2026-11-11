from collections import defaultdict
from pathlib import Path

DATA_DIR = Path("src/data")


def parse_features(blob: bytes):
    features = defaultdict(list)
    if not blob:
        return features
    for entry in blob.split(b"\x01"):
        field_id, rest = entry.split(b"\x02", 1)
        feature_id, value = rest.split(b"\x03", 1)
        features[field_id.decode("ascii")].append(
            (feature_id.decode("ascii"), float(value))
        )
    return features


with (DATA_DIR / "sample_skeleton_train.csv").open("rb") as stream:
    row = stream.readline().rstrip(b"\r\n")
    sample_id, click, conversion, common_id, feature_num, blob = row.split(b",", 5)
    features = parse_features(blob)
    assert sum(map(len, features.values())) == int(feature_num)
    print(sample_id.decode(), int(click), int(conversion), common_id.decode())

    print({field: len(values) for field, values in features.items()})

common_id, feature_num, blob = common_row.rstrip(b"\r\n").split(b",", 2)
common_features = parse_features(blob)