use std::fs::{self, OpenOptions};
use std::io::Write;
use std::path::PathBuf;

pub fn setup_shell_hooks(shell: &str) -> Result<(), Box<dyn std::error::Error>> {
    match shell {
        "bash" => setup_bash_hooks(),
        "zsh" => setup_zsh_hooks(),
        "fish" => setup_fish_hooks(),
        _ => Err(format!("Unsupported shell: {}", shell).into()),
    }
}

pub fn remove_shell_hooks(shell: &str) {
    match shell {
        "bash" => remove_bash_hooks(),
        "zsh" => remove_zsh_hooks(), 
        "fish" => remove_fish_hooks(),
        _ => eprintln!("Unsupported shell: {}", shell),
    }
}

fn setup_bash_hooks() -> Result<(), Box<dyn std::error::Error>> {
    let home = std::env::var("HOME")?;
    let bashrc_path = PathBuf::from(&home).join(".bashrc");
    
    let hook_content = r#"
# Popat Error Helper Integration
if command -v popat >/dev/null 2>&1; then
    popat_command_not_found_handle() {
        local command="$1"
        shift
        
        # Try to execute the command and capture output
        if ! command -v "$command" >/dev/null 2>&1; then
            echo "🦜 Squawk! Command '$command' not found. Did you mean one of these?"
            # Suggest similar commands
            if command -v "$command"* >/dev/null 2>&1; then
                compgen -c "$command" | head -3
            fi
            return 127
        fi
        
        return 1
    }
    
    # Wrap common error-prone commands
    python() {
        local output
        output=$(command python "$@" 2>&1)
        local exit_code=$?
        
        if [ $exit_code -ne 0 ]; then
            # Pass error to Popat
            echo "$output" | POPAT_ERROR_TEXT="$output" POPAT_COMMAND="python $*" popat
        else
            echo "$output"
        fi
        
        return $exit_code
    }
    
    node() {
        local output
        output=$(command node "$@" 2>&1)
        local exit_code=$?
        
        if [ $exit_code -ne 0 ]; then
            echo "$output" | POPAT_ERROR_TEXT="$output" POPAT_COMMAND="node $*" popat
        else
            echo "$output"
        fi
        
        return $exit_code
    }
fi
"#;
    
    // Check if hooks already exist
    let bashrc_content = fs::read_to_string(&bashrc_path).unwrap_or_default();
    if bashrc_content.contains("# Popat Error Helper Integration") {
        println!("🦜 Bash hooks already installed!");
        return Ok(());
    }
    
    // Append hooks to .bashrc
    let mut file = OpenOptions::new()
        .create(true)
        .append(true)
        .open(&bashrc_path)?;
    
    writeln!(file, "{}", hook_content)?;
    
    Ok(())
}

fn setup_zsh_hooks() -> Result<(), Box<dyn std::error::Error>> {
    let home = std::env::var("HOME")?;
    let zshrc_path = PathBuf::from(&home).join(".zshrc");
    
    let hook_content = r#"
# Popat Error Helper Integration
if command -v popat >/dev/null 2>&1; then
    # Function to wrap commands and pass errors to Popat
    popat_wrap_command() {
        local cmd="$1"
        shift
        local output
        output=$(command "$cmd" "$@" 2>&1)
        local exit_code=$?
        
        if [ $exit_code -ne 0 ]; then
            POPAT_ERROR_TEXT="$output" POPAT_COMMAND="$cmd $*" popat
        else
            echo "$output"
        fi
        
        return $exit_code
    }
    
    # Wrap common commands
    alias python='popat_wrap_command python'
    alias node='popat_wrap_command node'
    alias javac='popat_wrap_command javac'
    alias cargo='popat_wrap_command cargo'
fi
"#;
    
    let zshrc_content = fs::read_to_string(&zshrc_path).unwrap_or_default();
    if zshrc_content.contains("# Popat Error Helper Integration") {
        println!("🦜 Zsh hooks already installed!");
        return Ok(());
    }
    
    let mut file = OpenOptions::new()
        .create(true)
        .append(true)
        .open(&zshrc_path)?;
    
    writeln!(file, "{}", hook_content)?;
    
    Ok(())
}

fn setup_fish_hooks() -> Result<(), Box<dyn std::error::Error>> {
    let home = std::env::var("HOME")?;
    let fish_config_path = PathBuf::from(&home).join(".config/fish/config.fish");
    
    // Create directory if it doesn't exist
    if let Some(parent) = fish_config_path.parent() {
        fs::create_dir_all(parent)?;
    }
    
    let hook_content = r#"
# Popat Error Helper Integration
if command -v popat > /dev/null 2>&1
    function python --wraps python
        set -l output (command python $argv 2>&1)
        set -l exit_code $status
        
        if test $exit_code -ne 0
            env POPAT_ERROR_TEXT="$output" POPAT_COMMAND="python $argv" popat
        else
            echo $output
        end
        
        return $exit_code
    end
    
    function node --wraps node  
        set -l output (command node $argv 2>&1)
        set -l exit_code $status
        
        if test $exit_code -ne 0
            env POPAT_ERROR_TEXT="$output" POPAT_COMMAND="node $argv" popat
        else
            echo $output
        end
        
        return $exit_code
    end
end
"#;
    
    let fish_content = fs::read_to_string(&fish_config_path).unwrap_or_default();
    if fish_content.contains("# Popat Error Helper Integration") {
        println!("🦜 Fish hooks already installed!");
        return Ok(());
    }
    
    let mut file = OpenOptions::new()
        .create(true)
        .append(true)
        .open(&fish_config_path)?;
    
    writeln!(file, "{}", hook_content)?;
    
    Ok(())
}

fn remove_bash_hooks() {
    // Implementation to remove hooks from shell configs
    let home = std::env::var("HOME").unwrap_or_default();
    let bashrc_path = PathBuf::from(&home).join(".bashrc");
    
    if let Ok(content) = fs::read_to_string(&bashrc_path) {
        let lines: Vec<&str> = content.lines().collect();
        let mut new_content = String::new();
        let mut skip_section = false;
        
        for line in lines {
            if line.contains("# Popat Error Helper Integration") {
                skip_section = true;
                continue;
            }
            if skip_section && line.trim().is_empty() && !line.contains("popat") {
                skip_section = false;
            }
            if !skip_section {
                new_content.push_str(line);
                new_content.push('\n');
            }
        }
        
        let _ = fs::write(&bashrc_path, new_content);
    }
}

fn remove_zsh_hooks() {
    // Similar implementation for zsh
    let home = std::env::var("HOME").unwrap_or_default();
    let zshrc_path = PathBuf::from(&home).join(".zshrc");
    
    if let Ok(content) = fs::read_to_string(&zshrc_path) {
        let new_content = remove_popat_section(&content);
        let _ = fs::write(&zshrc_path, new_content);
    }
}

fn remove_fish_hooks() {
    // Similar implementation for fish
    let home = std::env::var("HOME").unwrap_or_default();
    let fish_config_path = PathBuf::from(&home).join(".config/fish/config.fish");
    
    if let Ok(content) = fs::read_to_string(&fish_config_path) {
        let new_content = remove_popat_section(&content);
        let _ = fs::write(&fish_config_path, new_content);
    }
}

fn remove_popat_section(content: &str) -> String {
    let lines: Vec<&str> = content.lines().collect();
    let mut new_content = String::new();
    let mut skip_section = false;
    
    for line in lines {
        if line.contains("# Popat Error Helper Integration") {
            skip_section = true;
            continue;
        }
        if skip_section && line.trim().is_empty() && !line.contains("popat") {
            skip_section = false;
        }
        if !skip_section {
            new_content.push_str(line);
            new_content.push('\n');
        }
    }
    
    new_content
}
