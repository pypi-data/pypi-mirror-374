from typing import Tuple, Union
from tempfile import TemporaryDirectory
import json
import math
import numpy as np
import h5py
import hashlib
import spikeinterface as si
import kachery as ka
import spikeinterface.preprocessing as spre


def prepare_spikesortingview_data(
    *,
    recording: si.BaseRecording,
    sorting: si.BaseSorting,
    segment_duration_sec: float,
    snippet_len: Tuple[int, int],
    max_num_snippets_per_segment: Union[int, None],
    channel_neighborhood_size: int,
    bandpass_filter: bool = False,
) -> str:
    # NOTE(DS): for data longer than 25hours with fs = 20000; num_frame is too large for int32
    if recording.get_num_frames() > (2**31 - 1):
        int_type = np.int64
    else:
        int_type = np.int32
        # int_type = np.int64 #NOTE(DS): to test in short recording

    print(f"int_type: {int_type}")

    if bandpass_filter:
        recording = spre.bandpass_filter(recording)
    unit_ids = np.array(sorting.get_unit_ids()).astype(np.int32)
    channel_ids = np.array(recording.get_channel_ids()).astype(np.int32)
    sampling_frequency = recording.get_sampling_frequency()
    num_frames = recording.get_num_frames()
    num_frames_per_segment = math.ceil(segment_duration_sec * sampling_frequency)
    num_segments = math.ceil(num_frames / num_frames_per_segment)
    if hasattr(recording, "has_scaleable_traces") and callable(getattr(recording, "has_scaleable_traces")):
        scalable = recording.has_scaleable_traces()
    elif hasattr(recording, "has_scaled") and callable(getattr(recording, "has_scaled")):
        scalable = recording.has_scaled()
    else:
        scalable = False

    with TemporaryDirectory() as tmpdir:
        output_file_name = tmpdir + "/spikesortingview.h5"
        with h5py.File(output_file_name, "w") as f:
            f.create_dataset("unit_ids", data=unit_ids)
            f.create_dataset(
                "sampling_frequency",
                data=np.array([sampling_frequency]).astype(np.float32),
            )
            f.create_dataset("channel_ids", data=channel_ids)
            f.create_dataset("num_frames", data=np.array([num_frames]).astype(int_type))
            channel_locations = recording.get_channel_locations()
            f.create_dataset("channel_locations", data=np.array(channel_locations))
            f.create_dataset("num_segments", data=np.array([num_segments]).astype(np.int32))
            f.create_dataset(
                "num_frames_per_segment",
                data=np.array([num_frames_per_segment]).astype(np.int32),
            )
            f.create_dataset(
                "snippet_len",
                data=np.array([snippet_len[0], snippet_len[1]]).astype(np.int32),
            )
            f.create_dataset(
                "max_num_snippets_per_segment",
                data=np.array([max_num_snippets_per_segment]).astype(np.int32),
            )
            f.create_dataset(
                "channel_neighborhood_size",
                data=np.array([channel_neighborhood_size]).astype(np.int32),
            )

            # first get peak channels and channel neighborhoods
            unit_peak_channel_ids = {}
            fallback_unit_peak_channel_ids = {}
            unit_channel_neighborhoods = {}
            for iseg in range(num_segments):
                something_missing = False
                for unit_id in unit_ids:
                    if str(unit_id) not in unit_peak_channel_ids:
                        something_missing = True
                if not something_missing:
                    break
                print(f"Initial pass: segment {iseg}")
                start_frame = iseg * num_frames_per_segment
                end_frame = min(start_frame + num_frames_per_segment, num_frames)
                start_frame_with_padding = max(start_frame - snippet_len[0], 0)
                end_frame_with_padding = min(end_frame + snippet_len[1], num_frames)
                traces_with_padding = recording.get_traces(
                    start_frame=start_frame_with_padding,
                    end_frame=end_frame_with_padding,
                    return_scaled=scalable,
                )
                assert isinstance(traces_with_padding, np.ndarray)
                for unit_id in unit_ids:
                    if str(unit_id) not in unit_peak_channel_ids:
                        spike_train = sorting.get_unit_spike_train(
                            unit_id=unit_id,
                            start_frame=start_frame,
                            end_frame=end_frame,
                        )
                        assert isinstance(spike_train, np.ndarray)
                        if len(spike_train) > 0:
                            values = traces_with_padding[spike_train - start_frame_with_padding, :].astype(np.int32)
                            avg_value = np.mean(values, axis=0)
                            peak_channel_ind = np.argmax(np.abs(avg_value))
                            peak_channel_id = channel_ids[peak_channel_ind]
                            channel_neighborhood = get_channel_neighborhood(
                                channel_ids=channel_ids,
                                channel_locations=channel_locations,
                                peak_channel_id=peak_channel_id,
                                channel_neighborhood_size=channel_neighborhood_size,
                            )
                            if len(spike_train) >= 10:
                                unit_peak_channel_ids[str(unit_id)] = peak_channel_id
                            else:
                                fallback_unit_peak_channel_ids[str(unit_id)] = peak_channel_id
                            unit_channel_neighborhoods[str(unit_id)] = channel_neighborhood
            for unit_id in unit_ids:
                peak_channel_id = unit_peak_channel_ids.get(str(unit_id), None)
                if peak_channel_id is None:
                    peak_channel_id = fallback_unit_peak_channel_ids.get(str(unit_id), None)
                if peak_channel_id is None:
                    raise Exception(f"Peak channel not found for unit {unit_id}. This is probably because no spikes were found in any segment for this unit.")
                channel_neighborhood = unit_channel_neighborhoods[str(unit_id)]
                f.create_dataset(
                    f"unit/{unit_id}/peak_channel_id",
                    data=np.array([peak_channel_id]).astype(np.int32),
                )
                f.create_dataset(
                    f"unit/{unit_id}/channel_neighborhood",
                    data=np.array(channel_neighborhood).astype(np.int32),
                )

            for iseg in range(num_segments):
                print(f"Segment {iseg} of {num_segments}")
                start_frame = iseg * num_frames_per_segment
                end_frame = min(start_frame + num_frames_per_segment, num_frames)
                start_frame_with_padding = max(start_frame - snippet_len[0], 0)
                end_frame_with_padding = min(end_frame + snippet_len[1], num_frames)
                traces_with_padding = recording.get_traces(
                    start_frame=start_frame_with_padding,
                    end_frame=end_frame_with_padding,
                    return_scaled=scalable,
                )
                traces_sample = traces_with_padding[
                    start_frame - start_frame_with_padding : start_frame - start_frame_with_padding + int(sampling_frequency * 1),
                    :,
                ]
                f.create_dataset(f"segment/{iseg}/traces_sample", data=traces_sample)
                all_subsampled_spike_trains = []
                for unit_id in unit_ids:
                    peak_channel_id = unit_peak_channel_ids.get(str(unit_id), None)
                    if peak_channel_id is None:
                        peak_channel_id = fallback_unit_peak_channel_ids.get(str(unit_id), None)
                    if peak_channel_id is None:
                        raise Exception(f"Peak channel not found for unit {unit_id}. This is probably because no spikes were found in any segment for this unit.")
                    spike_train = sorting.get_unit_spike_train(unit_id=unit_id, start_frame=start_frame, end_frame=end_frame).astype(int_type)
                    f.create_dataset(f"segment/{iseg}/unit/{unit_id}/spike_train", data=spike_train)
                    channel_neighborhood = unit_channel_neighborhoods[str(unit_id)]
                    peak_channel_ind = channel_ids.tolist().index(peak_channel_id)
                    if len(spike_train) > 0:
                        spike_amplitudes = traces_with_padding[spike_train - start_frame_with_padding, peak_channel_ind]
                        f.create_dataset(
                            f"segment/{iseg}/unit/{unit_id}/spike_amplitudes",
                            data=spike_amplitudes,
                        )
                    else:
                        spike_amplitudes = np.array([], dtype=np.int32)
                    if max_num_snippets_per_segment is not None and len(spike_train) > max_num_snippets_per_segment:
                        subsampled_spike_train = subsample(spike_train, max_num_snippets_per_segment)
                    else:
                        subsampled_spike_train = spike_train
                    f.create_dataset(
                        f"segment/{iseg}/unit/{unit_id}/subsampled_spike_train",
                        data=subsampled_spike_train,
                    )
                    all_subsampled_spike_trains.append(subsampled_spike_train)
                subsampled_spike_trains_concat = np.concatenate(all_subsampled_spike_trains)
                # print('Extracting spike snippets')
                spike_snippets_concat = extract_spike_snippets(
                    traces=traces_with_padding,
                    times=subsampled_spike_trains_concat - start_frame_with_padding,
                    snippet_len=snippet_len,
                )
                # print('Collecting spike snippets')
                index = 0
                for ii, unit_id in enumerate(unit_ids):
                    channel_neighborhood = unit_channel_neighborhoods[str(unit_id)]
                    channel_neighborhood_indices = [channel_ids.tolist().index(ch_id) for ch_id in channel_neighborhood]
                    num = len(all_subsampled_spike_trains[ii])
                    spike_snippets = spike_snippets_concat[index : index + num, :, channel_neighborhood_indices]
                    index = index + num
                    f.create_dataset(
                        f"segment/{iseg}/unit/{unit_id}/subsampled_spike_snippets",
                        data=spike_snippets,
                    )
        uri = ka.store_file_local(output_file_name)
        return uri


def get_channel_neighborhood(
    *,
    channel_ids: np.ndarray,
    channel_locations: np.ndarray,
    peak_channel_id: int,
    channel_neighborhood_size: int,
):
    channel_locations_by_id = {}
    for ii, channel_id in enumerate(channel_ids):
        channel_locations_by_id[channel_id] = channel_locations[ii]
    peak_location = channel_locations_by_id[int(peak_channel_id)]
    distances = []
    for channel_id in channel_ids:
        loc = channel_locations_by_id[int(channel_id)]
        dist = np.linalg.norm(np.array(loc) - np.array(peak_location))
        distances.append(dist)
    sorted_indices = np.argsort(distances)
    neighborhood_channel_ids = []
    for ii in range(min(channel_neighborhood_size, len(channel_ids))):
        neighborhood_channel_ids.append(int(channel_ids[sorted_indices[ii]]))
    return neighborhood_channel_ids


def subsample(x: np.ndarray, num: int):
    if num >= len(x):
        return x
    stride = math.floor(len(x) / num)
    return x[0 : stride * num : stride]


def extract_spike_snippets(*, traces: np.ndarray, times: np.ndarray, snippet_len: Tuple[int, int]):
    a = snippet_len[0]
    b = snippet_len[1]
    T = a + b
    M = traces.shape[1]
    L = len(times)
    ret = np.zeros((L, T, M), dtype=traces.dtype)
    if L > 0:
        for t in range(T):
            valid_inds = np.where(times < traces.shape[0] - b)
            ret[valid_inds, t, :] = traces[times[valid_inds] - a + t, :]
    return ret


def _sha1_of_string(txt: str) -> str:
    hh = hashlib.sha1(txt.encode("utf-8"))
    ret = hh.hexdigest()
    return ret


def _sha1_of_object(obj: object) -> str:
    txt = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return _sha1_of_string(txt)
