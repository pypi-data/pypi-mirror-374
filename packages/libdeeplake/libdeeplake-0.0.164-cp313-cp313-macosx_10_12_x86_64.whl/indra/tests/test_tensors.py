from indra import api
import deeplake
import numpy as np
from .utils import tmp_datasets_dir
from .constants import (
    MNIST_DS_NAME,
)


def test_indra():
    ds = api.dataset(MNIST_DS_NAME)
    tensors = ds.tensors
    assert isinstance(tensors, list)


def test_headless_tensor(tmp_datasets_dir):
    ds = deeplake.dataset(tmp_datasets_dir / "headless-tensor-ds", overwrite=True)
    with ds:
        ds.create_tensor("labels", dtype=np.uint8, htype="class_label")
        ds.labels.append(1)
        ds.labels.append(2)
        ds.labels.append(3)
    ids = api.dataset(str(tmp_datasets_dir / "headless-tensor-ds"))
    t = ids.labels
    del ids
    assert len(t) == 3
    assert np.all(t[0].numpy() == [1])
    assert np.all(t[1].numpy() == [2])
    assert np.all(t[2].numpy() == [3])
    tt = t[0:2]
    del t
    assert len(tt) == 2


def test_class_names_reordering_tensor(tmp_datasets_dir):
    path1 = tmp_datasets_dir / "diff_class_labels_1"
    path2 = tmp_datasets_dir / "diff_class_labels_2"
    ds1 = deeplake.dataset(path1, overwrite=True)
    ds2 = deeplake.dataset(path2, overwrite=True)
    with ds1:
        ds1.create_tensor("labels", dtype=np.uint16, htype="class_label")
        ds1.labels.append("one")
        ds1.labels.append("two")
        ds1.labels.append("three")

    with ds2:
        ds2.create_tensor("labels", dtype=np.uint16, htype="class_label")
        ds2.labels.append("three")
        ds2.labels.append("two")
        ds2.labels.append("one")

    assert ds1.labels.info["class_names"] != ds2.labels.info["class_names"]
    print("CLASS_NAMES: ", ds1.labels.info)
    print("CLASS_NAMES: ", ds2.labels.info)

    q1 = f'SELECT * FROM "{path1}"'
    q2 = f'SELECT * FROM "{path2}"'
    ds = deeplake.query(f"{q1} UNION {q2}")
    assert len(ds) == 6

    assert np.all(
        ds.labels[:].numpy()
        == np.array([[0], [1], [2], [2], [1], [0]], dtype=np.uint16)
    )
    assert np.all(ds.labels[3].numpy() == np.array([2], dtype=np.uint16))
    assert np.all(ds.labels[4].numpy() == np.array([1], dtype=np.uint16))
    assert np.all(ds.labels[3:5].numpy() == np.array([[2], [1]], dtype=np.uint16))
    assert np.all(
        ds.labels[1:5].numpy() == np.array([[1], [2], [2], [1]], dtype=np.uint16)
    )
