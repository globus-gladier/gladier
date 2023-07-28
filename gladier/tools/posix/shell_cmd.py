from __future__ import annotations

import typing as t

from gladier import JSONObject
from gladier.tools.globus import GlobusComputeState, ComputeFunctionType


def shell_cmd(
    args,
    arg_sep_char=" ",
    capture_output=False,
    cwd=None,
    env=None,
    timeout=60,
    exception_on_error=True,
    input_path=None,
    output_path=None,
    error_path=None,
    **kwargs,
):
    import os
    import subprocess

    # If the args are provided as a string (instead of a list), separate them
    # into a list removing dupes of the separator char
    if isinstance(args, str):
        args = [a for a in args.split(arg_sep_char) if len(a) > 0]

    assert env is None or isinstance(env, dict)
    assert timeout is None or isinstance(timeout, int)
    assert input_path is None or isinstance(input_path, str)
    assert output_path is None or (
        isinstance(output_path, str) and capture_output is False
    )
    assert error_path is None or (
        isinstance(error_path, str) and capture_output is False
    )

    if cwd is not None:
        cwd = os.path.expanduser(cwd)

    if input_path is not None:
        input_path = os.path.expanduser(input_path)

    run_args = {
        "args": " ".join(args),
        "shell": True,
        "cwd": cwd,
        "timeout": timeout,
        "check": exception_on_error,
        "capture_output": capture_output,
        "env": env,
    }
    if capture_output:
        run_args["text"] = True

    # Remove Nones from the arguments
    run_args = {k: v for k, v in run_args.items() if v is not None}

    in_file = None
    if input_path is not None:
        in_file = open(input_path, "r")
        run_args["stdin"] = in_file

    out_file = None
    if output_path is not None:
        out_file = open(output_path, "w")
        run_args["stdout"] = out_file

    err_file = None
    if error_path is not None:
        err_file = open(error_path, "w")
        run_args["stderr"] = err_file

    try:
        res = subprocess.run(**run_args)

    finally:
        if in_file is not None:
            in_file.close()
        if out_file is not None:
            out_file.close()
        if err_file is not None:
            err_file.close()

    return res.returncode, res.stdout, res.stderr


class ShellCmdState(GlobusComputeState):
    cmd_args: t.Union[t.List[str], str]
    capture_output: bool = False
    cwd: t.Optional[str] = None
    env: t.Optional[str] = None  # TODO, maybe this is list[str]
    timeout: int = 60
    exception_on_error: bool = True
    input_path: t.Optional[str] = None
    output_path: t.Optional[str] = None
    error_path: t.Optional[str] = None
    function_to_call: ComputeFunctionType = shell_cmd
    function_parameters: t.Union[t.Dict[str, t.Any], str] = ""

    """Run a command in a shell with various options. Suitable for use as a
    Globus Compute function. On anything other than exit success (returning 0), an
    exception will be raised, the stack trace will be propogated, and the flow
    will be halted. On exit success, the return code, stdout, and sterr are returned
    in a list in the format:

    [0, "Standard Output Text", "Standard Error Text"]

    Note: stdout and sterr will always be None unless ``capture_output`` is set.



    Args:
        args: Arguments to the command. Can be either a list of strings
            containing command and parameters, or a single string with command
            and parameters together.
        arg_sep_char: If the args val is a string, the character that separates
            the various arguments. By default, it is space.
        capture_output: Whether output should be captured. If so, the return
            value will contain captured text. Beware of capturing too much text,
            especially in funcx and Globus Flows use cases where output size is
            limited.
        cwd: [Optional] The directory to run the command from. When used in funcx,the
            run directory may be unpredictable based on how the funcx endpoint is
            started and configured.
        env: [Optional] A dictionary of environment variables to set
        timeout: How long the command should be allowed to run. Default is 60
            seconds.
        exception_on_error: If the command fails, should an exception be raised
            or should just the (presumably non-zero) return code be returned.
            Defaults to True.
        input_path: A path to a file which should be used as the standard input
            to the command. When not provided, stdin does not exist so attempts
            to read from it will result in an error.
        output_path: A path to a file which should be used to capture the output
            (stdout) of the command. This cannot be set if `capture_output` is set.
        error_path: A path to a file which should be used to capture the error output
            (stderr) of the command. This cannot be set if `capture_output` is set.
        **kwargs:
        nil:

    Returns:
        A tuple containing the return code of the command execution, the string
        of the standard out and standard error (if capture_output is True)
    """

    def get_flow_definition(self) -> JSONObject:
        self.set_call_params_from_self_model(
            {
                "capture_output",
                "cwd",
                "env",
                "timeout",
                "exception_on_error",
                "input_path",
                "output_path",
                "error_path",
            }
        )
        self.function_parameters["args"] = self.cmd_args
        return super().get_flow_definition()
