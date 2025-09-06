from indra import api
import os

root = os.environ["VIZ_TEST_DATASETS_PATH"]

def test_nifti_gz():
    ds = api.dataset(os.path.join(root, 'nifti/'))
    d = ds.t2[0].numpy()
    assert(d.shape == (155, 240, 240, 1))

    ds = api.dataset(os.path.join(root, 'nifti_resampled_gz/'))
    d = ds.scan[0].numpy()
    assert(d.shape == (32, 49, 49, 1))

    d = ds.segmentation[0].numpy()
    assert(d.shape == (32, 49, 49, 1))

    d = ds.scan[1].numpy()
    assert(d.shape == (45, 56, 87, 1))

def test_nifti():
    ds = api.dataset(os.path.join(root, 'nifti_resampled/'))
    d = ds.scan[0].numpy()
    assert(d.shape == (45, 56, 87, 1))
