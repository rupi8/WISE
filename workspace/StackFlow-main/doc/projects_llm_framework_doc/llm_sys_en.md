# llm-sys

The basic service unit of StackFlow, providing external serial and TCP channels and some system function services, while internally handling port resource allocation and a simple in-memory database.

## External API
- sys.ping: Test if communication with the LLM is possible.
- sys.lsmode: Models that have existed in the system in the past.
- sys.bashexec: Execute bash commands.
- sys.hwinfo: Retrieve onboard CPU, memory, and temperature parameters of the LLM.
- sys.uartsetup: Set serial port parameters, effective for a single session.
- sys.reset: Reset the entire LLM framework application.
- sys.reboot: Restart the system.
- sys.version: Get the version of the LLM framework program.

## Internal API
- sql_select: Query key-value pairs in the small in-memory KV database.
- register_unit: Register a unit.
- release_unit: Release a unit.
- sql_set: Set key-value pairs in the small in-memory KV database.
- sql_unset: Delete key-value pairs in the small in-memory KV database.