import time

import numpy as np
from simba.utils.enums import Formats
from simba.utils.checks import check_valid_array
from simba.mixins.circular_statistics import CircularStatisticsMixin

# def three_point_direction(nose_loc: np.ndarray,
#                           left_ear_loc: np.ndarray,
#                           right_ear_loc: np.ndarray)  -> np.ndarray:
#     """
#     Calculate animal heading direction using three anatomical landmarks with input validation.
#
#     Computes the mean directional angle of an animal based on nose and ear coordinates
#     using circular statistics. Provides a robust estimate of the animal's facing direction by calculating individual directional vectors from each ear to the nose, then computing their
#     circular mean to handle angular discontinuities properly.
#
#     The function serves as a validated wrapper around the underlying numba-accelerated implementation, ensuring input data meets requirements before computation.
#
#     .. seealso::
#        For the underlying numba-accelerated implementation, see :func:`simba.mixins.circular_statistics.CircularStatisticsMixin.direction_three_bps`.
#        For two-point direction calculation, see :func:`simba.mixins.circular_statistics.CircularStatisticsMixin.direction_two_bps`.
#
#     .. image:: _static/img/angle_from_3_bps.png
#        :width: 600
#        :align: center
#
#     .. csv-table::
#        :header: EXPECTED RUNTIMES
#        :file: ../../../docs/tables/three_point_direction.csv
#        :widths: 10, 45, 45
#        :align: center
#        :header-rows: 1
#
#     :param np.ndarray nose_loc: 2D array with shape (n_frames, 2) containing [x, y] pixel coordinates  of the nose for each frame. Must contain non-negative numeric values.
#     :param np.ndarray left_ear_loc: 2D array with shape (n_frames, 2) containing [x, y] pixel coordinates  of the left ear for each frame. Must have the same number of frames as nose_loc.
#     :param np.ndarray right_ear_loc: 2D array with shape (n_frames, 2) containing [x, y] pixel coordinates of the right ear for each frame. Must have the same number of frames as nose_loc.
#     :return: 1D array with shape (n_frames,) containing directional angles in degrees [0, 360)  for each frame. Contains NaN values for frames where computation fails.
#     :rtype: np.ndarray
#
#     :example:
#     >>> nose_loc = np.array([[100, 150], [102, 148], [105, 145]], dtype=np.float32)
#     >>> left_ear_loc = np.array([[95, 160], [97, 158], [100, 155]], dtype=np.float32)
#     >>> right_ear_loc = np.array([[105, 160], [107, 158], [110, 155]], dtype=np.float32)
#     >>> directions = CircularStatisticsMixin.direction_three_bps( nose_loc=nose_loc, left_ear_loc=left_ear_loc, right_ear_loc=right_ear_loc)
#     """
#
#     check_valid_array(data=nose_loc, source=f'{three_point_direction.__name__} nose_loc', accepted_ndims=(2,), accepted_dtypes=Formats.NUMERIC_DTYPES.value, min_value=0.0, raise_error=True)
#     check_valid_array(data=left_ear_loc, source=f'{three_point_direction.__name__} left_ear_loc', accepted_ndims=(2,), accepted_dtypes=Formats.NUMERIC_DTYPES.value, min_value=0.0, raise_error=True, accepted_axis_0_shape=(nose_loc.shape[0],))
#     check_valid_array(data=right_ear_loc, source=f'{three_point_direction.__name__} right_ear_loc', accepted_ndims=(2,), accepted_dtypes=Formats.NUMERIC_DTYPES.value, min_value=0.0, raise_error=True, accepted_axis_0_shape=(right_ear_loc.shape[0],))
#
#     results = CircularStatisticsMixin().direction_three_bps(nose_loc=nose_loc.astype(np.float32),
#                                                             left_ear_loc=left_ear_loc.astype(np.float32),
#                                                             right_ear_loc=right_ear_loc.astype(np.float32))
#     return results
#
#


def two_point_direction(anterior_loc: np.ndarray, posterior_loc: np.ndarray)  -> np.ndarray:

    """
    Calculate directional angles between two body parts.

    Computes frame-wise directional angles from posterior to anterior body parts (e.g., tail to nose, nape to head) using arctangent calculations.

    It is a validated wrapper around the optimized numba implementation.

    .. seealso::
       For the underlying numba-accelerated implementation, see :func:`simba.mixins.circular_statistics.CircularStatisticsMixin.direction_two_bps`
       For three-point direction calculation, see :func:`simba.mixins.circular_statistics.CircularStatisticsMixin.three_point_direction` or :func:`simba.mixins.circular_statistics.CircularStatisticsMixin.direction_three_bps`

    .. csv-table::
       :header: EXPECTED RUNTIMES
       :file: ../../../docs/tables/two_point_direction.csv
       :widths: 10, 45, 45
       :align: center
       :header-rows: 1

    :param np.ndarray anterior_loc: 2D array with shape (n_frames, 2) containing [x, y] coordinates for the anterior body part (e.g., nose, head). Must contain non-negative numeric values.
    :param np.ndarray posterior_loc : np.ndarray 2D array with shape (n_frames, 2) containing [x, y] coordinates for the posterior body part (e.g., tail base, nape). Must contain non-negative numeric values.
    :return: 1D array with shape (n_frames,) containing directional angles in degrees [0, 360)  for each frame at type float32. Contains NaN values for frames where computation fails.
    :rtype: np.ndarray
    """

    check_valid_array(data=anterior_loc, source=f'{two_point_direction.__name__} anterior_loc', accepted_ndims=(2,), accepted_dtypes=Formats.NUMERIC_DTYPES.value, min_value=0.0, raise_error=True, accepted_axis_1_shape=[2,])
    check_valid_array(data=posterior_loc, source=f'{two_point_direction.__name__} posterior_loc', accepted_ndims=(2,), accepted_dtypes=Formats.NUMERIC_DTYPES.value, min_value=0.0, raise_error=True, accepted_axis_0_shape=(anterior_loc.shape[0],), accepted_axis_1_shape=[2,])
    results = CircularStatisticsMixin().direction_two_bps(anterior_loc=anterior_loc.astype(np.float32), posterior_loc=posterior_loc.astype(np.float32))

    return results


sizes = [500000, 1_000_000, 5_000_000, 10_000_000, 20_000_000, 40_000_000, 80_000_000, 120_000_000, 160_000_000, 240_000_000]

for size in sizes:
    times = []
    for i in range(3):
        a = np.random.randint(0, 500, (size, 2))
        b = np.random.randint(0, 500, (size, 2))
        start = time.time()
        two_point_direction(anterior_loc=a, posterior_loc=b)
        times.append(time.time() -start)
    print(size, '\t', np.mean(times), np.std(times))



