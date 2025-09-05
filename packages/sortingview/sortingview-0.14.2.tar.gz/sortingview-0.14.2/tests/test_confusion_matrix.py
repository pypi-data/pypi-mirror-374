# 8/24/22
# https://figurl.org/f?v=gs://figurl/spikesortingview-8&d=sha1://6f924d60a45e2800b6cfe198188d46a911313864&label=test_confusion_matrix

from typing import List
from tempfile import TemporaryDirectory
import spikeinterface as si
import spikeinterface.sorters as ss
import spikeinterface.comparison as sc
import spikeinterface.extractors as se
import kachery as ka
import sortingview.views as vv


def main():
    recording, _ = se.toy_example(num_units=12, num_channels=4, duration=200, seed=0, num_segments=1)
    with TemporaryDirectory() as tmpdir:
        sorter_params1 = {
            "detect_sign": -1,
            "adjacency_radius": -1,
            "freq_min": 300,
            "freq_max": 6000,
            "filter": True,
            "whiten": True,
            "num_workers": 4,
            "clip_size": 50,
            "detect_threshold": 3,
            "detect_interval": 10,
        }
        sorter_params2 = {**sorter_params1}
        sorter_params2["whiten"] = False
        R: si.BaseRecording = recording.save_to_folder(folder=tmpdir + "/recording")
        sortings = [
            ss.run_mountainsort4(
                recording=R,
                output_folder=f"{tmpdir}/output{i + 1}",
                remove_existing_folder=False,
                delete_output_folder=False,
                verbose=True,
                raise_error=True,
                docker_image=False,
                singularity_image=False,
                with_output=True,
                **sorter_params,
            )
            for i, sorter_params in enumerate([sorter_params1, sorter_params2])
        ]
        sorting1: si.BaseSorting = sortings[0]  # type: ignore
        sorting2: si.BaseSorting = sortings[1]  # type: ignore
        view = test_confusion_matrix(sorting1=sorting1, sorting2=sorting2)

        view_units_table = _create_units_table(sorting1=sorting1, sorting2=sorting2)

        view_composite = vv.Box(direction="horizontal", items=[vv.LayoutItem(view_units_table, max_size=200), vv.LayoutItem(view)])

        url = view_composite.url(label="test_confusion_matrix")
        print(url)


def _create_units_table(*, sorting1: si.BaseSorting, sorting2: si.BaseSorting):
    columns: List[vv.UnitsTableColumn] = []
    rows: List[vv.UnitsTableRow] = []
    for unit_id in sorting1.get_unit_ids():
        rows.append(vv.UnitsTableRow(unit_id=f"A{unit_id}", values={}))
    for unit_id in sorting2.get_unit_ids():
        rows.append(vv.UnitsTableRow(unit_id=f"B{unit_id}", values={}))
    return vv.UnitsTable(columns=columns, rows=rows)


def test_confusion_matrix(*, sorting1: si.BaseSorting, sorting2: si.BaseSorting):
    SC: sc.SymmetricSortingComparison = sc.compare_two_sorters(sorting1=sorting1, sorting2=sorting2)

    unit_event_counts: List[vv.UnitEventCount] = []
    for unit_id in sorting1.unit_ids:
        unit_event_counts.append(vv.UnitEventCount(unit_id=f"A{unit_id}", count=len(sorting1.get_unit_spike_train(unit_id))))
    for unit_id in sorting2.unit_ids:
        unit_event_counts.append(vv.UnitEventCount(unit_id=f"B{unit_id}", count=len(sorting2.get_unit_spike_train(unit_id))))

    matching_unit_event_counts: List[vv.MatchingUnitEventCount] = []
    for id1 in sorting1.unit_ids:
        ids2 = SC.get_matching_unit_list1(id1)
        for id2 in ids2:
            count = SC.get_matching_event_count(id1, id2)
            matching_unit_event_counts.append(vv.MatchingUnitEventCount(unit_id1=f"A{id1}", unit_id2=f"B{id2}", count=count))

    view = vv.ConfusionMatrix(
        sorting1_unit_ids=[f"A{id}" for id in sorting1.unit_ids],
        sorting2_unit_ids=[f"B{id}" for id in sorting2.unit_ids],
        unit_event_counts=unit_event_counts,
        matching_unit_event_counts=matching_unit_event_counts,
    )
    return view


if __name__ == "__main__":
    main()
