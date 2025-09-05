import time
from typing import List
import numpy as np
import pandas as pd

from simba.utils.enums import Formats
from simba.utils.checks import check_valid_array, check_valid_dataframe, check_float
from simba.mixins.circular_statistics import CircularStatisticsMixin
from simba.mixins.train_model_mixin import TrainModelMixin
from numba import njit, typed
from simba.utils.read_write import find_files_of_filetypes_in_directory, read_df
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


# def two_point_direction(anterior_loc: np.ndarray, posterior_loc: np.ndarray)  -> np.ndarray:
#
#     """
#     Calculate directional angles between two body parts.
#
#     Computes frame-wise directional angles from posterior to anterior body parts (e.g., tail to nose, nape to head) using arctangent calculations.
#
#     It is a validated wrapper around the optimized numba implementation.
#
#     .. seealso::
#        For the underlying numba-accelerated implementation, see :func:`simba.mixins.circular_statistics.CircularStatisticsMixin.direction_two_bps`
#        For three-point direction calculation, see :func:`simba.mixins.circular_statistics.CircularStatisticsMixin.three_point_direction` or :func:`simba.mixins.circular_statistics.CircularStatisticsMixin.direction_three_bps`
#
#     .. csv-table::
#        :header: EXPECTED RUNTIMES
#        :file: ../../../docs/tables/two_point_direction.csv
#        :widths: 10, 45, 45
#        :align: center
#        :header-rows: 1
#
#     :param np.ndarray anterior_loc: 2D array with shape (n_frames, 2) containing [x, y] coordinates for the anterior body part (e.g., nose, head). Must contain non-negative numeric values.
#     :param np.ndarray posterior_loc : np.ndarray 2D array with shape (n_frames, 2) containing [x, y] coordinates for the posterior body part (e.g., tail base, nape). Must contain non-negative numeric values.
#     :return: 1D array with shape (n_frames,) containing directional angles in degrees [0, 360)  for each frame at type float32. Contains NaN values for frames where computation fails.
#     :rtype: np.ndarray
#     """
#
#     check_valid_array(data=anterior_loc, source=f'{two_point_direction.__name__} anterior_loc', accepted_ndims=(2,), accepted_dtypes=Formats.NUMERIC_DTYPES.value, min_value=0.0, raise_error=True, accepted_axis_1_shape=[2,])
#     check_valid_array(data=posterior_loc, source=f'{two_point_direction.__name__} posterior_loc', accepted_ndims=(2,), accepted_dtypes=Formats.NUMERIC_DTYPES.value, min_value=0.0, raise_error=True, accepted_axis_0_shape=(anterior_loc.shape[0],), accepted_axis_1_shape=[2,])
#     results = CircularStatisticsMixin().direction_two_bps(anterior_loc=anterior_loc.astype(np.float32), posterior_loc=posterior_loc.astype(np.float32))
#
#     return results

# def angle_to_cardinal(data: np.ndarray) -> List[str]:
#     """
#     Convert degree angles to cardinal direction bucket e.g., 0 -> "N", 180 -> "S"
#
#     .. note::
#        To convert cardinal literals to integers, map using :func:`simba.utils.enums.lookups.cardinality_to_integer_lookup`.
#        To convert integers to cardinal literals, map using :func:`simba.utils.enums.lookups.integer_to_cardinality_lookup`.
#
#     .. image:: _static/img/degrees_to_cardinal.png
#        :width: 600
#        :align: center
#
#     .. seealso::
#        For numba function, see func:`simba.mixins.circular_statistics.CircularStatisticsMixin.degrees_to_cardinal`
#        Appears to be quicker in pure numpy.
#
#     .. csv-table::
#        :header: EXPECTED RUNTIMES
#        :file: ../../../docs/tables/angle_to_cardinal.csv
#        :widths: 10, 45, 45
#        :align: center
#        :header-rows: 1
#
#     :param np.ndarray data: 1D array of degrees in range [0, 360).
#     :return: List of strings representing frame-wise cardinality.
#     :rtype: List[str]
#
#     :example:
#     >>> data = np.array(list(range(0, 405, 45))).astype(np.float32)
#     >>> CircularStatisticsMixin().angle_to_cardinal(data=data)
#     ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N']
#     """
#
#     check_valid_array(data=data, source=f'{angle_to_cardinal.__name__} angle_to_cardinal', accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value, min_value=0.0, max_value=360, raise_error=True)
#     DIRECTIONS = np.array(["N", "NE", "E", "SE", "S", "SW", "W", "NW"], dtype='<U2')
#     indices = np.round(data / 45.0).astype(int) % 8
#     return DIRECTIONS[indices].tolist()



def find_collinear_features(data: pd.DataFrame,
                            threshold: float) -> List[str]:

    """
    Identify collinear features in a pandas DataFrame for removal.

    Finds pairs of features with Pearson correlation coefficients above the specified threshold and returns the names of features that should be removed to reduce multicollinearity.

    Serves as a validation wrapper around numba implementation.

    .. seealso::
       For the underlying numba-accelerated implementation, see :func:`simba.mixins.train_model_mixin.TrainModelMixin.find_highly_correlated_fields`
       For non-numba statistical methods, see :func:`simba.mixins.statistics_mixin.Statistics.find_collinear_features`

    :param pd.DataFrame data: Input DataFrame containing numeric features. Each column represents a feature and each row represents an observation. Must contain only numeric data types.
    :param float threshold: Correlation threshold for identifying collinear features. Must be between 0.0 and 1.0. Higher values (e.g., 0.9) identify only very highly correlated features, while lower values  (e.g., 0.1) identify more loosely correlated features.
    :return: List of column names that are highly correlated with other features and should be considered for removal to reduce multicollinearity.
    :rtype: List[str]

    :example:
    >>> a = np.random.randint(0, 5, (1_000_000, size))
    >>> df = pd.DataFrame(a)
    >>> c = find_collinear_features(data=df, threshold=0.0025)
    """


    check_valid_dataframe(df=data, source=f'{find_collinear_features.__name__} data', valid_dtypes=Formats.NUMERIC_DTYPES.value, allow_duplicate_col_names=False)
    check_float(name=f'{find_collinear_features.__name__} threshold', value=threshold, min_value=0, max_value=1, raise_error=True)

    field_names = typed.List([str(x) for x in data.columns])

    x = TrainModelMixin.find_highly_correlated_fields(data=data.values.astype(np.float32),
                                                      threshold=np.float64(threshold),
                                                      field_names=field_names)
    return list(x)




sizes = [100, 200, 400, 800, 1600]
for size in sizes:
    times = []
    for i in range(1):
        a = np.random.randint(0, 5, (1_000_000, size))
        df = pd.DataFrame(a)
        start = time.time()
        c = find_collinear_features(data=df, threshold=0.0025)
        times.append(time.time() - start)
    print(size, '\t', np.mean(times), np.std(times))

# DATA_PATH = r"C:\troubleshooting\jax_examples\data"
# data_files = find_files_of_filetypes_in_directory(directory=DATA_PATH, extensions=['.csv'], as_dict=True)
# data = []
# for cnt, (video_name, video_path) in enumerate(data_files.items()):
#   print(f'Reading file {cnt+1} / {len(data_files.keys())}...')
#   df = read_df(file_path=video_path, file_type='csv')
#   data.append(df)
#
# data = pd.concat(data, axis=0)
# s = find_collinear_features(data=data, threshold=0.01)
#


sizes = [100] #, 1_000_000, 10_000_000, 20_000_000, 40_000_000, 80_000_000, 160_000_000]
#
# for size in sizes:
#     times = []
#     for i in range(1):
#         a = np.random.randint(0, 360, (size,))
# #         start = time.time()
# #         x = find_collinear_features(data=a)
# #         times.append(time.time() -start)
# #     print(size, '\t', np.mean(times), np.std(times))
# #
