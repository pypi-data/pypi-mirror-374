use popat_core::{Popat, Context};
use std::sync::atomic::{AtomicBool, Ordering};
use std::path::Path;
use std::fs;

static DAEMON_RUNNING: AtomicBool = AtomicBool::new(false);

pub fn start_daemon(popat: &mut Popat) -> Result<(), Box<dyn std::error::Error>> {
    if DAEMON_RUNNING.load(Ordering::Relaxed) {
        return Err("Daemon is already running".into());
    }

    println!("✅ Daemon mode activated!");
    
    // Set up immediate shell hooks for automatic error interception
    setup_immediate_shell_integration()?;
    
    // Start background error checking
    check_for_errors(popat);
    
    DAEMON_RUNNING.store(true, Ordering::Relaxed);
    Ok(())
}

pub fn stop_daemon() -> Result<(), Box<dyn std::error::Error>> {
    if !DAEMON_RUNNING.load(Ordering::Relaxed) {
        return Err("Daemon is not running".into());
    }
    
    DAEMON_RUNNING.store(false, Ordering::Relaxed);
    println!("🛑 Background monitoring stopped.");
    Ok(())
}

fn check_for_errors(popat: &mut Popat) {
    // Check for environment variable-based errors (for immediate processing)
    if let Ok(error_text) = std::env::var("POPAT_ERROR_TEXT") {
        if !error_text.is_empty() {
            let context = Context {
                language: std::env::var("POPAT_LANGUAGE").ok(),
                file_name: std::env::var("POPAT_FILE").ok(),
                line_number: std::env::var("POPAT_LINE")
                    .ok()
                    .and_then(|s| s.parse().ok()),
                command: std::env::var("POPAT_COMMAND").ok(),
                environment: std::env::vars().collect(),
            };
            
            if let Some(response) = popat.process_error(&error_text, context) {
                crate::display::show_response(&response, &popat.config.ui);
            }
            
            // Clear the environment variable
            std::env::remove_var("POPAT_ERROR_TEXT");
        }
    }
}

fn setup_immediate_shell_integration() -> Result<(), Box<dyn std::error::Error>> {
    let current_dir = std::env::current_dir()?;
    let popat_path = current_dir.join("target").join("debug").join("popat.exe");
    
    println!("🔧 Setting up immediate shell integration...");
    println!();
    
    if cfg!(windows) {
        setup_windows_wrapper(&popat_path)?;
    } else {
        setup_unix_wrapper(&popat_path)?;
    }
    
    Ok(())
}

fn setup_windows_wrapper(popat_path: &Path) -> Result<(), Box<dyn std::error::Error>> {
    let current_dir = std::env::current_dir()?;
    
    // Create PowerShell wrapper scripts for common programming commands
    let commands = ["python", "node", "cargo", "javac", "gcc", "rustc"];
    
    for cmd in &commands {
        let wrapper_path = current_dir.join(format!("{}_popat.ps1", cmd));
        let wrapper_content = format!(
            r#"# Popat Wrapper for {}
param([Parameter(ValueFromRemainingArguments=$true)]$Args)

$ErrorActionPreference = "Continue"
$output = & {} @Args 2>&1
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) {{
    Write-Host "⚠️ Error detected! Calling Popat..." -ForegroundColor Yellow
    $errorText = ($output | Out-String).Trim()
    $errorText = $errorText -replace '"', '\"'
    & "{}" analyze --error "$errorText" --language "{}"
    Write-Host "`nOriginal error:" -ForegroundColor Red
    Write-Host $output -ForegroundColor Red
}} else {{
    Write-Host $output
}}

exit $exitCode
"#,
            cmd, cmd, popat_path.display(), get_language_for_command(cmd)
        );
        
        fs::write(&wrapper_path, wrapper_content)?;
    }
    
    println!("🎯 Automatic error detection is now active!");
    println!("📝 To test, try running commands with errors:");
    println!("   powershell .\\python_popat.ps1 test_error.py");
    println!("   powershell .\\python_popat.ps1 -c \"print('\"");
    println!("   powershell .\\node_popat.ps1 -e \"console.log(\"");
    println!();
    println!("💡 Or create aliases for seamless integration:");
    println!("   Set-Alias python .\\python_popat.ps1");
    println!("🛑 Use 'cargo run -- stop' to disable.");
    
    Ok(())
}

fn setup_unix_wrapper(_popat_path: &Path) -> Result<(), Box<dyn std::error::Error>> {
    // Similar implementation for Unix systems
    println!("Unix wrapper setup not implemented yet.");
    Ok(())
}

fn get_language_for_command(cmd: &str) -> &str {
    match cmd {
        "python" => "python",
        "node" => "javascript",
        "cargo" | "rustc" => "rust",
        "javac" => "java",
        "gcc" => "c",
        _ => "unknown"
    }
}