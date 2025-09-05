"""A Python library that provides data acquisition and processing assets shared between Sun (NeuroAI) lab libraries.

See https://github.com/Sun-Lab-NBB/sl-shared-assets for more details.
API documentation: https://sl-shared-assets-api-docs.netlify.app/
Authors: Ivan Kondratyev (Inkaros), Kushaan Gupta, Natalie Yeung
"""

from ataraxis_base_utilities import console

from .tools import (
    acquire_lock,
    release_lock,
    delete_directory,
    transfer_directory,
    generate_project_manifest,
    calculate_directory_checksum,
)
from .server import (
    Job,
    Server,
    JupyterJob,
    ProcessingStatus,
    TrackerFileNames,
    ProcessingTracker,
    ServerCredentials,
    ProcessingPipeline,
    ProcessingPipelines,
    generate_manager_id,
)
from .data_classes import (
    RawData,
    DrugData,
    ImplantData,
    SessionData,
    SessionLock,
    SubjectData,
    SurgeryData,
    SessionTypes,
    InjectionData,
    ProcedureData,
    ProcessedData,
    MesoscopePaths,
    ZaberPositions,
    ExperimentState,
    ExperimentTrial,
    MesoscopeCameras,
    AcquisitionSystems,
    MesoscopePositions,
    RunTrainingDescriptor,
    LickTrainingDescriptor,
    MesoscopeHardwareState,
    WindowCheckingDescriptor,
    MesoscopeMicroControllers,
    MesoscopeAdditionalFirmware,
    MesoscopeSystemConfiguration,
    MesoscopeExperimentDescriptor,
    MesoscopeExperimentConfiguration,
    get_working_directory,
    get_credentials_file_path,
    get_system_configuration_data,
)

# Ensures console is enabled when this library is imported
if not console.enabled:
    console.enable()

__all__ = [
    "AcquisitionSystems",
    "DrugData",
    "ExperimentState",
    "ExperimentTrial",
    "ImplantData",
    "InjectionData",
    "Job",
    "JupyterJob",
    "LickTrainingDescriptor",
    "MesoscopeAdditionalFirmware",
    "MesoscopeCameras",
    "MesoscopeExperimentConfiguration",
    "MesoscopeExperimentDescriptor",
    "MesoscopeHardwareState",
    "MesoscopeMicroControllers",
    "MesoscopePaths",
    "MesoscopePositions",
    "MesoscopeSystemConfiguration",
    "ProcedureData",
    "ProcessedData",
    "ProcessingPipeline",
    "ProcessingPipelines",
    "ProcessingStatus",
    "ProcessingTracker",
    "RawData",
    "RunTrainingDescriptor",
    "Server",
    "ServerCredentials",
    "SessionData",
    "SessionLock",
    "SessionTypes",
    "SubjectData",
    "SurgeryData",
    "TrackerFileNames",
    "WindowCheckingDescriptor",
    "ZaberPositions",
    "acquire_lock",
    "calculate_directory_checksum",
    "delete_directory",
    "generate_manager_id",
    "generate_project_manifest",
    "get_credentials_file_path",
    "get_system_configuration_data",
    "get_working_directory",
    "release_lock",
    "transfer_directory",
]
