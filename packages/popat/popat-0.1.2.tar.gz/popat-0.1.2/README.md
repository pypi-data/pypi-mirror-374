# Popat - The Intelligent Terminal Error Helper

**Advanced error detection and analysis for developers**

Popat is an intelligent coding assistant that automatically intercepts programming errors and provides helpful, context-aware responses to enhance debugging efficiency and reduce development time.

## What Makes Popat Special?

Popat transforms the debugging experience by providing an intelligent assistant that watches your code, catches every error, and responds with personalized guidance. Whether you're a beginner learning to code or an experienced developer working on complex projects, Popat transforms frustrating error messages into clear, actionable insights.

## Key Features

- **Automatic Error Detection**: Runs silently in background, catching errors from 25+ programming languages
- **5 Response Personalities**: Choose your debugging companion (Encouraging, Sarcastic, Educational, Professional, Silly)
- **Adaptive Learning**: Gets smarter about your coding patterns and provides personalized assistance
- **Universal Shell Integration**: Works seamlessly with bash, zsh, fish, PowerShell, and cmd
- **Comprehensive Language Support**: Deep error pattern recognition for Python, JavaScript, Rust, Java, C++, Go, and more
- **Progress Tracking**: Monitors error patterns, learning progress, and coding improvement over time
- **Zero-Configuration**: Works out of the box with intelligent defaults
- **Rich Terminal Output**: Beautiful colors and formatted suggestions

## Installation

### Option 1: Quick Install (Recommended)
```bash
# Install via pip (includes Rust binary)
pip install popat
```

### Option 2: From Source
```bash
# Clone and build from source
git clone https://github.com/your-repo/popat
cd popat
cargo build --release
```

### Option 3: Direct Binary
Download pre-built binaries from [GitHub Releases](https://github.com/your-repo/popat/releases)

## Getting Started

### Step 1: Start Popat Daemon

**For enhanced personality responses:**
```bash
popat start --noise
```

**For standard mode:**
```bash
popat start
```

### Step 2: Code Normally - Popat Monitors Everything

Once started, Popat automatically catches and responds to ANY error:

```python
# Try this Python code with a NameError:
python -c "print(undefined_variable)"
# Popat provides context-aware suggestions and fixes
```

```javascript
# Try this JavaScript code with a TypeError:
node -e "console.log('hello' + undefined.property)"
# Popat analyzes and explains the error with solutions
```

### Step 3: Stop When Done
```bash
popat stop
```

## Complete Command Reference

### Daemon Control
```bash
# Start with enhanced personality
popat start --noise

# Start with standard personality
popat start

# Stop daemon
popat stop

# Check daemon status
popat status
```

### Direct Error Analysis
```bash
# Analyze specific error message
popat analyze "NameError: name 'x' is not defined" --language python

# Analyze error from file
popat analyze --file error.log --language javascript

# Auto-detect language (when possible)
popat analyze "compilation terminated."

# Override personality for single analysis
popat analyze "SyntaxError" --personality sarcastic

# Enable verbose output
popat --verbose analyze "TypeError" --language python
```

### Configuration Management
```bash
# View current configuration
popat config --show

# Set personality
popat config --personality sarcastic

# Configure UI preferences
popat config --emoji true --colors auto

# Enable/disable learning
popat config --learning true

# View version information
popat --version
```

### Shell Integration & Setup
```bash
# Set up shell integration
popat setup --shell bash     # For bash
popat setup --shell zsh      # For zsh  
popat setup --shell fish     # For fish
popat setup --shell powershell # For PowerShell

# Remove shell integration
popat setup --remove
```

### Statistics and Learning
```bash
# View your error statistics
popat stats

# View detailed statistics
popat stats --detailed

# Reset learning data
popat stats --reset
```

### Language-Specific Commands
```bash
# Run Python with automatic error detection
popat python -c "print(undefined_var)"
popat python script.py

# Run Node.js with automatic error detection
popat node -e "console.log(missing_var)"
popat node app.js

# Run Cargo with automatic error detection
popat cargo build
popat cargo test
```

### Diagnostics and Logs
```bash
# Run diagnostic checks
popat doctor

# View recent logs
popat logs --tail 50

# Follow live logs
popat logs --follow

# Show usage examples
popat examples
```

### Interactive and Testing
```bash
# Interactive mode for testing responses
popat interactive

# Test specific error types
popat interactive --error-type NameError

# Test with specific personality
popat interactive --personality sarcastic

# Get help for any command
popat --help
popat analyze --help
popat config --help
```

## Available Response Personalities

Choose the companion that matches your preferred interaction style:

### **Encouraging** - Supportive Assistant
```
Popat: "You're so close! Just need to define 'variable' first!"
Solution: "Check if you meant a different variable name"
Tip: "Use your IDE's autocomplete to avoid typos!"
```

### **Sarcastic** - Direct Expert
```
Popat: "Oh please... 'undefined_variable' doesn't exist and you know it!"
Solution: "Maybe try DEFINING 'undefined_variable' first? Revolutionary idea!"
Note: "Reality check: Variables don't magically appear!"
```

### **Educational** - Patient Teacher
```
Popat: "NameError occurs when Python can't find 'variable' in the current scope."
Solution: "Define 'variable' in the appropriate scope"
Learning: "Python has lexical scoping rules"
```

### **Professional** - Business Consultant  
```
Popat: "NameError: Variable 'x' is not defined in the current scope."
Solution: "Declare variable 'x' before use"
Recommendation: "Use consistent naming conventions"
```

### **Silly** - Comic Relief
```
Popat: "BEEP BOOP! 'variable' has vanished into the digital void!"
Solution: "Summon 'variable' into existence with some code magic!"
Tip: "Variables need to be conjured before use!"
```

## Advanced Usage

### Background Monitoring
Once you run `popat start`, Popat will:
- Monitor all terminal commands automatically
- Detect errors from any programming language
- Provide instant, context-aware suggestions
- Learn from your patterns to improve over time

### Shell Integration
Popat integrates deeply with your shell to catch errors automatically:

```bash
# Bash/Zsh users
popat setup --shell bash
source ~/.bashrc  # or ~/.zshrc

# Fish users  
popat setup --shell fish

# PowerShell users
popat setup --shell powershell
```

### Language Support
Popat automatically detects and supports:
- **Python**: SyntaxError, NameError, IndentationError, ImportError
- **JavaScript/Node.js**: ReferenceError, TypeError, SyntaxError
- **Rust**: Compilation errors, linker errors
- **Java**: Compilation errors, runtime exceptions
- **C/C++**: Compilation errors, linker errors
- **Go**: Compilation errors, runtime panics

## Configuration

Popat stores its configuration in your system's config directory. You can customize:

- Personality type
- Language preferences  
- UI settings (colors, support)
- Privacy settings
- Learning behavior

## How It Works

1. **Background Monitoring**: Popat runs as a lightweight daemon process
2. **Error Interception**: Shell hooks capture command outputs and error codes
3. **Pattern Matching**: Advanced regex and context analysis identify error types
4. **Response Generation**: AI-powered system generates personalized, helpful responses
5. **Learning**: User interactions are analyzed to improve future suggestions

## Troubleshooting

### Common Issues & Solutions

**Q: `popat start --noise` doesn't work**
```bash
# Make sure Popat is properly installed
popat --version

# Run diagnostics to check installation
popat doctor

# Check if daemon is already running
popat status

# Try rebuilding if installed from source
cargo build --release
```

**Q: Not detecting Python errors automatically**
```bash
# Use Popat wrapper commands for immediate detection
popat python -c "print(undefined_var)"

# Or ensure shell integration is set up
popat setup --shell bash  # or your shell

# Test with direct analysis
popat analyze "NameError: test" --language python

# Check diagnostics
popat doctor
```

**Q: Responses are not engaging enough**
```bash
# Make sure you're using the enhanced mode
popat stop
popat start --noise  # This enables enhanced personality!

# Or set sarcastic as default
popat config --personality sarcastic

# Verify current configuration
popat config --show
```

**Q: Shell integration not working**
```bash
# Reload your shell after setup
source ~/.bashrc   # bash
source ~/.zshrc    # zsh
exec fish          # fish

# Or restart your terminal entirely
```

**Q: Permission errors on Windows**
```bash
# Run PowerShell as Administrator for initial setup
# Then use regular terminal for normal operation
```

### Debug Mode
```bash
# Run with verbose output to see what's happening
popat --verbose analyze "test error" --language python

# Run comprehensive diagnostics
popat doctor

# Check daemon logs
popat logs --tail 50

# Follow live logs for real-time debugging
popat logs --follow
```

## Quick Start Summary

**The command that enables intelligent error monitoring:**

```bash
popat start --noise
```

This single command:
- Starts background monitoring
- Enables enhanced personality responses  
- Automatically catches ALL programming errors
- Provides context-aware help with engaging responses
- Learns your patterns to get better over time

**Then just code normally** - Popat handles the rest!

## Contributing

Join our mission to make debugging more efficient! We welcome:

- **Bug Reports**: Found an issue? Let us know!
- **Feature Requests**: Have ideas? We want to hear them!
- **Language Support**: Help add more programming languages  
- **Response Improvements**: Make responses even more helpful
- **Documentation**: Improve guides and examples
- **Testing**: Add test cases for edge cases

### Quick Contribution Guide
```bash
# Fork and clone
git clone https://github.com/your-username/popat
cd popat

# Make changes
# Add tests
# Update documentation

# Test your changes
cargo test
cargo build --release

# Submit PR with detailed description
```

## License & Legal

**MIT License** - Use Popat freely in personal and commercial projects.

See [LICENSE](LICENSE) for full terms.

## Credits & Acknowledgments

Built with dedication and expertise using:

- **Rust** - For blazing fast performance and memory safety
- **Python** - For easy installation and cross-platform compatibility  
- **SQLite** - For local data storage and learning persistence
- **Crossterm** - For beautiful colored terminal output
- **Clap** - For powerful CLI argument parsing

**Special thanks to:**
- Every developer who's ever stared at a confusing error message
- The Rust community for amazing tools and libraries
- Beta testers who helped make Popat better
- Coffee shops that fuel late-night coding sessions

---

## Ready to Transform Your Debugging Experience?

**Stop struggling with cryptic error messages!**

Install Popat today and get an intelligent coding companion:

```bash
pip install popat
popat start --noise
```

**Your code errors will never be confusing again!**

*Happy debugging! - The Popat Team*

## Complete Command Summary

| Command | Description | Example |
|---------|-------------|----------|
| `popat start` | Start daemon (normal) | `popat start` |
| `popat start --noise` | Start daemon (enhanced) | `popat start --noise` |
| `popat stop` | Stop daemon | `popat stop` |
| `popat status` | Check daemon status | `popat status` |
| `popat analyze` | Analyze error | `popat analyze "NameError"` |
| `popat config` | Manage settings | `popat config --show` |
| `popat python` | Run Python with detection | `popat python script.py` |
| `popat node` | Run Node.js with detection | `popat node app.js` |
| `popat cargo` | Run Cargo with detection | `popat cargo build` |
| `popat setup` | Configure shell integration | `popat setup --shell bash` |
| `popat stats` | View statistics | `popat stats --detailed` |
| `popat interactive` | Interactive testing mode | `popat interactive` |
| `popat logs` | View daemon logs | `popat logs --tail 50` |
| `popat doctor` | Run diagnostics | `popat doctor` |
| `popat examples` | Show usage examples | `popat examples` |
| `popat --version` | Show version info | `popat --version` |
| `popat --verbose` | Enable verbose mode | `popat --verbose analyze` |

## Language Support Matrix

| Language | Error Types Supported | Detection Level | Wrapper Available |
|----------|----------------------|-----------------|-------------------|
| **Python** | 25+ (NameError, TypeError, SyntaxError, IndentationError, ImportError, etc.) | Expert | `py.bat` |
| **JavaScript/Node.js** | TypeError, ReferenceError, SyntaxError, RangeError | Expert | `js.bat` |
| **Rust** | Compilation errors, borrow checker, linker errors | Good | Planned |
| **Java** | CompilationError, RuntimeException, ClassNotFound | Good | Planned |
| **C/C++** | Compilation errors, linker errors, segfaults | Good | Planned |
| **Go** | Compilation errors, runtime panics | Good | Planned |
| **PHP** | Parse errors, fatal errors | Basic | Planned |
| **Ruby** | SyntaxError, NameError, NoMethodError | Basic | Planned |

### Python Error Coverage (25+ Types)
```
NameError           TypeError            ValueError
KeyError            IndexError          AttributeError 
SyntaxError         IndentationError    TabError
ImportError         ModuleNotFoundError FileNotFoundError
PermissionError     RecursionError      ZeroDivisionError
AssertionError      UnboundLocalError   OverflowError
MemoryError         KeyboardInterrupt   SystemExit
StopIteration       GeneratorExit       FloatingPointError
```

## Advanced Features

### Automatic Background Monitoring
Once you run `popat start --noise`, Popat will:
- **Monitor Everything**: All terminal commands across all languages
- **Instant Detection**: Catches errors the moment they happen
- **Context Awareness**: Understands error context and provides relevant suggestions
- **Adaptive Learning**: Gets smarter about your coding patterns over time
- **Zero Interference**: Runs silently without affecting performance

### Deep Shell Integration
Popat integrates seamlessly with your development environment:

```bash
# Bash/Zsh users - One-time setup
popat setup --shell bash
source ~/.bashrc  # Reload shell

# Fish users
popat setup --shell fish

# PowerShell users (Windows)
popat setup --shell powershell
```

After setup, Popat automatically intercepts errors from:
- Direct command execution (`python script.py`)
- Build systems (`make`, `cargo build`, `npm run`)
- Package managers (`pip install`, `npm install`)
- Any command that produces stderr output

## Configuration & Customization

Popat stores configuration in your system's config directory and can be customized via:

```bash
# Set default personality
popat config --personality sarcastic

# Configure UI preferences
popat config --emoji true --colors auto

# Privacy settings
popat config --learning true --telemetry false

# Language preferences
popat config --primary-language python --secondary-language javascript

# View current settings
popat config --show
```

### Configuration Options
- **Personality Types**: encouraging, sarcastic, educational, professional, silly
- **UI Settings**: colors (auto/always/never), emoji support, output format
- **Learning Behavior**: adaptive responses, error pattern tracking, progress monitoring
- **Privacy Controls**: local-only data, telemetry opt-out, anonymous usage stats
- **Language Priorities**: Primary and secondary language detection preferences

## How Popat Works (Under the Hood)

1. **Background Monitoring**: Lightweight daemon process watches terminal activity
2. **Error Interception**: Shell hooks capture command outputs and exit codes  
3. **Pattern Matching**: Advanced regex engine analyzes error messages for type and context
4. **Response Generation**: Personality engine generates contextual, helpful responses
5. **Machine Learning**: User interaction patterns improve future suggestions
6. **Local Storage**: SQLite database stores learning data and user preferences locally

### Architecture Overview
```
Terminal Command → Shell Hook → Error Detection → Pattern Analysis → Response Generation → User Display
                                      ↓
                              SQLite Learning DB ← Feedback Loop ← User Interaction
```

## Performance & Requirements

- **Memory Usage**: ~5-10MB RAM (daemon mode)
- **CPU Impact**: <1% during normal operation
- **Startup Time**: <100ms for daemon initialization
- **Response Time**: <50ms for error analysis and response
- **Storage**: ~1-5MB for learning database
- **Requirements**: 
  - Rust 1.60+ (for building from source)
  - Python 3.7+ (for pip installation)
  - 50MB disk space
