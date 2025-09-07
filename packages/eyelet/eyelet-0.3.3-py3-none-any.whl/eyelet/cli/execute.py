"""Hook execution command - the main runtime endpoint"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console

from eyelet.application.services import ExecutionService, WorkflowService
from eyelet.domain.models import HookExecution
from eyelet.infrastructure.database import get_db_path
from eyelet.infrastructure.repositories import SQLiteExecutionRepository
from eyelet.services.config_service import ConfigService
from eyelet.services.hook_logger import HookLogger

console = Console()


def create_eyelet_log_entry_legacy(input_data, start_time, project_dir=None):
    """Legacy JSON file logging - kept for compatibility"""
    if project_dir is None:
        project_dir = Path.cwd()

    # Extract hook information
    hook_type = input_data.get("hook_event_name", "unknown")
    tool_name = input_data.get("tool_name", "")

    # Build directory structure
    # Format: ./eyelet-hooks/{hook_type}/{tool_name}/{date}/
    eyelet_dir = project_dir / "eyelet-hooks"

    if hook_type in ["PreToolUse", "PostToolUse"] and tool_name:
        log_dir = eyelet_dir / hook_type / tool_name / start_time.strftime("%Y-%m-%d")
    elif hook_type == "PreCompact":
        compact_type = input_data.get("compact_type", "unknown")
        log_dir = (
            eyelet_dir / hook_type / compact_type / start_time.strftime("%Y-%m-%d")
        )
    else:
        # For hooks without tools (Notification, UserPromptSubmit, Stop, etc.)
        log_dir = eyelet_dir / hook_type / start_time.strftime("%Y-%m-%d")

    # Create directory structure
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create filename with full timestamp
    # Format: YYYYMMDD_HHMMSS_microseconds_{hook_type}_{tool_name}.json
    timestamp_str = start_time.strftime("%Y%m%d_%H%M%S_%f")
    if tool_name:
        filename = f"{timestamp_str}_{hook_type}_{tool_name}.json"
    else:
        filename = f"{timestamp_str}_{hook_type}.json"

    log_file = log_dir / filename

    # Prepare comprehensive log data
    log_data = {
        "timestamp": start_time.isoformat(),
        "timestamp_unix": start_time.timestamp(),
        "hook_type": hook_type,
        "tool_name": tool_name,
        "session_id": input_data.get("session_id", "unknown"),
        "transcript_path": input_data.get("transcript_path", ""),
        "cwd": input_data.get("cwd", os.getcwd()),
        "environment": {
            "python_version": sys.version,
            "platform": sys.platform,
            "eyelet_version": "0.2.0",  # TODO: Import from __version__
            "env_vars": {
                k: v
                for k, v in os.environ.items()
                if k.startswith(("CLAUDE", "EYELET", "ANTHROPIC"))
            },
        },
        "input_data": input_data,
        "metadata": {
            "log_file": str(log_file),
            "log_dir": str(log_dir),
            "project_dir": str(project_dir),
        },
    }

    # Write the log file
    with open(log_file, "w") as f:
        json.dump(log_data, f, indent=2, default=str)

    return log_file, log_data


@click.command()
@click.option("--workflow", help="Workflow to execute")
@click.option("--log-only", is_flag=True, help="Only log, no processing")
@click.option("--log-result", is_flag=True, help="Log result after execution")
@click.option("--debug", is_flag=True, help="Enable debug output")
@click.option("--no-logging", is_flag=True, help="Disable all logging")
@click.option("--legacy-log", is_flag=True, help="Use legacy JSON file logging only")
@click.pass_context
def execute(ctx, workflow, log_only, log_result, debug, no_logging, legacy_log):
    """
    Execute as a hook endpoint - Man the guns!

    This command is called by Claude Code when hooks are triggered.
    It reads JSON from stdin and processes according to configuration.
    """
    start_time = datetime.now()

    # Read input from stdin
    try:
        if sys.stdin.isatty():
            # For testing: if no stdin, create sample data
            input_data = {
                "hook_event_name": "test",
                "test_mode": True,
                "timestamp": start_time.isoformat(),
            }
        else:
            input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        if debug:
            console.print(f"[red]Failed to parse JSON input: {e}[/red]")
        # Still log what we received
        input_data = {
            "hook_event_name": "parse_error",
            "error": str(e),
            "raw_input": sys.stdin.read() if not sys.stdin.isatty() else "no input",
        }
    except Exception as e:
        if debug:
            console.print(f"[red]Failed to read input: {e}[/red]")
        input_data = {"hook_event_name": "read_error", "error": str(e)}

    # Initialize configuration and logging
    project_dir = ctx.obj.get("config_dir", Path.cwd()) if ctx.obj else Path.cwd()

    # Log using new unified system (unless disabled)
    hook_logger = None
    hook_data = None
    if not no_logging and not legacy_log:
        try:
            config_service = ConfigService(project_dir)
            hook_logger = HookLogger(config_service, project_dir)

            # Create hook data and log it
            hook_data = hook_logger._create_hook_data(input_data, start_time)
            log_results = hook_logger.log_hook(input_data, start_time)

            if debug:
                console.print(f"[dim]Logged to: {log_results}[/dim]")
        except Exception as e:
            if debug:
                console.stderr = True
                console.print(f"[yellow]Unified logging failed: {e}[/yellow]")
                console.stderr = False
            # Fall back to legacy logging if requested
            legacy_log = True

    # Legacy JSON file logging (if enabled or as fallback)
    log_file = None
    if not no_logging and legacy_log:
        try:
            log_file, log_data = create_eyelet_log_entry_legacy(
                input_data, start_time, project_dir
            )
            if debug:
                console.print(f"[dim]Legacy log created: {log_file}[/dim]")
        except Exception as e:
            if debug:
                console.print(f"[yellow]Legacy logging failed: {e}[/yellow]")

    # Extract hook information
    hook_type = input_data.get("hook_event_name", "unknown")
    tool_name = input_data.get("tool_name", None)

    # Create execution record
    execution = HookExecution(
        hook_id=f"{hook_type}_{tool_name or 'general'}",
        hook_type=hook_type,
        tool_name=tool_name,
        input_data=input_data,
        status="running",
    )

    # Initialize services
    execution_service = ExecutionService(SQLiteExecutionRepository(get_db_path()))

    try:
        # Record execution start
        execution = execution_service.record_execution(execution)

        if debug:
            console.print(f"[dim]Hook: {hook_type}, Tool: {tool_name}[/dim]")

        # Process based on options
        if log_only:
            # Just log and exit successfully
            execution.status = "success"
            execution.output_data = {"action": "logged"}

        elif log_result:
            # Log the result of a previous execution
            execution.status = "success"
            execution.output_data = {"action": "result_logged"}

        elif workflow:
            # Execute specified workflow
            workflow_service = WorkflowService(Path.cwd() / "workflows")

            try:
                result = workflow_service.execute_workflow(workflow, input_data)
                execution.status = "success"
                execution.output_data = result
            except Exception as e:
                execution.status = "error"
                execution.error_message = str(e)
                if debug:
                    console.print(f"[red]Workflow error: {e}[/red]")

        else:
            # Default processing
            execution.status = "success"
            execution.output_data = {"action": "processed"}

        # Calculate duration
        execution.duration_ms = int(
            (datetime.now() - start_time).total_seconds() * 1000
        )

        # Update execution record
        execution_service.record_execution(execution)

        # Update logs with results
        if hook_logger and hook_data:
            try:
                hook_logger.update_hook_result(
                    hook_data,
                    status=execution.status,
                    duration_ms=execution.duration_ms,
                    output_data=execution.output_data,
                    error_message=execution.error_message,
                )
            except Exception as e:
                if debug:
                    console.print(f"[yellow]Failed to update hook result: {e}[/yellow]")

        # Update legacy log if used
        if log_file:
            try:
                # Read existing log
                with open(log_file) as f:
                    final_log_data = json.load(f)

                # Add execution results
                final_log_data["execution"] = {
                    "status": execution.status,
                    "duration_ms": execution.duration_ms,
                    "output_data": execution.output_data,
                    "error_message": execution.error_message,
                }
                final_log_data["completed_at"] = datetime.now().isoformat()

                # Write updated log
                with open(log_file, "w") as f:
                    json.dump(final_log_data, f, indent=2, default=str)
            except Exception as e:
                if debug:
                    console.print(f"[yellow]Failed to update Eyelet log: {e}[/yellow]")

        # Output any required response
        if execution.output_data and not log_only:
            # Check for blocking response
            if execution.output_data.get("block", False):
                # Return error code to block the action
                if debug:
                    console.print("[yellow]Blocking action[/yellow]")
                sys.exit(2)

            # Check for response data
            if "response" in execution.output_data:
                print(json.dumps(execution.output_data["response"]))

        # Success
        sys.exit(0)

    except Exception as e:
        # Record failure
        execution.status = "error"
        execution.error_message = str(e)
        execution.duration_ms = int(
            (datetime.now() - start_time).total_seconds() * 1000
        )

        try:
            execution_service.record_execution(execution)
        except Exception:
            pass  # Don't fail on logging errors

        # Update logs with error
        if hook_logger and hook_data:
            try:
                hook_logger.update_hook_result(
                    hook_data,
                    status="error",
                    duration_ms=execution.duration_ms,
                    output_data={},
                    error_message=str(e),
                )
            except Exception:
                pass

        # Update legacy log with error if used
        if log_file:
            try:
                with open(log_file) as f:
                    final_log_data = json.load(f)

                final_log_data["execution"] = {
                    "status": "error",
                    "duration_ms": execution.duration_ms,
                    "error": str(e),
                    "error_type": type(e).__name__,
                }
                final_log_data["completed_at"] = datetime.now().isoformat()

                with open(log_file, "w") as f:
                    json.dump(final_log_data, f, indent=2, default=str)
            except Exception:
                pass

        if debug:
            console.print(f"[red]Execution error: {e}[/red]")

        # Exit with success to not disrupt Claude Code
        sys.exit(0)
