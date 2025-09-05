# dataplug_ui/ui_builder.py

from ipywidgets import (
    ToggleButtons, BoundedIntText, Button, Output,
    IntProgress, HTML, GridspecLayout, VBox, Tab,
)

def build_widgets(
    upload_w, s3_explorer_w, public_w, metaspace_w
) -> dict:
    """
    Instantiate all sub-widgets and controls, return a dict with them.
    """
    # Benchmark controls
    bench_toggle = ToggleButtons(
        options=["Disabled", "Enabled"],
        value="Disabled",
        description="Benchmarking:",
        layout=dict(width="auto"),
    )
    min_bs = BoundedIntText(value=1, min=1, max=1_000_000, description="Min:")
    max_bs = BoundedIntText(value=100, min=1, max=1_000_000, description="Max:")
    step_bs = BoundedIntText(value=10, min=1, max=1_000_000, description="Step:")

    grid = GridspecLayout(3, 2)
    grid[0, 0] = HTML("<strong>Min Batch:</strong>")
    grid[0, 1] = min_bs
    grid[1, 0] = HTML("<strong>Max Batch:</strong>")
    grid[1, 1] = max_bs
    grid[2, 0] = HTML("<strong>Step:</strong>")
    grid[2, 1] = step_bs

    run_bench_btn = Button(
        description="Run Benchmark",
        button_style="warning",
        icon="play",
        layout=dict(width="200px", margin="10px auto"),
    )
    bench_output = Output()
    bench_box = VBox([grid, run_bench_btn, bench_output])
    bench_box.layout.display = "none"

    # Processing controls
    process_btn = Button(
        description="Process Data",
        button_style="primary",
        icon="cogs",
        layout=dict(width="200px", margin="10px auto"),
    )
    process_output = Output()
    progress = IntProgress(value=0, min=0, max=100, description="Decoding:")
    progress.layout.display = "none"
    ideal_bs_label = HTML("<strong>Ideal Batch Size:</strong> Not set.")

    # Tabs container
    tabs = Tab(
        children=[
            upload_w.get_widget(),
            s3_explorer_w.get_widget(),
            public_w.get_widget(),
            metaspace_w.get_widget(),
        ]
    )
    for idx, title in enumerate(["Upload", "S3 Explorer", "Public", "Metaspace"]):
        tabs.set_title(idx, title)

    def header_html():
        # Now return an ipywidgets HTML widget
        return HTML(
            '<div style="text-align:center;margin-bottom:20px;">'
            '<h1 style="color:#2C3E50;"><i class="fa fa-database"></i> Data Cockpit</h1>'
            '<p style="color:#7F8C8D;">Manage and explore your data efficiently</p>'
            '</div>'
        )

    return {
        "bench_toggle": bench_toggle,
        "min_bs": min_bs,
        "max_bs": max_bs,
        "step_bs": step_bs,
        "run_bench_btn": run_bench_btn,
        "bench_output": bench_output,
        "bench_box": bench_box,
        "process_btn": process_btn,
        "process_output": process_output,
        "progress": progress,
        "ideal_bs_label": ideal_bs_label,
        "tabs": tabs,
        "header_html": header_html,
    }
