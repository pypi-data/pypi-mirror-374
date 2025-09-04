# Mission Statement

## fdprof: Whole Process File Descriptor Monitoring

### Core Mission
fdprof is designed to monitor **entire processes** and their file descriptor usage from the **outside**. It operates as a process wrapper that observes and analyzes file descriptor patterns at the operating system level.

### Design Philosophy
- **External monitoring only**: fdprof wraps and monitors processes, it does not require code changes
- **Whole process scope**: Monitor the complete lifecycle of a process and all its file descriptors
- **Non-intrusive**: No code instrumentation, decorators, or application modifications required
- **Operating system level**: Leverage OS-level tools (psutil) for accurate FD tracking

### What fdprof IS:
✅ A process wrapper for FD monitoring
✅ An external analysis tool
✅ A command-line utility
✅ A visualization and plotting tool
✅ A debugging aid for resource leaks

### What fdprof is NOT:
❌ An application framework
❌ A library for embedding in other code
❌ A decorator-based monitoring system
❌ An APM (Application Performance Monitoring) platform
❌ A profiler requiring code changes

### Scope Boundaries
To prevent scope creep, fdprof will **NOT** include:
- Python decorators or context managers
- Code instrumentation libraries
- In-process monitoring hooks
- Application framework integration
- Complex configuration systems
- Database persistence layers
- Web dashboards or APIs
- Real-time streaming interfaces

### Event Logging Exception
The **only** application-level integration fdprof supports is optional event logging via stdout:
```python
print(f"EVENT: {time.time():.9f} message")
```

This is acceptable because:
- It uses standard output (no special libraries)
- It's completely optional
- It doesn't change application logic
- It works with any language, not just Python

### Success Criteria
fdprof succeeds when users can:
1. Wrap any command: `fdprof mycommand args`
2. Get immediate FD insights without code changes
3. Identify resource leaks through visualization
4. Debug process behavior with minimal setup
5. Understand FD patterns across process lifecycle

### Anti-Pattern Examples
These would violate our mission:
```python
# DON'T: Decorators
@fdprof.monitor
def my_function():
    pass

# DON'T: Context managers
with fdprof.monitoring():
    do_work()

# DON'T: Explicit instrumentation
fdprof.track_fd_open(filename)
```

### The Right Way
```bash
# DO: External process monitoring
fdprof python my_script.py
fdprof --plot gunicorn app:app
fdprof java -jar myapp.jar
```

This mission ensures fdprof remains focused, simple, and universally applicable to any process, regardless of programming language or framework.
