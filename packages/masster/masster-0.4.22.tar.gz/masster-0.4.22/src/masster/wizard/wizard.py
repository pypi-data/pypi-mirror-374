"""
Wizard module for automated processing of mass spectrometry studies.

This module provides the Wizard class for fully automated processing of MS data
from raw files to final study results, including batch conversion, assembly,
alignment, merging, plotting, and export.

Key Features:
- Automated discovery and batch conversion of raw data files
- Intelligent resume capability for interrupted processes
- Parallel processing optimization for large datasets
- Adaptive study format based on study size
- Comprehensive logging and progress tracking
- Optimized memory management for large studies

Classes:
- Wizard: Main class for automated study processing
- wizard_def: Default parameters configuration class

Example Usage:
```python
from masster import Wizard, wizard_def

# Create wizard with default parameters
wizard = Wizard(
    source="./raw_data",
    folder="./processed_study",
    polarity="positive",
    num_cores=4
)

```
"""

from __future__ import annotations

import os
import sys
import time
import importlib
import glob
import multiprocessing
from pathlib import Path
from typing import Optional, Any, Dict, List
from dataclasses import dataclass, field
import concurrent.futures
from datetime import datetime

# Import masster modules - use delayed import to avoid circular dependencies
from masster.logger import MassterLogger
from masster.study.defaults.study_def import study_defaults
from masster.study.defaults.align_def import align_defaults
from masster.study.defaults.merge_def import merge_defaults
from masster._version import __version__ as version


@dataclass
class wizard_def:
    """
    Default parameters for the Wizard automated processing system.
    
    This class provides comprehensive configuration for all stages of automated
    mass spectrometry data processing from raw files to final results.
    
    Attributes:
        # Core Configuration
        source (str): Path to directory containing raw data files
        folder (str): Output directory for processed study
        polarity (str): Ion polarity mode ("positive" or "negative")
        num_cores (int): Number of CPU cores to use for parallel processing
        
        # File Discovery
        file_extensions (List[str]): File extensions to search for
        search_subfolders (bool): Whether to search subdirectories
        skip_patterns (List[str]): Filename patterns to skip
        
        # Processing Parameters
        adducts (List[str]): Adduct specifications for given polarity
        batch_size (int): Number of files to process per batch
        memory_limit_gb (float): Memory limit for processing (GB)
        
        # Resume & Recovery
        resume_enabled (bool): Enable automatic resume capability
        force_reprocess (bool): Force reprocessing of existing files
        backup_enabled (bool): Create backups of intermediate results
        
        # Output & Export
        generate_plots (bool): Generate visualization plots
        export_formats (List[str]): Output formats to generate
        compress_output (bool): Compress final study file
        
        # Logging
        log_level (str): Logging detail level
        log_to_file (bool): Save logs to file
        progress_interval (int): Progress update interval (seconds)
    """
    
    # === Core Configuration ===
    source: str = ""
    folder: str = ""  
    polarity: str = "positive"
    num_cores: int = 4
    
    # === File Discovery ===
    file_extensions: List[str] = field(default_factory=lambda: [".wiff", ".raw", ".mzML"])
    search_subfolders: bool = True
    skip_patterns: List[str] = field(default_factory=lambda: ["blank", "test"])
    
    # === Processing Parameters ===
    adducts: List[str] = field(default_factory=list)  # Will be set based on polarity
    batch_size: int = 8
    memory_limit_gb: float = 16.0
    max_file_size_gb: float = 4.0
    
    # === Resume & Recovery ===
    resume_enabled: bool = True
    force_reprocess: bool = False
    backup_enabled: bool = True
    checkpoint_interval: int = 10  # Save progress every N files
    
    # === Study Assembly ===
    min_samples_for_merge: int = 2
    rt_tolerance: float = 1.5
    mz_max_diff: float = 0.01
    alignment_algorithm: str = "kd"
    merge_method: str = "qt"
    
    # === Feature Detection ===
    chrom_fwhm: float = 0.5
    noise: float = 50.0
    chrom_peak_snr: float = 5.0
    tol_ppm: float = 10.0
    detector_type: str = "unknown"  # Detected detector type ("orbitrap", "quadrupole", "unknown")
    
    # === Output & Export ===
    generate_plots: bool = True
    generate_interactive: bool = True
    export_formats: List[str] = field(default_factory=lambda: ["csv", "mgf", "xlsx"])
    compress_output: bool = True
    adaptive_compression: bool = True  # Adapt based on study size
    
    # === Logging ===
    log_level: str = "INFO"
    log_to_file: bool = True
    progress_interval: int = 30  # seconds
    verbose_progress: bool = True
    
    # === Advanced Options ===
    use_process_pool: bool = True  # vs ThreadPoolExecutor
    optimize_memory: bool = True
    cleanup_temp_files: bool = True
    validate_outputs: bool = True
        
    _param_metadata: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "source": {
                "dtype": str,
                "description": "Path to directory containing raw data files",
                "required": True,
            },
            "folder": {
                "dtype": str, 
                "description": "Output directory for processed study",
                "required": True,
            },
            "polarity": {
                "dtype": str,
                "description": "Ion polarity mode",
                "default": "positive",
                "allowed_values": ["positive", "negative", "pos", "neg"],
            },
            "num_cores": {
                "dtype": int,
                "description": "Number of CPU cores to use",
                "default": 4,
                "min_value": 1,
                "max_value": multiprocessing.cpu_count(),
            },
            "batch_size": {
                "dtype": int,
                "description": "Number of files to process per batch",
                "default": 8,
                "min_value": 1,
                "max_value": 32,
            },
            "memory_limit_gb": {
                "dtype": float,
                "description": "Memory limit for processing (GB)",
                "default": 16.0,
                "min_value": 1.0,
                "max_value": 128.0,
            },
        },
        repr=False,
    )
    
    def __post_init__(self):
        """Set polarity-specific defaults after initialization."""
        # Set default adducts based on polarity if not provided
        if not self.adducts:
            if self.polarity.lower() in ["positive", "pos"]:
                self.adducts = ["H:+:0.8", "Na:+:0.1", "NH4:+:0.1"]
            elif self.polarity.lower() in ["negative", "neg"]: 
                self.adducts = ["H-1:-:1.0", "CH2O2:0:0.5"]
            else:
                # Default to positive
                self.adducts = ["H:+:0.8", "Na:+:0.1", "NH4:+:0.1"]
        
        # Validate num_cores
        max_cores = multiprocessing.cpu_count()
        if self.num_cores <= 0:
            self.num_cores = max_cores
        elif self.num_cores > max_cores:
            self.num_cores = max_cores
            
        # Ensure paths are absolute
        if self.source:
            self.source = os.path.abspath(self.source)
        if self.folder:
            self.folder = os.path.abspath(self.folder)


class Wizard:
    """
    Simplified Wizard for automated mass spectrometry data processing.
    
    The Wizard provides a clean interface for creating and executing analysis scripts
    that process raw MS data through the complete pipeline: file discovery, feature
    detection, sample processing, study assembly, alignment, merging, and export.
    
    This simplified version focuses on two core functions:
    - create_script(): Generate standalone analysis scripts
    - execute(): Create and run analysis scripts
    """
    
    def __init__(
        self,
        source: str = "",
        folder: str = "",
        polarity: str = "positive",
        adducts: Optional[List[str]] = None,
        num_cores: int = 0,
        **kwargs
    ):
        """
        Initialize the Wizard with analysis parameters.
        
        Parameters:
            source: Directory containing raw data files
            folder: Output directory for processed study
            polarity: Ion polarity mode ("positive" or "negative")
            adducts: List of adduct specifications (auto-set if None)
            num_cores: Number of CPU cores (0 = auto-detect 75% of available)
            **kwargs: Additional parameters (see wizard_def for full list)
        """
        
        # Auto-detect optimal number of cores if not specified
        if num_cores <= 0:
            num_cores = max(1, int(multiprocessing.cpu_count() * 0.75))
            
        # Create parameters instance
        if "params" in kwargs and isinstance(kwargs["params"], wizard_def):
            self.params = kwargs.pop("params")
        else:
            # Create default parameters
            self.params = wizard_def(
                source=source,
                folder=folder,
                polarity=polarity,
                num_cores=num_cores
            )
            
            # Set adducts if provided
            if adducts is not None:
                self.params.adducts = adducts
            
            # Update with any additional parameters
            for key, value in kwargs.items():
                if hasattr(self.params, key):
                    setattr(self.params, key, value)
        
        # Validate required parameters
        if not self.params.source:
            raise ValueError("source is required")
        if not self.params.folder:
            raise ValueError("folder is required")
        
        # Create and validate paths
        self.source_path = Path(self.params.source)
        self.folder_path = Path(self.params.folder) 
        self.folder_path.mkdir(parents=True, exist_ok=True)
        
        # Auto-infer polarity from the first file if not explicitly set by user
        if polarity == "positive" and "polarity" not in kwargs:
            inferred_polarity = self._infer_polarity_from_first_file()
            if inferred_polarity:
                self.params.polarity = inferred_polarity
                # Update adducts based on inferred polarity  
                self.params.__post_init__()

    def _infer_polarity_from_first_file(self) -> str:
        """
        Infer polarity from the first available raw data file.
        
        Returns:
            Inferred polarity string ("positive" or "negative") or None if detection fails
        """
        try:
            # Find first file
            for extension in ['.wiff', '.raw', '.mzML']:
                pattern = f"**/*{extension}" if True else f"*{extension}"  # search_subfolders=True
                files = list(self.source_path.rglob(pattern))
                if files:
                    first_file = files[0]
                    break
            else:
                return 'positive'

            # Only implement for .wiff files initially (most common format)
            if first_file.suffix.lower() == '.wiff':
                from masster.sample.load import _wiff_to_dict
                
                # Extract metadata from first file
                metadata_df = _wiff_to_dict(str(first_file))
                
                if not metadata_df.empty and 'polarity' in metadata_df.columns:
                    # Get polarity from first experiment  
                    first_polarity = metadata_df['polarity'].iloc[0]
                    
                    # Convert numeric polarity codes to string
                    if first_polarity == 1 or str(first_polarity).lower() in ['positive', 'pos', '+']:
                        return "positive"
                    elif first_polarity == -1 or str(first_polarity).lower() in ['negative', 'neg', '-']:
                        return "negative"
                    
        except Exception:
            # Silently fall back to default if inference fails
            pass
            
        return 'positive'

    @property
    def polarity(self) -> str:
        """Get the ion polarity mode."""
        return self.params.polarity

    @property
    def adducts(self) -> List[str]:
        """Get the adduct specifications."""
        return self.params.adducts

    def create_script(self, filename: str = "run_masster.py") -> bool:
        """
        Generate a standalone Python script for the analysis pipeline.
        
        Parameters:
            filename: Name for the generated script file
            
        Returns:
            True if script was generated successfully, False otherwise
        """
        try:
            script_path = self.folder_path / filename
            script_content = self._generate_script_content()
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            print(f"Analysis script created: {script_path}")
            return True
            
        except Exception as e:
            print(f"Failed to create script: {e}")
            return False

    def execute(self, filename: str = "run_masster.py") -> bool:
        """
        Create and execute a standalone analysis script.
        
        Parameters:
            filename: Name for the generated script file
            
        Returns:
            True if execution completed successfully, False otherwise
        """
        # First create the script
        if not self.create_script(filename):
            return False
            
        # Then execute it
        script_path = self.folder_path / filename
        
        try:
            print("Executing...")
            
            import subprocess
            result = subprocess.run([
                sys.executable, str(script_path)
            ], cwd=str(self.folder_path), encoding='utf-8', errors='replace')
            
            success = result.returncode == 0
            
            if success:
                print("=" * 70)
                print("Script execution completed successfully")
            else:
                print("=" * 70)
                print(f"Script execution failed with return code: {result.returncode}")
                
            return success
            
        except Exception as e:
            print(f"Error during script execution: {e}")
            return False

    def _generate_script_content(self) -> str:
        """Generate the complete analysis script content."""
        
        # Convert Path objects to strings for JSON serialization
        params_dict = {}
        for key, value in self.params.__dict__.items():
            if key == '_param_metadata':  # Skip metadata in generated script
                continue
            if isinstance(value, Path):
                params_dict[key] = str(value)
            else:
                params_dict[key] = value

        # Obtain list of files in source with extension wiff, .raw, .mzML
        raw_files = []
        for ext in params_dict.get('file_extensions', []):
            raw_files.extend(glob.glob(f"{params_dict.get('source', '')}/**/*{ext}", recursive=True))

        # Create readable PARAMS dict with comments
        params_lines = []
        params_lines.append('# Analysis parameters')
        params_lines.append('PARAMS = {')
        
        # Core Configuration
        params_lines.append('    # === Core Configuration ===')
        params_lines.append(f'    "source": {params_dict.get("source", "")!r},  # Directory containing raw data files')
        params_lines.append(f'    "folder": {params_dict.get("folder", "")!r},  # Output directory for processed study')
        params_lines.append(f'    "polarity": {params_dict.get("polarity", "positive")!r},  # Ion polarity mode ("positive" or "negative")')
        params_lines.append(f'    "num_cores": {params_dict.get("num_cores", 4)},  # Number of CPU cores for parallel processing')
        params_lines.append('')
        
        # File Discovery
        params_lines.append('    # === File Discovery ===')
        params_lines.append(f'    "file_extensions": {params_dict.get("file_extensions", [".wiff", ".raw", ".mzML"])!r},  # File extensions to search for')
        params_lines.append(f'    "search_subfolders": {params_dict.get("search_subfolders", True)},  # Whether to search subdirectories recursively')
        params_lines.append(f'    "skip_patterns": {params_dict.get("skip_patterns", ["blank", "condition"])!r},  # Filename patterns to skip')
        params_lines.append('')
        
        # Processing Parameters
        params_lines.append('    # === Processing Parameters ===')
        params_lines.append(f'    "adducts": {params_dict.get("adducts", [])!r},  # Adduct specifications for feature detection and annotation')
        params_lines.append(f'    "detector_type": {params_dict.get("detector_type", "unknown")!r},  # MS detector type ("orbitrap", "tof", "unknown")')
        params_lines.append('')
        
        # Alignment & Merging
        params_lines.append('    # === Alignment & Merging ===')
        params_lines.append(f'    "rt_tol": {params_dict.get("rt_tol", 2.0)},  # Retention time tolerance for alignment (seconds)')
        params_lines.append(f'    "mz_tol": {params_dict.get("mz_tol", 0.01)},  # Mass-to-charge ratio tolerance for alignment (Da)')
        params_lines.append(f'    "alignment_method": {params_dict.get("alignment_method", "kd")!r},  # Algorithm for sample alignment')
        params_lines.append(f'    "min_samples_per_feature": {params_dict.get("min_samples_per_feature", 1)},  # Minimum samples required per consensus feature')
        params_lines.append(f'    "merge_method": {params_dict.get("merge_method", "qt")!r},  # Method for merging consensus features')
        params_lines.append('')        

        # Sample Processing
        params_lines.append('    # === Sample Processing (used in add_samples_from_folder) ===')
        params_lines.append(f'    "batch_size": {params_dict.get("batch_size", 8)},  # Number of files to process per batch')
        params_lines.append(f'    "memory_limit_gb": {params_dict.get("memory_limit_gb", 16.0)},  # Memory limit for processing (GB)')
        params_lines.append('')        
        
        # Script Options
        params_lines.append('    # === Script Options ===')
        params_lines.append(f'    "resume_enabled": {params_dict.get("resume_enabled", True)},  # Enable automatic resume capability')
        params_lines.append(f'    "force_reprocess": {params_dict.get("force_reprocess", False)},  # Force reprocessing of existing files')
        params_lines.append(f'    "cleanup_temp_files": {params_dict.get("cleanup_temp_files", True)},  # Clean up temporary files after processing')
        
        params_lines.append('}')
        
        # Create script lines
        script_lines = [
            '#!/usr/bin/env python3',
            '"""',
            'Automated Mass Spectrometry Data Analysis Pipeline',
            f'Generated by masster wizard v{version}',
            '"""',
            '',
            'import sys',
            'import time',
            'from pathlib import Path',
            '',
            '# Import masster modules',
            'from masster.study import Study',
            'from masster import __version__',
            '',
        ]
        
        # Add the formatted PARAMS
        script_lines.extend(params_lines)
        
        # Add the main function and pipeline
        script_lines.extend([
            '',
            '',
            'def discover_raw_files(source_folder, file_extensions, search_subfolders=True):',
            '    """Discover raw data files in the source folder."""',
            '    source_path = Path(source_folder)',
            '    raw_files = []',
            '    ',
            '    for ext in file_extensions:',
            '        if search_subfolders:',
            '            pattern = f"**/*{ext}"',
            '            files = list(source_path.rglob(pattern))',
            '        else:',
            '            pattern = f"*{ext}"',
            '            files = list(source_path.glob(pattern))',
            '        raw_files.extend(files)',
            '    ',
            '    return raw_files',
            '',
            '',
            'def process_single_file(args):',
            '    """Process a single raw file to sample5 format - module level for multiprocessing."""',
            '    raw_file, output_folder = args',
            '    from masster.sample import Sample',
            '    ',
            '    try:',
            '        # Create sample5 filename',
            '        sample_name = raw_file.stem',
            '        sample5_path = Path(output_folder) / f"{sample_name}.sample5"',
            '        ',
            '        # Skip if sample5 already exists',
            '        if sample5_path.exists():',
            '            print(f"  Skipping {raw_file.name} (sample5 already exists)")',
            '            return str(sample5_path)',
            '        ',
            '        print(f"  Converting {raw_file.name}...")',
            '        ',
            '        # Load and process raw file with full pipeline',
            '        sample = Sample(log_label=sample_name)',
            '        sample.load(filename=str(raw_file))',
            '        sample.find_features(',
            '            noise=PARAMS[\'noise\'],',
            '            chrom_fwhm=PARAMS[\'chrom_fwhm\'],',
            '            chrom_peak_snr=PARAMS[\'chrom_peak_snr\']',
            '        )',
            '        sample.find_adducts(adducts=PARAMS[\'adducts\'])',
            '        sample.find_ms2()',
            '        # sample.find_iso()',
            '        # sample.export_mgf()',
            '        # sample.export_mztab()',
            '        # sample.plot_2d(filename="{sample_name}.html")',
            '        sample.save(str(sample5_path))',
            '        ',
            '        # print(f"  Completed {raw_file.name} -> {sample5_path.name}")',
            '        return str(sample5_path)',
            '        ',
            '    except Exception as e:',
            '        print(f"  ERROR processing {raw_file.name}: {e}")',
            '        return None',
            '',
            '',
            'def convert_raw_to_sample5(raw_files, output_folder, polarity, num_cores):',
            '    """Convert raw data files to sample5 format."""',
            '    import concurrent.futures',
            '    import os',
            '    ',
            '    # Create output directory',
            '    os.makedirs(output_folder, exist_ok=True)',
            '    ',
            '    # Prepare arguments for multiprocessing',
            '    file_args = [(raw_file, output_folder) for raw_file in raw_files]',
            '    ',
            '    # Process files in parallel',
            '    sample5_files = []',
            '    with concurrent.futures.ProcessPoolExecutor(max_workers=num_cores) as executor:',
            '        futures = [executor.submit(process_single_file, args) for args in file_args]',
            '        ',
            '        for future in concurrent.futures.as_completed(futures):',
            '            result = future.result()',
            '            if result:',
            '                sample5_files.append(result)',
            '    ',
            '    return sample5_files',
            '',
            '',
            'def main():',
            '    """Main analysis pipeline."""',
            '    try:',
            '        print("=" * 70)',
            f'        print("masster {version} - Automated MS Data Analysis")',
            '        print("=" * 70)',
            '        print(f"Source: {PARAMS[\'source\']}")',
            '        print(f"Output: {PARAMS[\'folder\']}")',
            '        print(f"Polarity: {PARAMS[\'polarity\']}")',
            '        print(f"CPU Cores: {PARAMS[\'num_cores\']}")',
            '        print("=" * 70)',
            '        ',
            '        start_time = time.time()',
            '        ',
            '        # Step 1: Discover raw data files',
            '        print("\\nStep 1/7: Discovering raw data files...")',
            '        raw_files = discover_raw_files(',
            '            PARAMS[\'source\'],',
            '            PARAMS[\'file_extensions\'],',
            '            PARAMS[\'search_subfolders\']',
            '        )',
            '        ',
            '        if not raw_files:',
            '            print("No raw data files found!")',
            '            return False',
            '        ',
            '        print(f"Found {len(raw_files)} raw data files")',
            '        for f in raw_files[:5]:  # Show first 5 files',
            '            print(f"  {f.name}")',
            '        if len(raw_files) > 5:',
            '            print(f"  ... and {len(raw_files) - 5} more")',
            '        ',
            '        # Step 2: Process raw files',
            '        print("\\nStep 2/7: Processing raw files...")',
            '        sample5_files = convert_raw_to_sample5(',
            '            raw_files,',
            '            PARAMS[\'folder\'],',
            '            PARAMS[\'polarity\'],',
            '            PARAMS[\'num_cores\']',
            '        )',
            '        ',
            '        if not sample5_files:',
            '            print("No sample5 files were created!")',
            '            return False',
            '        ',
            '        print(f"Successfully processed {len(sample5_files)} files to sample5")',
            '        ',
            '        # Step 3: Create and configure study',
            '        print("\\nStep 3/7: Initializing study...")',
            '        study = Study(folder=PARAMS[\'folder\'])',
            '        study.polarity = PARAMS[\'polarity\']',
            '        study.adducts = PARAMS[\'adducts\']',
            '        ',
            '        # Step 4: Add sample5 files to study',
            '        print("\\nStep 4/7: Adding samples to study...")',
            '        study.add(str(Path(PARAMS[\'folder\']) / "*.sample5"))',
            '        ',
            '        # Step 5: Core processing',
            '        print("\\nStep 5/7: Processing...")',
            '        study.align(',
            '            algorithm=PARAMS[\'alignment_method\'],',
            '            rt_tol=PARAMS[\'rt_tol\']',
            '        )',
            '        ',
            '        # Merge and create consensus features',
            '        study.merge(',
            '            min_samples=PARAMS[\'min_samples_per_feature\'],',
            '            threads=PARAMS[\'num_cores\'],',
            '            rt_tol=PARAMS[\'rt_tol\'],',
            '            mz_tol=PARAMS[\'mz_tol\']',
            '        )',
            '        study.find_iso()',
            '        study.fill(min_samples_rel=0.0)',
            '        study.integrate()',    
            '        ',
            '        # Step 6/7: Saving results',
            '        print("\\nStep 6/7: Saving results...")',
            '        study.save()',
            '        study.export_xlsx()',
            '        study.export_mgf()',
            '        study.export_mztab()',
            '        ',
            '        # Step 7: Plots',
            '        print("\\nStep 7/7: Exporting plots...")',
            '        study.plot_consensus_2d(filename="consensus.html")',
            '        study.plot_consensus_2d(filename="consensus.png")',
            '        study.plot_alignment(filename="alignment.html")',
            '        study.plot_alignment(filename="alignment.png")',
            '        study.plot_pca(filename="pca.html")',
            '        study.plot_pca(filename="pca.png")',
            '        study.plot_bpc(filename="bpc.html")',
            '        study.plot_bpc(filename="bpc.png")',
            '        study.plot_rt_correction(filename="rt_correction.html")',
            '        study.plot_rt_correction(filename="rt_correction.png")',

            '        ',
            '        # Print summary',
            '        study.info()',
            '        total_time = time.time() - start_time',
            '        print("\\n" + "=" * 70)',
            '        print("ANALYSIS COMPLETE")',
            '        print("=" * 70)',
            '        print(f"Total processing time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")',
            '        print(f"Raw files processed: {len(raw_files)}")',
            '        print(f"Sample5 files created: {len(sample5_files)}")',
            '        if hasattr(study, "consensus_df"):',
            '            print(f"Consensus features generated: {len(study.consensus_df)}")',
            '        print("=" * 70)',
            '        ',
            '        return True',
            '        ',
            '    except KeyboardInterrupt:',
            '        print("\\nAnalysis interrupted by user")',
            '        return False',
            '    except Exception as e:',
            '        print(f"Analysis failed with error: {e}")',
            '        import traceback',
            '        traceback.print_exc()',
            '        return False',
            '',
            '',
            'if __name__ == "__main__":',
            '    success = main()',
            '    sys.exit(0 if success else 1)',
        ])
        
        return '\n'.join(script_lines)


def create_script(
    source: str, 
    folder: str, 
    filename: str = 'run_masster.py', 
    polarity: str = "positive",
    adducts: Optional[List[str]] = None,
    params: Optional[wizard_def] = None,
    num_cores: int = 0,
    **kwargs
) -> bool:
    """
    Create a standalone analysis script without initializing a Wizard instance.
    
    This function generates a Python script that replicates automated processing
    steps with the specified configuration. The script can be executed independently
    to perform the same analysis.
    
    Parameters:
        source: Directory containing raw data files
        folder: Output directory for processed study  
        filename: Filename for the generated script (should end with .py)
        polarity: Ion polarity mode ("positive" or "negative")
        adducts: List of adduct specifications (auto-set if None)
        params: Custom wizard_def parameters (optional)
        num_cores: Number of CPU cores (0 = auto-detect)
        **kwargs: Additional parameters to override defaults
        
    Returns:
        True if script was generated successfully, False otherwise
        
    Example:
        >>> from masster.wizard import create_script
        >>> create_script(
        ...     source=r'D:\\Data\\raw_files',
        ...     folder=r'D:\\Data\\output', 
        ...     filename='run_masster.py',
        ...     polarity='positive'
        ... )
    """
    
    try:
        # Create parameters
        if params is not None:
            # Use provided params as base
            wizard_params = params
            # Update with provided values
            wizard_params.source = source
            wizard_params.folder = folder
            if polarity != "positive":  # Only override if explicitly different
                wizard_params.polarity = polarity
            if num_cores > 0:
                wizard_params.num_cores = num_cores
            if adducts is not None:
                wizard_params.adducts = adducts
        else:
            # Create new params with provided values
            wizard_params = wizard_def(
                source=source,
                folder=folder,
                polarity=polarity,
                num_cores=max(1, int(multiprocessing.cpu_count() * 0.75)) if num_cores <= 0 else num_cores
            )
            
            if adducts is not None:
                wizard_params.adducts = adducts
            
            # Apply any additional kwargs
            for key, value in kwargs.items():
                if hasattr(wizard_params, key):
                    setattr(wizard_params, key, value)
        
        # Ensure study folder exists
        study_path = Path(folder)
        study_path.mkdir(parents=True, exist_ok=True)
        
        # Create a temporary Wizard instance to generate the script
        temp_wizard = Wizard(params=wizard_params)
        
        # Generate the script using the instance method
        success = temp_wizard.create_script(filename)
        
        return success
        
    except Exception as e:
        print(f"Failed to create script: {e}")
        import traceback
        traceback.print_exc()
        return False


def execute(
    source: str, 
    folder: str, 
    filename: str = 'run_masster.py', 
    polarity: str = "positive",
    adducts: Optional[List[str]] = None,
    params: Optional[wizard_def] = None,
    num_cores: int = 0,
    **kwargs
) -> bool:
    """
    Create and execute a standalone analysis script for automated MS data processing.
    
    This function generates a Python script with the same parameters as create_script(),
    but immediately executes it after creation. Combines script generation and execution
    in a single step.
    
    Parameters:
        source: Directory containing raw data files
        folder: Output directory for processed study  
        filename: Filename for the generated script (should end with .py)
        polarity: Ion polarity mode ("positive" or "negative")
        adducts: List of adduct specifications (auto-set if None)
        params: Custom wizard_def parameters (optional)
        num_cores: Number of CPU cores (0 = auto-detect)
        **kwargs: Additional parameters to override defaults
        
    Returns:
        True if script was created and executed successfully, False otherwise
        
    Example:
        >>> from masster.wizard import execute
        >>> execute(
        ...     source=r'D:\\Data\\raw_files',
        ...     folder=r'D:\\Data\\output', 
        ...     polarity='positive'
        ... )
    """
    
    try:
        # First, create the script using create_script()
        script_created = create_script(
            source=source,
            folder=folder,
            filename=filename,
            polarity=polarity,
            adducts=adducts,
            params=params,
            num_cores=num_cores,
            **kwargs
        )
        
        if not script_created:
            print("Failed to create analysis script")
            return False
            
        # Get the full path to the created script
        study_path = Path(folder)
        script_path = study_path / Path(filename).name
        
        if not script_path.exists():
            print(f"Script file not found: {script_path}")
            return False
            
        print(f"Executing...")
        #print("=" * 70)
        
        # Execute the script using subprocess with real-time output
        import subprocess
        
        # Run the script with Python, letting it inherit our stdout/stderr
        try:
            # Use subprocess.run for direct output inheritance - no capturing/re-printing
            result = subprocess.run([
                sys.executable, str(script_path)
            ], cwd=str(study_path))
            
            return_code = result.returncode
            
        except Exception as e:
            print(f"Error during script execution: {e}")
            return False
        
        success = return_code == 0
        
        if success:
            print("=" * 70)
            print("Script execution completed successfully")
        else:
            print("=" * 70)
            print(f"Script execution failed with return code: {return_code}")
            
        return success
        
    except Exception as e:
        print(f"Failed to execute script: {e}")
        import traceback
        traceback.print_exc()
        return False


# Export the main classes and functions
__all__ = ["Wizard", "wizard_def", "create_script", "execute"]
