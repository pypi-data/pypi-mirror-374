import os
from typing import Callable, Optional, Tuple, Dict

from dataplug.formats.generic.csv import CSV, partition_num_chunks as csv_partition
from dataplug.formats.geospatial.cog import (
    CloudOptimizedGeoTiff, grid_partition_strategy as cog_partitioner,
)
from dataplug.formats.geospatial.copc import (
    CloudOptimizedPointCloud, square_split_strategy as copc_partitioner,
)
from dataplug.formats.geospatial.laspc import (
    LiDARPointCloud, square_split_strategy as las_partitioner,
)
from dataplug.formats.genomics.fastq import FASTQGZip, partition_reads_batches
from dataplug.formats.genomics.fasta import FASTA, partition_chunks_strategy as fasta_partitioner
from dataplug.formats.genomics.vcf import VCF, partition_num_chunks as vcf_partitioner
from dataplug.formats.metabolomics.imzml import ImzML, partition_chunks_strategy as ibd_partitioner

FORMAT_MAP: Dict[str, Tuple] = {
    ".csv":   (CSV, csv_partition),
    ".fastq": (FASTQGZip, partition_reads_batches),
    ".gz":    (FASTQGZip, partition_reads_batches),
    ".fasta": (FASTA, fasta_partitioner),
    ".ibd":   (ImzML, ibd_partitioner),
    ".las":   (LiDARPointCloud, las_partitioner),
    ".laz":   (CloudOptimizedPointCloud, copc_partitioner),
    ".vcf":   (VCF, vcf_partitioner),
    ".tif":   (CloudOptimizedGeoTiff, cog_partitioner),
}

def get_format_handler(uri: str) -> Tuple[Optional[type], Optional[Callable]]:
    """Return (format class, partition fn) based on file extension."""
    ext = os.path.splitext(uri)[1].lower()
    return FORMAT_MAP.get(ext, (None, None))
