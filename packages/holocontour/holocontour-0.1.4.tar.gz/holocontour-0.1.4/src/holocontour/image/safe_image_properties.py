from morphocut import Node, Output, ReturnOutputs
import numpy as np
from morphocut.image import RegionProperties, RawOrVariable
from skimage.measure import label as sklabel
from scipy import ndimage as ndi


class DummyRegionProps:
    def __init__(self, shape):
        small = 1e-6

        self.area = 1
        self.perimeter = small
        self.filled_area = 1
        self.min_intensity = 0
        self.max_intensity = 0
        self.mean_intensity = 0
        self.image = np.zeros(shape, dtype=bool)
        self.bbox = (0, 0, 1, 1)
        self.bbox_area = 1
        self.centroid = (0.0, 0.0)
        self.equivalent_diameter = small
        self.major_axis_length = small
        self.minor_axis_length = small
        self.orientation = 0.0
        self.solidity = small
        self.extent = small
        self.eccentricity = small
        self.convex_area = 1
        self.image_filled = np.zeros(shape, dtype=bool)
        self.coords = np.empty((0, 2))
        self.label = -1
        self.euler_number = 0
        self.local_centroid = (0.0, 0.0)


@ReturnOutputs
@Output("regionprops")
class SafeImageProperties(Node):
    def __init__(self, mask: RawOrVariable, image: RawOrVariable = None):
        super().__init__()
        self.mask = mask
        self.image = image

    def transform(self, mask: np.ndarray, image: np.ndarray):
        binmask = (mask != 0)
        if not np.any(binmask):
            print("[WARNING] Empty mask — returning DummyRegionProps.")
            return DummyRegionProps(mask.shape)

        labels, nlabels = sklabel(binmask, return_num=True)

        if nlabels == 1:
            chosen_label = 1
        else:
            counts = np.bincount(labels.ravel())
            counts[0] = 0  # ignore background
            chosen_label = int(np.argmax(counts))

        obj_slices = ndi.find_objects(labels, nlabels)
        slices = obj_slices[chosen_label - 1]
        if slices is None:
            return DummyRegionProps(mask.shape)

        return RegionProperties(
            slices,
            chosen_label,
            labels,
            image,
            True,
        )