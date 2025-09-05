import os
import logging
from typing import Optional, Callable

import boto3
from IPython.display import display, HTML

from .aws_utils import configure_aws_env, list_buckets, load_public_datasets
from .format_handlers import get_format_handler
from .ui_builder import build_widgets
from .events import connect_events

from .widgets.upload_widget import UploadWidget
from .widgets.s3_explorer_widget import S3ExplorerWidget
from .widgets.public_datasets_widget import PublicDatasetsWidget
from .widgets.metaspace_widget import MetaspaceDatasetsWidget

from .events import (
    _on_bench_toggle,
    _run_benchmark,
    _process_data,
    _on_tab_change,
)

logger = logging.getLogger(__name__)

class DataCockpit:
    def __init__(
        self,
        benchmarking_fn: Optional[Callable[[str, int], float]] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_region: str = "us-east-1",
    ) -> None:
        # Internal state
        self._data_slices = None
        self.ideal_batch_size: Optional[int] = None
        self.benchmark_fn = benchmarking_fn

        # AWS setup
        configure_aws_env(aws_access_key_id, aws_secret_access_key, aws_region)
        self.s3_client = boto3.client("s3", region_name=aws_region)

        # Load buckets & public datasets
        base_dir = os.path.dirname(__file__)
        self.buckets = list_buckets(self.s3_client)
        self.public_datasets = load_public_datasets(base_dir)

        # Instantiate sub-widgets and store them as attributes on self
        self.upload_w = UploadWidget(self.s3_client)
        self.upload_w.set_buckets(self.buckets)

        self.s3_explorer_w = S3ExplorerWidget(self.s3_client)
        self.s3_explorer_w.set_buckets(self.buckets)

        self.public_w = PublicDatasetsWidget(self.public_datasets)
        self.metaspace_w = MetaspaceDatasetsWidget()

        # Build UI components from those widget attributes
        widgets = build_widgets(
            self.upload_w,
            self.s3_explorer_w,
            self.public_w,
            self.metaspace_w,
        )
        # Inject all controls (bench_toggle, tabs, etc.) into self
        self.__dict__.update(widgets)

        # Wire up all event handlers (so _get_active_source can find self.upload_w, etc.)
        connect_events(self)

        # Render CSS + UI
        display(HTML(self._load_custom_css()))
        display(self._compose_main_ui())

    def _load_custom_css(self) -> str:
        """Read and wrap widget CSS in a <style> tag."""
        css_path = os.path.join(
            os.path.dirname(__file__),
            "utils", "widgets", "styles", "custom_styles.css",
        )
        if os.path.isfile(css_path):
            with open(css_path, "r") as f:
                return f"<style>{f.read()}</style>"
        return ""

    def _compose_main_ui(self):
        """Assemble the main UI VBox."""
        from ipywidgets import VBox
        return VBox([
            self.header_html(),
            self.bench_toggle,
            self.bench_box,
            self.tabs,
            self.ideal_bs_label,
            self.process_btn,
            self.process_output,
            self.progress,
        ], layout=dict(width="100%", padding="20px"))

    # ── Helpers for events ───────────────────────────────────────────────────────

    def _get_active_source(self):
        """Return (S3 URI, widget) of the active tab’s last selection."""
        for widget in (
            self.upload_w,
            self.s3_explorer_w,
            self.public_w,
            self.metaspace_w,
        ):
            for attr in ("last_s3_uri", "selected_uri", "s3_uri"):
                uri = getattr(widget, attr, None)
                if uri:
                    return uri, widget
        return None, None

    def _extract_ideal_bs(self) -> Optional[int]:
        """Parse the ideal batch size integer from the HTML label."""
        text = self.ideal_bs_label.value
        if "</strong>" in text:
            try:
                return int(text.split("</strong>")[-1])
            except ValueError:
                return None
        return None

    # ── Public API ───────────────────────────────────────────────────────────────

    def get_data_slices(self):
        """Return the most recent list of data slice objects."""
        return self._data_slices

    def get_batch_size(self) -> Optional[int]:
        """Return the currently active batch size."""
        if self.ideal_batch_size is not None:
            return self.ideal_batch_size
        _, widget = self._get_active_source()
        return getattr(widget, "get_batch_size", lambda: None)()


# ── Bind event handlers ───────────────────────────────────────────────────────────────

DataCockpit._on_bench_toggle = _on_bench_toggle
DataCockpit._run_benchmark   = _run_benchmark
DataCockpit._process_data    = _process_data
DataCockpit._on_tab_change   = _on_tab_change