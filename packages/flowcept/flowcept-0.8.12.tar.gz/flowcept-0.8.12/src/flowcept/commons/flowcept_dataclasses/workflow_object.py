"""Workflow Object module."""

from typing import Dict, AnyStr, List
import msgpack
from omegaconf import OmegaConf, DictConfig

from flowcept.version import __version__
from flowcept.commons.utils import get_utc_now, get_git_info
from flowcept.configs import (
    settings,
    FLOWCEPT_USER,
    SYS_NAME,
    EXTRA_METADATA,
    ENVIRONMENT_ID,
    SETTINGS_PATH,
)


# Not a dataclass because a dataclass stores keys even when there's no value,
# adding unnecessary overhead.
class WorkflowObject:
    """Workflow class."""

    workflow_id: AnyStr = None
    parent_workflow_id: AnyStr = None
    machine_info: Dict = None
    conf: Dict = None
    flowcept_settings: Dict = None
    flowcept_version: AnyStr = None
    utc_timestamp: float = None
    user: AnyStr = None
    campaign_id: AnyStr = None
    adapter_id: AnyStr = None
    interceptor_ids: List[AnyStr] = None
    name: AnyStr = None
    custom_metadata: Dict = None
    environment_id: str = None
    sys_name: str = None
    extra_metadata: str = None
    used: Dict = None
    code_repository: Dict = None
    generated: Dict = None

    def __init__(self, workflow_id=None, name=None, used=None, generated=None):
        self.workflow_id = workflow_id
        self.name = name
        self.used = used
        self.generated = generated

    @staticmethod
    def workflow_id_field():
        """Get workflow id."""
        return "workflow_id"

    @staticmethod
    def from_dict(dict_obj: Dict) -> "WorkflowObject":
        """Convert from dictionary."""
        wf_obj = WorkflowObject()
        for k, v in dict_obj.items():
            setattr(wf_obj, k, v)
        return wf_obj

    def to_dict(self):
        """Convert to dictionary."""
        result_dict = {}
        for attr, value in self.__dict__.items():
            if value is not None:
                result_dict[attr] = value
        result_dict["type"] = "workflow"
        return result_dict

    def enrich(self, adapter_key=None):
        """Enrich it."""
        self.utc_timestamp = get_utc_now()
        self.flowcept_settings = OmegaConf.to_container(settings) if isinstance(settings, DictConfig) else settings
        self.conf = {"settings_path": SETTINGS_PATH}
        if adapter_key is not None:
            # TODO :base-interceptor-refactor: :code-reorg: :usability:
            # revisit all times we assume settings is not none
            self.adapter_id = adapter_key

        if self.user is None:
            self.user = FLOWCEPT_USER

        if self.environment_id is None and ENVIRONMENT_ID is not None:
            self.environment_id = ENVIRONMENT_ID

        if self.sys_name is None and SYS_NAME is not None:
            self.sys_name = SYS_NAME

        if self.extra_metadata is None and EXTRA_METADATA is not None:
            _extra_metadata = (
                OmegaConf.to_container(EXTRA_METADATA) if isinstance(EXTRA_METADATA, DictConfig) else EXTRA_METADATA
            )
            self.extra_metadata = _extra_metadata

        if self.code_repository is None:
            try:
                self.code_repository = get_git_info()
            except Exception as e:
                print(e)
                pass

        if self.flowcept_version is None:
            self.flowcept_version = __version__

    def serialize(self):
        """Serialize it."""
        return msgpack.dumps(self.to_dict())

    @staticmethod
    def deserialize(serialized_data) -> "WorkflowObject":
        """Deserialize it."""
        dict_obj = msgpack.loads(serialized_data)
        obj = WorkflowObject()
        for k, v in dict_obj.items():
            setattr(obj, k, v)
        return obj

    def __repr__(self):
        """Set the repr."""
        return (
            f"WorkflowObject("
            f"workflow_id={repr(self.workflow_id)}, "
            f"parent_workflow_id={repr(self.parent_workflow_id)}, "
            f"machine_info={repr(self.machine_info)}, "
            f"flowcept_settings={repr(self.flowcept_settings)}, "
            f"flowcept_version={repr(self.flowcept_version)}, "
            f"utc_timestamp={repr(self.utc_timestamp)}, "
            f"user={repr(self.user)}, "
            f"campaign_id={repr(self.campaign_id)}, "
            f"adapter_id={repr(self.adapter_id)}, "
            f"interceptor_ids={repr(self.interceptor_ids)}, "
            f"name={repr(self.name)}, "
            f"used={repr(self.used)}, "
            f"generated={repr(self.generated)}, "
            f"custom_metadata={repr(self.custom_metadata)})"
        )

    def __str__(self):
        """Set the string."""
        return self.__repr__()
