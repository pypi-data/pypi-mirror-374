"""
Result classes for Heaptree API responses.
"""


class CreateNodeResponseWrapper:
    def __init__(self, raw_response):
        self._raw = raw_response
    
    @property
    def node_id(self) -> str:
        """Convenience property for accessing single node ID when only one node was created."""
        node_ids = self._raw["node_ids"]
        if len(node_ids) == 1:
            return node_ids[0]
        elif len(node_ids) == 0:
            raise ValueError("No nodes were created")
        else:
            raise ValueError(
                f"Multiple nodes created ({len(node_ids)}). "
                f"Use .node_ids to access all node IDs: {node_ids}"
            )
    
    @property
    def web_access_url(self) -> str:
        """Convenience property for accessing single web access URL when only one node was created."""
        node_ids = self._raw["node_ids"]
        if len(node_ids) == 1:
            return self._raw["web_access_urls"][node_ids[0]]
        elif len(node_ids) == 0:
            raise ValueError("No nodes were created")
        else:
            raise ValueError(
                f"Multiple nodes created ({len(node_ids)}). "
                f"Use .web_access_urls to access all web access URLs: {self._raw['web_access_urls']}"
            )
    
    @property
    def node_ids(self) -> list[str]:
        return self._raw["node_ids"]
    
    @property
    def web_access_urls(self) -> dict[str, str]:
        return self._raw["web_access_urls"]
    
    @property
    def status(self) -> str:
        """Status of the node creation operation."""
        return self._raw.get("status", "unknown")
    
    @property
    def execution_time_seconds(self) -> float:
        """Time taken to create the nodes in seconds."""
        return self._raw.get("execution_time_seconds", 0.0)


class NodesResponseWrapper:
    """Wrapper for get_nodes API response."""
    
    def __init__(self, raw_response):
        self._raw = raw_response
    
    @property
    def nodes(self) -> list[dict]:
        """List of node information dictionaries."""
        return self._raw.get("nodes", [])
    
    @property
    def count(self) -> int:
        """Number of nodes returned."""
        return len(self.nodes)
    
    @property
    def node_ids(self) -> list[str]:
        """Extract node IDs from the nodes list."""
        return [node["node_id"] for node in self.nodes if "node_id" in node]


class ExecutionResponseWrapper:
    """Wrapper for run_command and run_code API responses."""
    
    def __init__(self, raw_response):
        self._raw = raw_response
    
    @property
    def output(self) -> str:
        """Output from the command/code execution."""
        return self._raw.get("output", "")
    
    @property
    def error(self) -> str:
        """Error output if any."""
        return self._raw.get("error", "")
    
    @property
    def exit_code(self) -> int:
        """Exit code of the command/code execution."""
        return self._raw.get("exit_code", 0)
    
    @property
    def success(self) -> bool:
        """Whether the execution was successful."""
        return self.exit_code == 0 and not self.error
    
    @property
    def execution_time_seconds(self) -> float:
        """Time taken for execution in seconds."""
        return self._raw.get("execution_time_seconds", 0.0)


class UsagesResponseWrapper:
    """Wrapper for get_usages API response."""
    
    def __init__(self, raw_response):
        self._raw = raw_response
    
    @property
    def usages(self) -> list[dict]:
        """List of usage records."""
        return self._raw.get("usages", [])
    
    @property
    def count(self) -> int:
        """Number of usage records returned."""
        return len(self.usages)
    
    @property
    def total_cost(self) -> float:
        """Total cost across all usage records."""
        return sum(usage.get("cost", 0.0) for usage in self.usages)
    
    @property
    def total_duration_seconds(self) -> float:
        """Total duration across all usage records in seconds."""
        return sum(usage.get("duration_seconds", 0.0) for usage in self.usages)