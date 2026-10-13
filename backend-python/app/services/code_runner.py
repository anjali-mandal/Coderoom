import asyncio
import shutil
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


RUN_TIMEOUT_SECONDS = 10
MAX_OUTPUT_LENGTH = 20_000


class CodeRunnerError(Exception):
    pass


def _runtime_error(language: str, executable: str) -> CodeRunnerError:
    return CodeRunnerError(
        f"{language} runtime is not installed on the server. "
        f"Install '{executable}' and try again."
    )


async def _run_process(command: list[str], cwd: Path) -> tuple[str, int]:
    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=str(cwd),
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
    except FileNotFoundError as exc:
        raise CodeRunnerError(f"Unable to start the {command[0]} runtime.") from exc

    try:
        output, _ = await asyncio.wait_for(
            process.communicate(),
            timeout=RUN_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError as exc:
        process.kill()
        await process.wait()
        raise CodeRunnerError(
            f"Execution timed out after {RUN_TIMEOUT_SECONDS} seconds."
        ) from exc

    text = output.decode("utf-8", errors="replace")
    return text[:MAX_OUTPUT_LENGTH], process.returncode


def _require_runtime(executable: str, language: str) -> str:
    path = shutil.which(executable)
    if not path:
        raise _runtime_error(language, executable)
    return path


async def run_code(language: str, code: str) -> str:
    if language == "css":
        return "CSS is a stylesheet and has no standalone console output. Use the preview to see its styles."

    with TemporaryDirectory(prefix="coderoom-run-") as temp_dir:
        workdir = Path(temp_dir)

        if language == "python":
            source = workdir / "main.py"
            source.write_text(code, encoding="utf-8")
            command = [sys.executable, "-I", str(source)]
        elif language == "javascript":
            runtime = _require_runtime("node", "JavaScript")
            source = workdir / "main.js"
            source.write_text(code, encoding="utf-8")
            command = [runtime, str(source)]
        elif language == "typescript":
            runtime = _require_runtime("node", "TypeScript")
            source = workdir / "main.ts"
            source.write_text(code, encoding="utf-8")
            command = [runtime, "--experimental-strip-types", str(source)]
        elif language == "java":
            runtime = _require_runtime("javac", "Java")
            java_runtime = _require_runtime("java", "Java")
            source = workdir / "Main.java"
            source.write_text(code, encoding="utf-8")
            compile_output, compile_status = await _run_process(
                [runtime, str(source)],
                workdir,
            )
            if compile_status != 0:
                return compile_output or "Java compilation failed."
            command = [java_runtime, "-cp", str(workdir), "Main"]
        elif language == "csharp":
            runtime = _require_runtime("dotnet", "C#")
            source = workdir / "Program.cs"
            project = workdir / "Runner.csproj"
            source.write_text(code, encoding="utf-8")
            project.write_text(
                """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>
</Project>
""",
                encoding="utf-8",
            )
            command = [runtime, "run", "--project", str(project), "--nologo"]
        else:
            raise CodeRunnerError(f"Unsupported language: {language}")

        output, status = await _run_process(command, workdir)
        if status != 0:
            return output or f"{language} execution failed."
        return output or "Program finished without output."
