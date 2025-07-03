import asyncio
from typing import Tuple


async def async_run_command(*args, timeout: float = 5) -> Tuple[int, str, str]:
    """Safe asynchronous command execution tool"""
    proc = await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        if proc.returncode is None:
            raise RuntimeError("Process finished but returncode is None")
        return proc.returncode, stdout.decode(), stderr.decode()
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise RuntimeError("Command timed out")
    except Exception as e:
        proc.kill()
        await proc.wait()
        raise e
