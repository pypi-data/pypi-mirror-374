# Data Cockpit

**Data Cockpit** is an interactive IPython widget built on top of the [Dataplug](https://github.com/dataplug/dataplug) framework. It enables scientists and engineers to:

- **Upload** and browse datasets in Amazon S3  
- **Explore** curated public and Metaspace collections  
- **Benchmark** performance to discover optimal batch sizes  
- **Partition** a variety of scientific data types into chunks or batches  
- **Integrate** seamlessly into Jupyter notebooks for elastic, parallel workloads  

---

## Why Data Cockpit?

### Built on Dataplug’s Cloud-Aware Partitioning

Dataplug is a client-side Python framework for **dynamic, zero-cost data slicing** of unstructured scientific data stored in object stores like S3. It:

- **Pre-processes** data in a read-only fashion, building lightweight indexes decoupled from the raw objects  
- **Exploits** S3 byte-range reads to parallelize high-bandwidth access across many workers  
- **Supports** a plug-in interface for multiple domains:  
  - **Generic**: CSV, raw text  
  - **Genomics**: FASTA, FASTQ, VCF  
  - **Geospatial**: LiDAR, Cloud-Optimized Point Cloud (COPC), COG  
  - **Metabolomics**: ImzML  
- **Allows** re-partitioning with different strategies without rewriting the original data  

### What Data Cockpit Adds

While Dataplug focuses on efficient data slicing, Data Cockpit provides an **end-to-end Jupyter UI** that:

1. **Uploads** your local files directly into any S3 bucket  
2. **Browses** existing buckets or public datasets from the AWS Open Data Registry  
3. **Runs benchmarks** across a configurable range of batch sizes to find the fastest throughput  
4. **Processes & partitions** your data with one click, displaying progress and results entirely in-notebook  
5. **Retrieves** partitions via `get_data_slices()`, which returns the DataPlug data slices (metadata) for downstream processing  

---

## Installation

```bash
pip install cloud-data-cockpit
```

Or install both Data Cockpit and geospatial extras together:

```bash
pip install cloud-data-cockpit[geospatial]  
```
