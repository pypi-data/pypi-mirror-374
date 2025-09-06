"""
Workspace path handling for user sessions.
"""

from pathlib import Path, PurePath, PurePosixPath

from fastmcp import Context

from ..utils.config import DATA_DIR
from .utils import get_session_id_tuple

WORKSPACES_ROOT_DIR = DATA_DIR / "workspaces"  # Path on the host where workspaces are stored
CONTAINER_WORKSPACE_PATH = PurePosixPath("/workspace")  # Path inside the sandbox container where workspace is mounted


def get_workspace_path(service_name: str = None, *, in_sandbox: bool = False, ctx: Context | tuple = None) -> PurePath:
    """
    Get the workspace path for a specific service (e.g. MCP server).
    If `service_name` is None, then the path to entire workspace folder (as mounted to a sandbox) is returned.
    If `in_sandbox` is True, it returns a path in sandbox, e.g.: `/workspace/mcp_repl`.
    If `in_sandbox` is False, it returns the path based on user and session IDs in the format:
    `<DATA_DIR>/workspaces/<user_id>/<session_id>/<service_name>`, where `DATA_DIR` should come from
    the environment variables, e.g.:
    `/data/workspaces/foo-user/bar-session/mcp_repl`.
    The `ctx` is used to get user and session IDs tuple. It can be passed directly or via HTTP headers from `Context`.
    If `ctx` is None, the current FastMCP request HTTP headers are used.

    Args:
        ctx: The FastMCP context, which contains the user session.
        service_name: The name of the service (e.g. "mcp_server").
        in_sandbox: If True, use a sandbox path; otherwise, use user/session-based path.

    Returns: The workspace path as a PurePath object.
    """
    if in_sandbox:
        path = CONTAINER_WORKSPACE_PATH
    else:
        user_id, session_id = ctx if isinstance(ctx, tuple) else get_session_id_tuple(ctx)
        path = WORKSPACES_ROOT_DIR / user_id / session_id
    if service_name:
        path = path / service_name
    return path


def container_to_host_path(path: PurePosixPath, *, ctx: Context | tuple = None) -> Path | None:
    """
    Convert a path in a sandbox container to a host path

    Args:
        container_path: Path inside the container (must be a subdir of CONTAINER_WORKSPACE_PATH).
        user_id: ID of the user.
        session_id: ID of the session.

    Returns:
        Path to the file on the host, or None if the conversion fails.
    """
    old_root = CONTAINER_WORKSPACE_PATH
    new_root = get_workspace_path(ctx=ctx)
    try:
        return new_root / PurePosixPath(path).relative_to(old_root)
    except ValueError as e:
        raise ValueError(f"Container path must be a subdir of '{old_root}', got '{path}' instead") from e


def host_to_container_path(path: Path, *, ctx: Context | tuple = None) -> PurePosixPath:
    """Convert a host path to a path in a sandbox container."""
    old_root = get_workspace_path(ctx=ctx)
    new_root = CONTAINER_WORKSPACE_PATH
    try:
        return new_root / Path(path).relative_to(old_root)
    except ValueError as exc:
        raise ValueError(f"Host path must be a subdir of '{old_root}', got '{path}' instead") from exc
