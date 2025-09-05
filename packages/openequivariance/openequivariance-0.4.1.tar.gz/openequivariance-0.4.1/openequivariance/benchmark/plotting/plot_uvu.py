import numpy as np
import matplotlib.pyplot as plt
import pathlib
from openequivariance.benchmark.plotting.plotting_utils import (
    set_grid,
    colormap,
    labelmap,
    grouped_barchart,
    load_benchmarks,
    filter_experiments,
)


def plot_uvu(data_folder):
    data_folder = pathlib.Path(data_folder)
    benchmarks, metadata = load_benchmarks(data_folder)
    configs = metadata["config_labels"]
    implementations = metadata["implementations"]

    for benchmark in benchmarks:
        if (
            benchmark["implementation_name"]
            == "E3NNTensorProductCompiledMaxAutotuneCUDAGraphs"
        ):
            benchmark["implementation_name"] = "E3NNTensorProduct"

    for i, implementation in enumerate(implementations):
        if implementation == "E3NNTensorProductCompiledMaxAutotuneCUDAGraphs":
            implementations[i] = "E3NNTensorProduct"

    def calculate_tp_per_sec(exp):
        return exp["benchmark results"]["batch_size"] / (
            np.mean(exp["benchmark results"]["time_millis"]) * 0.001
        )

    dataf32 = {"forward": {}, "backward": {}}
    for i, desc in enumerate(configs):
        for direction in ["forward", "backward"]:
            dataf32[direction][desc] = {}
            for impl in implementations:
                f32_benches = [
                    b
                    for b in benchmarks
                    if b["benchmark results"]["rep_dtype"] == "<class 'numpy.float32'>"
                ]
                exp = filter_experiments(
                    f32_benches,
                    {
                        "config_label": desc,
                        "direction": direction,
                        "implementation_name": impl,
                    },
                    match_one=True,
                )
                if exp is not None:
                    dataf32[direction][desc][labelmap[impl]] = calculate_tp_per_sec(exp)
                else:
                    dataf32[direction][desc][labelmap[impl]] = 0.0

    dataf64 = {"forward": {}, "backward": {}}
    for i, desc in enumerate(configs):
        for direction in ["forward", "backward"]:
            dataf64[direction][desc] = {}
            for impl in implementations:
                f64_benches = [
                    b
                    for b in benchmarks
                    if b["benchmark results"]["rep_dtype"] == "<class 'numpy.float64'>"
                ]
                exp = filter_experiments(
                    f64_benches,
                    {
                        "config_label": desc,
                        "direction": direction,
                        "implementation_name": impl,
                    },
                    match_one=True,
                )

                if exp is not None:
                    dataf64[direction][desc][labelmap[impl]] = calculate_tp_per_sec(exp)
                else:
                    dataf64[direction][desc][labelmap[impl]] = 0.0

    fig = plt.figure(figsize=(7, 7))
    gs = fig.add_gridspec(2, 2)
    axs = gs.subplots(sharex=True)

    grouped_barchart(
        dataf32["forward"],
        axs[0][0],
        bar_height_fontsize=0,
        xticklabel=False,
        colormap=colormap,
        group_spacing=6.0,
    )
    grouped_barchart(
        dataf32["backward"],
        axs[1][0],
        bar_height_fontsize=0,
        colormap=colormap,
        group_spacing=6.0,
    )

    grouped_barchart(
        dataf64["forward"],
        axs[0][1],
        bar_height_fontsize=0,
        xticklabel=False,
        colormap=colormap,
        group_spacing=6.0,
    )
    grouped_barchart(
        dataf64["backward"],
        axs[1][1],
        bar_height_fontsize=0,
        colormap=colormap,
        group_spacing=6.0,
    )

    for i in range(2):
        for j in range(2):
            set_grid(axs[i][j])
            set_grid(axs[i][j])

    axs[0][0].set_ylabel("Forward")
    axs[1][0].set_ylabel("Backward")

    handles, labels = axs[0][0].get_legend_handles_labels()
    unique = [
        (h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]
    ]
    axs[0][0].legend(*zip(*unique))

    fig.supylabel("Throughput (# tensor products / s)", x=0.036, y=0.605)

    axs[1][0].set_xlabel("float32")
    axs[1][1].set_xlabel("float64")

    fig.show()
    fig.tight_layout()
    fig.savefig(str(data_folder / "throughput_comparison.pdf"))

    speedup_table = []
    for direction in ["forward", "backward"]:
        for impl in ["e3nn", "cuE"]:
            for dtype_label, dtype_set in [("f32", dataf32), ("f64", dataf64)]:
                speedups = [
                    measurement["ours"] / measurement[impl]
                    for _, measurement in dtype_set[direction].items()
                    if impl in measurement
                ]
                stats = (
                    np.min(speedups),
                    np.mean(speedups),
                    np.median(speedups),
                    np.max(speedups),
                )
                stats = [f"{stat:.2f}" for stat in stats]

                dir_print = direction
                if direction == "forward":
                    dir_print += "  "
                result = [dir_print, impl, dtype_label] + stats
                speedup_table.append(result)

    print("\t\t".join(["Direction", "Base", "dtype", "min", "mean", "med", "max"]))
    for row in speedup_table:
        print("\t\t".join(row))
