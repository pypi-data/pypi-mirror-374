# ORCA Transportation Model Orchestrator

The ORCA Orchestrator is a comprehensive Python tool for managing and executing the ORCA transportation model. It provides a unified interface for model initialization, execution, state management, and cloud synchronization.

## Overview

The orchestrator manages complex transportation modeling workflows by:
- Coordinating multiple sub-component models (ActivitySim, Quetzal, PopulationSim, etc.)
- Managing databank lifecycle (initialization, execution, archiving)
- Handling cloud synchronization with Azure Data Lake Storage (ADLS)
- Providing performance monitoring and error handling
- Maintaining execution state across iterations and steps

## Architecture

The orchestrator consists of several key components:

### Core Classes

1. **`OrcaOrchestrator`** - Main orchestrator class that manages model execution
2. **`OrcaLogger`** - Centralized logging with singleton behavior
3. **`OrcaState`** - State management for tracking iterations and steps
4. **`OrcaDatabank`** - Local file operations and databank management
5. **`OrcaFileSync`** - Cloud synchronization with Azure Data Lake Storage
6. **`OrcaPerformanceMonitor`** - Runtime and system resource monitoring

### Key Features

- **Multi-mode execution**: Local testing and cloud production modes
- **Iterative modeling**: Support for multiple model iterations with state persistence
- **Cloud integration**: Seamless synchronization with Azure Data Lake Storage
- **Error handling**: Comprehensive error dumps and recovery mechanisms
- **Performance monitoring**: Real-time tracking of system resources and execution time
- **Template management**: Automated copying and setup of model templates

## Usage

### Command Line Interface

The orchestrator provides an action-based command line interface:

```bash
python orchestrator.py [options]
```

### Actions

#### 1. Run Models (`run_models`)
Initialize and run the complete model workflow.

```bash
# Basic model run
python orchestrator.py --action run_models --databank my_scenario

# Advanced options
python orchestrator.py --action run_models \
    --databank my_scenario \
    --mode cloud_production \
    --iterations 3 \
    --steps activitysim quetzal \
    --project-folder custom_project
```

#### 2. Initialize Databank (`initialize_databank`)
Create and set up a new databank without running models.

```bash
# Initialize new databank
python orchestrator.py --action initialize_databank --databank my_scenario

# Overwrite existing databank
python orchestrator.py --action initialize_databank --databank my_scenario --overwrite

# Dry run (show what would be done)
python orchestrator.py --action initialize_databank --databank my_scenario --dry-run
```

#### 3. Cloud Synchronization (`adls_sync`)
Synchronize databank with Azure Data Lake Storage.

```bash
# Upload to cloud
python orchestrator.py --action adls_sync --databank my_scenario --sync-action upload

# Download from cloud
python orchestrator.py --action adls_sync --databank my_scenario --sync-action download

# List cloud contents
python orchestrator.py --action adls_sync --databank my_scenario --sync-action list

# Custom project folder
python orchestrator.py --action adls_sync \
    --databank my_scenario \
    --sync-action upload \
    --project-folder my_custom_project
```

#### 4. Unpack Land Use (`unpack_landuse`)
Extract land use files filtered by model year from zip archives.

```bash
python orchestrator.py --action unpack_landuse \
    --model-year 2017 \
    --input landuse_data.zip \
    --output ./data
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--databank` | Name of the databank (scenario) | `db_test` |
| `--config` | Configuration file name | `orca_model_config.yaml` |
| `--state` | State file name | `orca_model_state.json` |
| `--mode` | Execution mode (`local_testing`, `cloud_production`) | `local_testing` |
| `--iterations` | Number of iterations to run | From config file |
| `--steps` | Specific model steps to run | From config file |
| `--overwrite` | Overwrite existing databank | `False` |
| `--dry-run` | Show what would be done without executing | `False` |
| `--project-folder` | Override ADLS project folder path | From config file |
| `--verbose` | Enable verbose logging | `False` |

## Configuration

The orchestrator uses a YAML configuration file (`orca_model_config.yaml`) that defines:

### Model Configuration Structure

```yaml
# Model execution settings
model_steps:
  - activitysim
  - quetzal
  - populationsim

iterations:
  total: 3
  start_at: 1

# Sub-component configurations
sub_components:
  activitysim:
    template_dir: "/path/to/activitysim/template"
    commands:
      - description: "Run ActivitySim"
        command: "python run_activitysim.py"
    output_archives:
      - pattern: "outputs/*.csv"
        archive_name: "activitysim_outputs"
    cleanup_patterns:
      - "*.tmp"
      - "temp_*"

# Input data sources
input_data:
  landuse:
    - source: "/shared/landuse/"
      target: "inputs/landuse/"
  networks:
    - source: "/shared/networks/"
      target: "inputs/networks/"

# Cloud operations
operational_mode:
  cloud:
    adls_url: "https://account.dfs.core.windows.net"
    adls_container: "raw"
    adls_folder: "orca_model_runs"

# Performance monitoring
performance_monitoring:
  enabled: true
  poll_interval: 1.0
  track_memory: true
  track_cpu: true
```

## Execution Modes

### Local Testing Mode
- Executes models locally without cloud integration
- Suitable for development and testing
- All data remains on local filesystem

### Cloud Production Mode
- Integrates with Azure Data Lake Storage
- Automatic synchronization of databanks
- Suitable for production modeling workflows
- Supports distributed execution

## File Management

### Databank Structure
```
databank_name/
├── orca_model_config.yaml       # Configuration file
├── orca_model_state.json        # Execution state
├── orca_orchestrator.log        # Orchestrator logs
├── inputs/                      # Shared input data
├── outputs/                     # Model outputs
├── activitysim/                 # Sub-component folder
├── quetzal/                     # Sub-component folder
└── .cloud_sync_conflict/        # Conflict resolution
```

### Cloud Synchronization Behavior

#### Upload Logic:
- Sub-component folders are zipped before upload
- Config files are uploaded individually with conflict handling
- Output files are uploaded individually (never overwritten)
- Error dumps are uploaded to special error_dumps/ folder

#### Download Logic:
- Empty local databank: Downloads everything
- Existing local databank: Downloads only new output files
- Conflict files are moved to `.cloud_sync_conflict/` folder

## State Management

The orchestrator maintains execution state in `orca_model_state.json`:

```json
{
  "start_at": 1,
  "total_iterations": 3,
  "current_iteration": 1,
  "steps": ["activitysim", "quetzal"],
  "completed_steps": ["activitysim"],
  "current_step_index": 1,
  "status": "running",
  "start_time": "2025-01-15 10:30:00",
  "last_updated": "2025-01-15 11:45:00"
}
```

## Performance Monitoring

When enabled, the orchestrator tracks:
- Runtime duration for each step
- System memory usage (GB)
- CPU utilization (%)
- Process-specific metrics

Monitoring data is exported to CSV files for analysis.

## Error Handling

### Error Dumps
When a model execution fails, the orchestrator creates comprehensive error dumps containing:
- All data from the failed step directory
- Configuration files
- Log files
- System state information
- Optionally, entire databank content

### Recovery
The state file enables resuming execution from the last successful step.

## Dependencies

### Required:
- Python 3.7+
- PyYAML
- Standard library modules (json, logging, argparse, etc.)

### Optional:
- `psutil` - For system monitoring
- `tlpytools.adls_server` - For Azure Data Lake Storage integration

## Environment Variables

- `UPLOAD_OUTPUTS_ONLY` - If set to True, only uploads outputs and config files to cloud
- Performance monitoring can be controlled via config file

## Logging

The orchestrator provides comprehensive logging with:
- Singleton logger pattern for consistency
- File and console output
- Configurable log levels
- System information capture
- Azure SDK logging suppression

Log files are created in the databank directory as `orca_orchestrator.log`.

## Examples

### Complete Workflow Example
```bash
# 1. Initialize a new databank
python orchestrator.py --action initialize_databank --databank scenario_2030

# 2. Run the complete model workflow
python orchestrator.py --action run_models --databank scenario_2030 --iterations 5

# 3. Upload results to cloud
python orchestrator.py --action adls_sync --databank scenario_2030 --sync-action upload
```

### Cloud Production Example
```bash
# Initialize and run in cloud production mode
python orchestrator.py --action run_models \
    --databank production_scenario \
    --mode cloud_production \
    --iterations 10 \
    --project-folder production_runs
```

### Debugging Example
```bash
# Run with verbose logging and dry-run
python orchestrator.py --action initialize_databank \
    --databank debug_scenario \
    --verbose \
    --dry-run
```

## Troubleshooting

### Common Issues

1. **Configuration not found**: Ensure `orca_model_config.yaml` exists or specify custom config
2. **Cloud authentication**: Verify Azure credentials are configured
3. **Permission errors**: Check file system permissions for databank directory
4. **Memory issues**: Monitor system resources during large model runs

### Debug Tips

1. Use `--verbose` flag for detailed logging
2. Check `orca_orchestrator.log` for detailed execution information
3. Use `--dry-run` to validate configuration without execution
4. Monitor state file for execution progress

## Integration

The orchestrator is designed to integrate with:
- ActivitySim transportation modeling framework
- Quetzal strategic modeling platform
- PopulationSim population synthesis tool
- Azure Data Lake Storage for cloud workflows
- Various transportation modeling tools and utilities

For specific integration details, refer to the sub-component documentation and configuration examples.
