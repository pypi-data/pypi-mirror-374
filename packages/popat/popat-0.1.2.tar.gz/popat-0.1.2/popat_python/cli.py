#!/usr/bin/env python3
"""
Popat CLI - Python wrapper for the Rust-based error helper
"""
import os
import sys
import subprocess
import signal
import time
import click
from colorama import init, Fore, Style
from pathlib import Path

# Initialize colorama for cross-platform color support
init()

def find_popat_binary():
    """Find the Popat binary in the system"""
    # First check if there's a bundled binary (for pip installs)
    bundled_binary = Path(__file__).parent / ('popat.exe' if os.name == 'nt' else 'popat')
    if bundled_binary.exists():
        return str(bundled_binary)
    
    # Then check if it's in PATH
    if subprocess.run(['where' if os.name == 'nt' else 'which', 'popat'], 
                     capture_output=True).returncode == 0:
        return 'popat'
    
    # Check common installation locations
    possible_paths = [
        Path.home() / '.cargo' / 'bin' / ('popat.exe' if os.name == 'nt' else 'popat'),
        Path('/usr/local/bin/popat'),
        Path('/usr/bin/popat'),
        # Add Windows paths
        Path(os.environ.get('LOCALAPPDATA', '')) / 'Programs' / 'popat' / 'popat.exe',
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path)
    
    return None

@click.group(invoke_without_command=True)
@click.option('--start', 'start_mode', flag_value=True, help='Start daemon mode')
@click.option('--noise', is_flag=True, help='Start with sassy attitude')
@click.option('--version', is_flag=True, help='Show version information')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
@click.pass_context
def main(ctx, start_mode, noise, version, verbose):
    """🦜 Popat - The Funny Terminal Error Helper"""
    
    if version:
        click.echo("🦜 Popat v0.1.0 - The Funny Terminal Error Helper")
        click.echo("Built with ❤️ and lots of ☕")
        return
    
    # Store verbose mode in context for other commands
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    
    if ctx.invoked_subcommand is None:
        if start_mode:
            start_daemon(noise, verbose)
        else:
            # Show help
            click.echo("🦜 Welcome to Popat - The Funny Terminal Error Helper!")
            click.echo()
            click.echo("Usage:")
            click.echo("  popat --start          # Start background monitoring")
            click.echo("  popat --start --noise  # Start with sassy attitude") 
            click.echo("  popat analyze 'error'  # Analyze specific error")
            click.echo("  popat setup            # Set up shell integration")
            click.echo("  popat stop             # Stop background monitoring")
            click.echo()
            click.echo("For full help: popat --help")

@main.command()
@click.option('--noise', is_flag=True, help='Start with sassy attitude')
@click.pass_context
def start(ctx, noise):
    """Start Popat in daemon mode"""
    verbose = ctx.obj.get('verbose', False) if ctx.obj else False
    start_daemon(noise, verbose)

@main.command()
def stop():
    """Stop the background daemon"""
    popat_binary = find_popat_binary()
    if not popat_binary:
        click.echo(f"{Fore.RED}🦜 Popat binary not found! Please install Popat first.{Style.RESET_ALL}")
        sys.exit(1)
    
    try:
        result = subprocess.run([popat_binary, 'stop'], capture_output=True, text=True, encoding='utf-8', errors='replace')
        if result.returncode == 0:
            output = result.stdout.strip() if result.stdout else "Background monitoring stopped"
            click.echo(f"{Fore.CYAN}🦜 {output}{Style.RESET_ALL}")
        else:
            error_msg = result.stderr.strip() if result.stderr else "Failed to stop daemon"
            click.echo(f"{Fore.RED}🦜 Failed to stop daemon: {error_msg}{Style.RESET_ALL}")
    except Exception as e:
        click.echo(f"{Fore.RED}🦜 Error stopping daemon: {e}{Style.RESET_ALL}")

@main.command()
@click.argument('error_text', required=False)
@click.option('--language', '-l', help='Programming language context')
@click.option('--file', '-f', help='File containing the error')
@click.option('--personality', help='Override personality for this analysis')
@click.pass_context
def analyze(ctx, error_text, language, file, personality):
    """Analyze an error message"""
    verbose = ctx.obj.get('verbose', False) if ctx.obj else False
    
    popat_binary = find_popat_binary()
    if not popat_binary:
        click.echo(f"{Fore.RED}🦜 Popat binary not found! Please install Popat first.{Style.RESET_ALL}")
        sys.exit(1)
    
    cmd = [popat_binary, 'analyze']
    
    if error_text:
        cmd.extend(['--error', error_text])
    elif file:
        cmd.extend(['--file', file])
    else:
        click.echo(f"{Fore.RED}🦜 Please provide either error text or a file!{Style.RESET_ALL}")
        sys.exit(1)
    
    if language:
        cmd.extend(['--language', language])
    
    if personality:
        cmd.extend(['--personality', personality])
        
    if verbose:
        cmd.append('--verbose')
        click.echo(f"{Fore.CYAN}🦜 Running: {' '.join(cmd)}{Style.RESET_ALL}")
    
    try:
        subprocess.run(cmd, encoding='utf-8', errors='replace')
    except Exception as e:
        click.echo(f"{Fore.RED}🦜 Error running analysis: {e}{Style.RESET_ALL}")

@main.command()
@click.option('--shell', help='Shell type (bash, zsh, fish)')
@click.option('--remove', is_flag=True, help='Remove existing hooks')
def setup(shell, remove):
    """Set up shell integration"""
    popat_binary = find_popat_binary()
    if not popat_binary:
        click.echo(f"{Fore.RED}🦜 Popat binary not found! Please install Popat first.{Style.RESET_ALL}")
        sys.exit(1)
    
    cmd = [popat_binary, 'setup']
    
    if shell:
        cmd.extend(['--shell', shell])
    if remove:
        cmd.append('--remove')
    
    try:
        subprocess.run(cmd)
    except Exception as e:
        click.echo(f"{Fore.RED}🦜 Error setting up shell integration: {e}{Style.RESET_ALL}")

@main.command()
@click.option('--detailed', is_flag=True, help='Show detailed statistics')
@click.option('--reset', is_flag=True, help='Reset all statistics')
def stats(detailed, reset):
    """Show usage statistics"""
    popat_binary = find_popat_binary()
    if not popat_binary:
        click.echo(f"{Fore.RED}🦜 Popat binary not found! Please install Popat first.{Style.RESET_ALL}")
        sys.exit(1)
    
    try:
        cmd = [popat_binary, 'stats']
        if detailed:
            cmd.append('--detailed')
        if reset:
            cmd.append('--reset')
            
        subprocess.run(cmd, encoding='utf-8', errors='replace')
    except Exception as e:
        click.echo(f"{Fore.RED}🦜 Error showing stats: {e}{Style.RESET_ALL}")

@main.command()
@click.option('--error-type', help='Test specific error type')
@click.option('--personality', help='Use specific personality for testing')
def interactive(error_type, personality):
    """Interactive mode for testing"""
    popat_binary = find_popat_binary()
    if not popat_binary:
        click.echo(f"{Fore.RED}🦜 Popat binary not found! Please install Popat first.{Style.RESET_ALL}")
        sys.exit(1)
    
    try:
        cmd = [popat_binary, 'interactive']
        if error_type:
            cmd.extend(['--error-type', error_type])
        if personality:
            cmd.extend(['--personality', personality])
            
        subprocess.run(cmd, encoding='utf-8', errors='replace')
    except Exception as e:
        click.echo(f"{Fore.RED}🦜 Error starting interactive mode: {e}{Style.RESET_ALL}")

def start_daemon(noise=False, verbose=False):
    """Start the Popat daemon"""
    popat_binary = find_popat_binary()
    if not popat_binary:
        click.echo(f"{Fore.RED}🦜 Popat binary not found! Please install Popat first.{Style.RESET_ALL}")
        click.echo(f"{Fore.YELLOW}   You can install it via: cargo install popat{Style.RESET_ALL}")
        sys.exit(1)
    
    if noise:
        click.echo(f"{Fore.MAGENTA}🦜 watching you chill...jeeezzz{Style.RESET_ALL}")
    else:
        click.echo(f"{Fore.CYAN}🦜 Popat daemon starting... ready to catch your mistakes!{Style.RESET_ALL}")
    
    try:
        # Start the daemon
        cmd = [popat_binary, 'start']
        if noise:
            cmd.append('--noise')
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        
        if result.returncode == 0:
            output = result.stdout.strip() if result.stdout else "Daemon started successfully"
            click.echo(f"{Fore.GREEN}🦜 {output}{Style.RESET_ALL}")
            click.echo(f"{Fore.YELLOW}   Now run any code and I'll catch your errors with style!{Style.RESET_ALL}")
            click.echo(f"{Fore.YELLOW}   Use 'popat stop' to disable.{Style.RESET_ALL}")
            
            # Enhanced shell integration
            setup_enhanced_integration()
            
        else:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error occurred"
            click.echo(f"{Fore.RED}🦜 Failed to start daemon: {error_msg}{Style.RESET_ALL}")
            
    except Exception as e:
        click.echo(f"{Fore.RED}🦜 Error starting daemon: {e}{Style.RESET_ALL}")

@main.command(context_settings={'ignore_unknown_options': True})
@click.argument('python_args', nargs=-1, type=click.UNPROCESSED)
def python(python_args):
    """Run Python with automatic error detection"""
    run_with_popat('python', 'python', python_args)

@main.command(context_settings={'ignore_unknown_options': True})
@click.argument('node_args', nargs=-1, type=click.UNPROCESSED)
def node(node_args):
    """Run Node.js with automatic error detection"""
    run_with_popat('node', 'javascript', node_args)

@main.command(context_settings={'ignore_unknown_options': True})
@click.argument('cargo_args', nargs=-1, type=click.UNPROCESSED)
def cargo(cargo_args):
    """Run Cargo with automatic error detection"""
    run_with_popat('cargo', 'rust', cargo_args)

def run_with_popat(command, language, args):
    """Run a command with automatic Popat error detection"""
    try:
        # Run the original command
        result = subprocess.run([command] + list(args), 
                              capture_output=True, text=True, 
                              encoding='utf-8', errors='replace')
        
        if result.returncode != 0:
            # Error detected - pass to Popat for analysis
            click.echo(f"{Fore.YELLOW}⚠️ Error detected! Calling Popat...{Style.RESET_ALL}")
            
            popat_binary = find_popat_binary()
            if popat_binary:
                try:
                    subprocess.run([popat_binary, 'analyze', '--error', result.stderr, '--language', language],
                                 encoding='utf-8', errors='replace')
                except Exception:
                    pass
            
            click.echo(f"{Fore.RED}\nOriginal error:{Style.RESET_ALL}")
            click.echo(f"{Fore.RED}{result.stderr}{Style.RESET_ALL}")
            if result.stdout:
                click.echo(result.stdout)
        else:
            # Success - just show output
            if result.stdout:
                click.echo(result.stdout)
            if result.stderr:
                click.echo(result.stderr)
        
        sys.exit(result.returncode)
        
    except FileNotFoundError:
        click.echo(f"{Fore.RED}🦜 '{command}' command not found! Make sure it's installed.{Style.RESET_ALL}")
        sys.exit(127)
    except Exception as e:
        click.echo(f"{Fore.RED}🦜 Error running {command}: {e}{Style.RESET_ALL}")
        sys.exit(1)

def setup_enhanced_integration():
    """Set up enhanced shell integration for automatic error capture"""
    click.echo(f"{Fore.BLUE}🔧 Setting up enhanced shell integration...{Style.RESET_ALL}")
    
    # Auto-detect shell and set up hooks
    shell = os.environ.get('SHELL', '').split('/')[-1]
    if not shell and os.name == 'nt':
        shell = 'powershell'
    
    if shell in ['bash', 'zsh', 'fish', 'powershell']:
        try:
            popat_binary = find_popat_binary()
            subprocess.run([popat_binary, 'setup', '--shell', shell], 
                         capture_output=True, check=True, encoding='utf-8', errors='replace')
            click.echo(f"{Fore.GREEN}✅ Enhanced shell integration enabled for {shell}{Style.RESET_ALL}")
            
            # For PowerShell, also set up automatic aliases
            if shell == 'powershell' and os.name == 'nt':
                setup_powershell_aliases()
            else:
                click.echo(f"{Fore.YELLOW}   Restart your terminal or run: source ~/.{shell}rc{Style.RESET_ALL}")
        except subprocess.CalledProcessError:
            click.echo(f"{Fore.YELLOW}⚠️  Automatic shell setup failed. You may need to manually configure.{Style.RESET_ALL}")
    else:
        click.echo(f"{Fore.YELLOW}⚠️  Shell '{shell}' not fully supported for auto-setup.{Style.RESET_ALL}")
    """Set up enhanced shell integration for automatic error capture"""
    click.echo(f"{Fore.BLUE}🔧 Setting up enhanced shell integration...{Style.RESET_ALL}")
    
    # Auto-detect shell and set up hooks
    shell = os.environ.get('SHELL', '').split('/')[-1]
    if not shell and os.name == 'nt':
        shell = 'powershell'
    
    if shell in ['bash', 'zsh', 'fish', 'powershell']:
        try:
            popat_binary = find_popat_binary()
            subprocess.run([popat_binary, 'setup', '--shell', shell], 
                         capture_output=True, check=True, encoding='utf-8', errors='replace')
            click.echo(f"{Fore.GREEN}✅ Enhanced shell integration enabled for {shell}{Style.RESET_ALL}")
            
            # For PowerShell, also set up automatic aliases
            if shell == 'powershell' and os.name == 'nt':
                setup_powershell_aliases()
            else:
                click.echo(f"{Fore.YELLOW}   Restart your terminal or run: source ~/.{shell}rc{Style.RESET_ALL}")
        except subprocess.CalledProcessError:
            click.echo(f"{Fore.YELLOW}⚠️  Automatic shell setup failed. You may need to manually configure.{Style.RESET_ALL}")
    else:
        click.echo(f"{Fore.YELLOW}⚠️  Shell '{shell}' not fully supported for auto-setup.{Style.RESET_ALL}")

def setup_powershell_aliases():
    """Set up PowerShell aliases for common commands to use Popat wrappers"""
    try:
        click.echo(f"{Fore.CYAN}📝 For immediate error detection, use these popat commands:{Style.RESET_ALL}")
        click.echo(f"{Fore.GREEN}   popat python [args]  # Instead of 'python [args]'{Style.RESET_ALL}")
        click.echo(f"{Fore.GREEN}   popat node [args]    # Instead of 'node [args]'{Style.RESET_ALL}")
        click.echo(f"{Fore.GREEN}   popat cargo [args]   # Instead of 'cargo [args]'{Style.RESET_ALL}")
        click.echo()
        click.echo(f"{Fore.CYAN}💡 Example: popat python -c \"print(undefined_var)\" will show Popat's error response!{Style.RESET_ALL}")
        
    except Exception as e:
        click.echo(f"{Fore.YELLOW}⚠️  Setup info failed: {e}{Style.RESET_ALL}")

@main.command()
def status():
    """Check daemon status"""
    popat_binary = find_popat_binary()
    if not popat_binary:
        click.echo(f"{Fore.RED}🦜 Popat binary not found! Please install Popat first.{Style.RESET_ALL}")
        sys.exit(1)
    
    try:
        result = subprocess.run([popat_binary, 'status'], 
                              capture_output=True, text=True, 
                              encoding='utf-8', errors='replace')
        if result.stdout:
            click.echo(result.stdout)
        if result.stderr:
            click.echo(f"{Fore.YELLOW}{result.stderr}{Style.RESET_ALL}")
    except Exception as e:
        click.echo(f"{Fore.RED}🦜 Error checking status: {e}{Style.RESET_ALL}")

@main.command()
@click.option('--show', is_flag=True, help='Show current configuration')
@click.option('--personality', help='Set personality (encouraging, sarcastic, educational, professional, silly)')
@click.option('--emoji', type=bool, help='Enable/disable emoji support')
@click.option('--colors', help='Color mode (auto, always, never)')
@click.option('--learning', type=bool, help='Enable/disable learning')
def config(show, personality, emoji, colors, learning):
    """Configure Popat settings"""
    popat_binary = find_popat_binary()
    if not popat_binary:
        click.echo(f"{Fore.RED}🦜 Popat binary not found! Please install Popat first.{Style.RESET_ALL}")
        sys.exit(1)
    
    try:
        if show:
            result = subprocess.run([popat_binary, 'config', 'show'], 
                                  capture_output=True, text=True, 
                                  encoding='utf-8', errors='replace')
            if result.stdout:
                click.echo(result.stdout)
            return
        
        # Handle setting configurations
        if personality:
            subprocess.run([popat_binary, 'config', 'set-personality', personality], 
                         encoding='utf-8', errors='replace')
            click.echo(f"{Fore.GREEN}🦜 Personality set to: {personality}{Style.RESET_ALL}")
        
        if emoji is not None:
            subprocess.run([popat_binary, 'config', 'set', 'emoji', str(emoji).lower()], 
                         encoding='utf-8', errors='replace')
            click.echo(f"{Fore.GREEN}🦜 Emoji support: {emoji}{Style.RESET_ALL}")
        
        if colors:
            subprocess.run([popat_binary, 'config', 'set', 'colors', colors], 
                         encoding='utf-8', errors='replace')
            click.echo(f"{Fore.GREEN}🦜 Color mode: {colors}{Style.RESET_ALL}")
        
        if learning is not None:
            subprocess.run([popat_binary, 'config', 'set', 'learning', str(learning).lower()], 
                         encoding='utf-8', errors='replace')
            click.echo(f"{Fore.GREEN}🦜 Learning: {learning}{Style.RESET_ALL}")
            
        if not any([personality, emoji is not None, colors, learning is not None]):
            click.echo(f"{Fore.YELLOW}🦜 No configuration changes specified. Use --show to view current config.{Style.RESET_ALL}")
            
    except Exception as e:
        click.echo(f"{Fore.RED}🦜 Error managing config: {e}{Style.RESET_ALL}")

@main.command()
@click.option('--tail', type=int, default=20, help='Number of recent log lines to show')
@click.option('--follow', '-f', is_flag=True, help='Follow log output')
def logs(tail, follow):
    """View Popat daemon logs"""
    popat_binary = find_popat_binary()
    if not popat_binary:
        click.echo(f"{Fore.RED}🦜 Popat binary not found! Please install Popat first.{Style.RESET_ALL}")
        sys.exit(1)
    
    try:
        cmd = [popat_binary, 'logs', '--tail', str(tail)]
        if follow:
            cmd.append('--follow')
            
        subprocess.run(cmd, encoding='utf-8', errors='replace')
    except Exception as e:
        click.echo(f"{Fore.RED}🦜 Error viewing logs: {e}{Style.RESET_ALL}")

@main.command()
def doctor():
    """Run diagnostic checks"""
    click.echo(f"{Fore.CYAN}🦜 Popat Doctor - Running diagnostic checks...{Style.RESET_ALL}")
    click.echo()
    
    # Check if binary exists
    popat_binary = find_popat_binary()
    if popat_binary:
        click.echo(f"{Fore.GREEN}✅ Popat binary found: {popat_binary}{Style.RESET_ALL}")
    else:
        click.echo(f"{Fore.RED}❌ Popat binary not found{Style.RESET_ALL}")
        return
    
    # Check binary functionality
    try:
        result = subprocess.run([popat_binary, '--version'], 
                              capture_output=True, text=True, 
                              encoding='utf-8', errors='replace', timeout=5)
        if result.returncode == 0:
            click.echo(f"{Fore.GREEN}✅ Binary is functional{Style.RESET_ALL}")
        else:
            click.echo(f"{Fore.YELLOW}⚠️  Binary returned non-zero exit code{Style.RESET_ALL}")
    except Exception as e:
        click.echo(f"{Fore.RED}❌ Binary test failed: {e}{Style.RESET_ALL}")
    
    # Check dependencies
    deps = ['python', 'node', 'cargo']
    for dep in deps:
        try:
            subprocess.run([dep, '--version'], 
                         capture_output=True, timeout=2)
            click.echo(f"{Fore.GREEN}✅ {dep} is available{Style.RESET_ALL}")
        except:
            click.echo(f"{Fore.YELLOW}⚠️  {dep} not found (optional){Style.RESET_ALL}")
    
    click.echo(f"{Fore.CYAN}\n🎉 Diagnostic complete!{Style.RESET_ALL}")

@main.command()
def examples():
    """Show usage examples"""
    click.echo(f"{Fore.CYAN}🦜 Popat Usage Examples{Style.RESET_ALL}")
    click.echo()
    
    examples_list = [
        ("Start with sassy attitude", "popat start --noise"),
        ("Analyze Python error", "popat analyze 'NameError: undefined' --language python"),
        ("Run Python with error detection", "popat python -c \"print(missing_var)\""),
        ("Configure personality", "popat config --personality sarcastic"),
        ("View statistics", "popat stats --detailed"),
        ("Interactive testing", "popat interactive"),
        ("Set up shell integration", "popat setup --shell bash"),
        ("Check status", "popat status"),
        ("View logs", "popat logs --tail 50"),
    ]
    
    for desc, cmd in examples_list:
        click.echo(f"{Fore.GREEN}{desc}:{Style.RESET_ALL}")
        click.echo(f"  {Fore.CYAN}{cmd}{Style.RESET_ALL}")
        click.echo()

if __name__ == '__main__':
    # Handle signals gracefully
    def signal_handler(sig, frame):
        click.echo(f"\n{Fore.CYAN}🦜 Goodbye! Thanks for using Popat!{Style.RESET_ALL}")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    main()