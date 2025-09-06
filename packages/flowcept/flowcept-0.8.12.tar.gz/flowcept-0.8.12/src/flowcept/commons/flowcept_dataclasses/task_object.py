"""Task object module."""

from typing import Dict, AnyStr, Any, Union, List
import msgpack

import flowcept
from flowcept.commons.flowcept_dataclasses.telemetry import Telemetry
from flowcept.commons.vocabulary import Status
from flowcept.configs import (
    HOSTNAME,
    PRIVATE_IP,
    PUBLIC_IP,
    LOGIN_NAME,
    NODE_NAME,
)


class TaskObject:
    """Task class."""

    type = "task"
    subtype: AnyStr = None
    task_id: AnyStr = None  # Any way to identify a task
    utc_timestamp: float = None
    adapter_id: AnyStr = None
    user: AnyStr = None
    data: Any = None
    used: Dict[AnyStr, Any] = None  # Used parameter and files
    campaign_id: AnyStr = None
    generated: Dict[AnyStr, Any] = None  # Generated results and files
    submitted_at: float = None
    started_at: float = None
    ended_at: float = None
    registered_at: float = None  # Leave this for dates generated at the DocInserter
    telemetry_at_start: Telemetry = None
    telemetry_at_end: Telemetry = None
    workflow_name: AnyStr = None
    workflow_id: AnyStr = None
    parent_task_id: AnyStr = None
    activity_id: AnyStr = None
    group_id: AnyStr = None  # Utilized especially for loop iteration tasks, to group them.
    status: Status = None
    stdout: Union[AnyStr, Dict] = None
    stderr: Union[AnyStr, Dict] = None
    custom_metadata: Dict[AnyStr, Any] = None
    mq_host: str = None
    environment_id: AnyStr = None
    node_name: AnyStr = None
    login_name: AnyStr = None
    public_ip: AnyStr = None
    private_ip: AnyStr = None
    hostname: AnyStr = None
    address: AnyStr = None
    dependencies: List = None
    dependents: List = None
    tags: List = None
    agent_id: str = None

    _DEFAULT_ENRICH_VALUES = {
        "node_name": NODE_NAME,
        "login_name": LOGIN_NAME,
        "public_ip": PUBLIC_IP,
        "private_ip": PRIVATE_IP,
        "hostname": HOSTNAME,
    }

    @staticmethod
    def get_time_field_names():
        """Get the time field."""
        return [
            "started_at",
            "ended_at",
            "submitted_at",
            "registered_at",
            "utc_timestamp",
        ]

    @staticmethod
    def get_dict_field_names():
        """Get field names."""
        return [
            "used",
            "generated",
            "custom_metadata",
            "telemetry_at_start",
            "telemetry_at_end",
        ]

    @staticmethod
    def task_id_field():
        """Get task id."""
        return "task_id"

    @staticmethod
    def workflow_id_field():
        """Get workflow id."""
        return "workflow_id"

    def enrich(self, adapter_key=None):
        """Enrich it."""
        if adapter_key is not None:
            # TODO :base-interceptor-refactor: :code-reorg: :usability:
            # revisit all times we assume settings is not none
            self.adapter_id = adapter_key

        if self.utc_timestamp is None:
            self.utc_timestamp = flowcept.commons.utils.get_utc_now()

        for key, fallback_value in TaskObject._DEFAULT_ENRICH_VALUES.items():
            if getattr(self, key) is None and fallback_value is not None:
                setattr(self, key, fallback_value)

    @staticmethod
    def enrich_task_dict(task_dict: dict):
        """Enrich the task."""
        for key, fallback_value in TaskObject._DEFAULT_ENRICH_VALUES.items():
            if (key not in task_dict or task_dict[key] is None) and fallback_value is not None:
                task_dict[key] = fallback_value

    def to_dict(self):
        """Convert to dictionary."""
        result_dict = {}
        for attr, value in self.__dict__.items():
            if value is not None:
                if attr == "telemetry_at_start":
                    result_dict[attr] = self.telemetry_at_start.to_dict()
                elif attr == "telemetry_at_end":
                    result_dict[attr] = self.telemetry_at_end.to_dict()
                elif attr == "status":
                    result_dict[attr] = value.value
                else:
                    result_dict[attr] = value
        result_dict["type"] = "task"
        return result_dict

    def serialize(self):
        """Serialize it."""
        return msgpack.dumps(self.to_dict())

    @staticmethod
    def from_dict(task_obj_dict: Dict[AnyStr, Any]) -> "TaskObject":
        """Create a TaskObject from a dictionary.

        Parameters
        ----------
        task_obj_dict : Dict[AnyStr, Any]
            Dictionary containing task attributes.

        Returns
        -------
        TaskObject
            A TaskObject instance populated with available data.
        """
        task = TaskObject()

        for key, value in task_obj_dict.items():
            if hasattr(task, key):
                if key == "status" and isinstance(value, str):
                    setattr(task, key, Status(value))
                else:
                    setattr(task, key, value)

        return task

    def __str__(self):
        """Return a user-friendly string representation of the TaskObject."""
        return self.__repr__()

    def __repr__(self):
        """Return an unambiguous string representation of the TaskObject."""
        attrs = ["task_id", "workflow_id", "campaign_id", "activity_id", "started_at", "ended_at"]
        optionals = ["subtype", "parent_task_id", "agent_id"]
        for opt in optionals:
            if getattr(self, opt) is not None:
                attrs.append(opt)
        attr_str = ", ".join(f"{attr}={repr(getattr(self, attr))}" for attr in attrs)
        return f"TaskObject({attr_str})"
