# TraceForest

> High-performance Python profiler that generates interactive call tree visualizations to identify execution bottlenecks.

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

TraceForest is a blazing-fast Python profiler that captures function calls in real-time and presents them as beautiful, interactive tree visualizations. Perfect for identifying performance bottlenecks and understanding code execution flow.

## Features

- **Real-time profiling** - Captures function calls as they happen
- **Interactive trees** - Beautiful hierarchical visualizations
- **Modern web interface** - Clean, responsive design with dark theme
- **Detailed metrics** - Precise timing information for each function
- **Deep call analysis** - See the complete execution path
- **Persistent storage** - Save and share profiling sessions
- **Zero configuration** - Start profiling with just a few lines of code

## Quick Start

### Installation

```bash
pip install traceforest
```

### Basic Usage

```python
from traceforest import Profiler

# Create profiler instance
profiler = Profiler()

# Start profiling
profiler.start()

# Your code here
def slow_function():
    import time
    time.sleep(1)
    return "done"

result = slow_function()

# Stop profiling and view results
profiler.stop()
profiler.export()
```

### Web Visualization

After running `export()`, TraceForest will:
1. Generate a unique profiling session
2. Open your browser to view the interactive tree

## Detailed Usage

### Profiling Classes and Methods

```python
from traceforest import Profiler

class MyClass:
    def method_a(self):
        time.sleep(0.5)
        self.method_b()
    
    def method_b(self):
        time.sleep(0.2)

profiler = Profiler()
profiler.start()

obj = MyClass()
obj.method_a()

profiler.stop()
profiler.export()
```

## Web Interface

The web interface provides:

- **Interactive tree navigation** - Click to expand/collapse branches
- **Visual performance bars** - See relative execution times at a glance
- **Detailed timing information** - Precise millisecond measurements


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
