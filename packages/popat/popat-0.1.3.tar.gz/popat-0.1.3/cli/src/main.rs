use clap::{Parser, Subcommand};
use std::io::{self, Write};
use std::process;

mod interceptor;
mod hooks;
mod display;
mod daemon;

use popat_core::{Popat, Context, PersonalityType};

#[derive(Parser)]
#[command(
    name = "popat",
    about = "🦜 The Funny Terminal Error Helper",
    version = "0.1.0",
    author = "Popat Team"
)]
struct Cli {
    #[command(subcommand)]
    command: Option<Commands>,
    
    /// Enable verbose output
    #[arg(short, long)]
    verbose: bool,
    
    /// Override personality for this session
    #[arg(short, long)]
    personality: Option<String>,
}

#[derive(Subcommand)]
enum Commands {
    /// Analyze an error directly
    Analyze {
        /// Error text to analyze
        #[arg(short, long)]
        error: Option<String>,
        
        /// File containing the error
        #[arg(short, long)]
        file: Option<String>,
        
        /// Programming language context
        #[arg(short, long)]
        language: Option<String>,
    },
    
    /// Start Popat in daemon mode
    Start {
        /// Start with sassy attitude
        #[arg(long)]
        noise: bool,
    },
    
    /// Stop the background daemon
    Stop,
    
    /// Set up shell integration
    Setup {
        /// Shell type (bash, zsh, fish)
        #[arg(short, long)]
        shell: Option<String>,
        
        /// Remove existing hooks
        #[arg(long)]
        remove: bool,
    },
    
    /// Configure Popat settings
    Config {
        #[command(subcommand)]
        action: ConfigAction,
    },
    
    /// Show usage statistics
    Stats,
    
    /// Interactive mode for testing
    Interactive,
}

#[derive(Subcommand)]
enum ConfigAction {
    /// Show current configuration
    Show,
    
    /// Set personality type
    SetPersonality {
        personality: String,
    },
    
    /// Enable/disable features
    Set {
        key: String,
        value: String,
    },
    
    /// Reset to defaults
    Reset,
}

fn main() {
    let cli = Cli::parse();
    
    // Initialize Popat
    let mut popat = match Popat::new() {
        Ok(p) => p,
        Err(e) => {
            eprintln!("🦜 Squawk! Failed to initialize Popat: {}", e);
            process::exit(1);
        }
    };
    
    // Override personality if specified
    if let Some(personality_str) = &cli.personality {
        if let Ok(personality) = parse_personality(personality_str) {
            popat.config.personality = personality;
            // Save the updated config
            let _ = popat.config.save();
        }
    }
    
    match cli.command {
        Some(Commands::Analyze { error, file, language }) => {
            handle_analyze(&mut popat, error, file, language);
        }
        Some(Commands::Start { noise }) => {
            handle_start(&mut popat, noise);
        }
        Some(Commands::Stop) => {
            handle_stop(&mut popat);
        }
        Some(Commands::Setup { shell, remove }) => {
            handle_setup(shell, remove);
        }
        Some(Commands::Config { action }) => {
            handle_config(&mut popat, action);
        }
        Some(Commands::Stats) => {
            handle_stats(&popat);
        }
        Some(Commands::Interactive) => {
            handle_interactive(&mut popat);
        }
        None => {
            // No command provided - check if we're being used as an error interceptor
            if let Ok(error_text) = std::env::var("POPAT_ERROR_TEXT") {
                let context = build_context_from_env();
                if let Some(response) = popat.process_error(&error_text, context) {
                    display::show_response(&response, &popat.config.ui);
                }
            } else {
                // Show help
                println!("🦜 Welcome to Popat - The Funny Terminal Error Helper!");
                println!();
                println!("Try running a command that produces an error, or use:");
                println!("  popat analyze --error 'your error message here'");
                println!("  popat setup  # Set up shell integration");
                println!("  popat interactive  # Test Popat interactively");
                println!();
                println!("For full help: popat --help");
            }
        }
    }
}

fn handle_analyze(
    popat: &mut Popat,
    error: Option<String>,
    file: Option<String>,
    language: Option<String>,
) {
    let error_text = match (error, file) {
        (Some(e), _) => e,
        (None, Some(f)) => {
            match std::fs::read_to_string(&f) {
                Ok(content) => content,
                Err(e) => {
                    eprintln!("🦜 Squawk! Can't read file '{}': {}", f, e);
                    return;
                }
            }
        }
        (None, None) => {
            eprintln!("🦜 I need either --error or --file to analyze!");
            return;
        }
    };
    
    let context = Context {
        language: language.or_else(|| detect_language_from_error(&error_text)),
        file_name: None,
        line_number: extract_line_number(&error_text),
        command: std::env::var("POPAT_COMMAND").ok(),
        environment: std::env::vars().collect(),
    };
    
    match popat.process_error(&error_text, context) {
        Some(response) => {
            display::show_response(&response, &popat.config.ui);
        }
        None => {
            println!("🦜 Hmm, I don't recognize this error pattern yet.");
            println!("   But don't worry - I'm always learning new tricks!");
            println!("   You can help by reporting this at: https://github.com/yourorg/popat/issues");
        }
    }
}

fn handle_setup(shell: Option<String>, remove: bool) {
    let shell_type = shell.unwrap_or_else(|| {
        std::env::var("SHELL")
            .unwrap_or_default()
            .split('/')
            .last()
            .unwrap_or("bash")
            .to_string()
    });
    
    if remove {
        hooks::remove_shell_hooks(&shell_type);
        println!("🦜 Shell hooks removed! Popat is now disabled.");
    } else {
        match hooks::setup_shell_hooks(&shell_type) {
            Ok(_) => {
                println!("🦜 Great! Popat is now integrated with your {} shell!", shell_type);
                println!("   Restart your terminal or run: source ~/.{}rc", shell_type);
                println!();
                println!("   Test it out with: python -c 'print('");
            }
            Err(e) => {
                eprintln!("🦜 Oops! Failed to set up shell hooks: {}", e);
                eprintln!("   You might need to manually add hooks to your shell config.");
            }
        }
    }
}

fn handle_config(popat: &mut Popat, action: ConfigAction) {
    match action {
        ConfigAction::Show => {
            display::show_config(&popat.config);
        }
        ConfigAction::SetPersonality { personality } => {
            match parse_personality(&personality) {
                Ok(p) => {
                    popat.config.personality = p;
                    if let Err(e) = popat.config.save() {
                        eprintln!("Failed to save config: {}", e);
                    } else {
                        println!("🦜 Personality set to: {:?}", popat.config.personality);
                    }
                }
                Err(_) => {
                    eprintln!("Invalid personality. Choose from: encouraging, sarcastic, educational, professional, silly");
                }
            }
        }
        ConfigAction::Set { key, value } => {
            // Handle other configuration changes
            match key.as_str() {
                "emoji" => {
                    popat.config.ui.emoji_support = value.parse().unwrap_or(true);
                    let _ = popat.config.save();
                    println!("🦜 Emoji support: {}", popat.config.ui.emoji_support);
                }
                "colors" => {
                    popat.config.ui.colored_output = value.parse().unwrap_or(true);
                    let _ = popat.config.save();
                    println!("🦜 Colored output: {}", popat.config.ui.colored_output);
                }
                _ => {
                    eprintln!("Unknown config key: {}", key);
                }
            }
        }
        ConfigAction::Reset => {
            popat.config = popat_core::config::PopatConfig::default();
            if let Err(e) = popat.config.save() {
                eprintln!("Failed to save config: {}", e);
            } else {
                println!("🦜 Configuration reset to defaults!");
            }
        }
    }
}

fn handle_stats(popat: &Popat) {
    let profile = popat.learning_engine.get_current_profile();
    
    println!("🦜 Popat Statistics");
    println!("==================");
    println!();
    println!("Skill Level: {:?}", profile.skill_level);
    println!("Personality: {:?}", popat.config.personality);
    println!("Total Errors Seen: {}", profile.total_errors_seen);
    println!("Total Errors Resolved: {}", profile.total_errors_resolved);
    
    if profile.total_errors_seen > 0 {
        let success_rate = (profile.total_errors_resolved as f32 / profile.total_errors_seen as f32) * 100.0;
        println!("Success Rate: {:.1}%", success_rate);
    }
    
    println!();
    println!("Languages Used:");
    for (lang, count) in &profile.languages_used {
        println!("  {}: {} errors", lang, count);
    }
    
    println!();
    println!("Common Mistakes:");
    if !profile.common_mistakes.is_empty() {
        for (i, mistake) in profile.common_mistakes.iter().enumerate() {
            println!("  {}. {:?}", i + 1, mistake);
        }
    } else {
        println!("  No common mistakes identified yet!");
    }
    
    println!();
    println!("Recent Activity:");
    let recent = profile.error_history.iter().rev().take(5);
    for interaction in recent {
        let status = if interaction.resolved { "✅" } else { "⏳" };
        println!("  {} {} - {} ({})", 
            status,
            interaction.timestamp.format("%m-%d %H:%M"),
            interaction.language,
            format!("{:?}", interaction.error_type)
        );
    }
}

fn handle_interactive(popat: &mut Popat) {
    println!("🦜 Welcome to Popat Interactive Mode!");
    println!("Enter error messages to see how I'd help, or 'quit' to exit.");
    println!();
    
    loop {
        print!("popat> ");
        io::stdout().flush().unwrap();
        
        let mut input = String::new();
        match io::stdin().read_line(&mut input) {
            Ok(_) => {
                let input = input.trim();
                if input.is_empty() {
                    continue;
                }
                if input == "quit" || input == "exit" {
                    println!("🦜 Thanks for flying with Popat! Goodbye!");
                    break;
                }
                
                let context = Context {
                    language: detect_language_from_error(input),
                    file_name: Some("interactive.py".to_string()),
                    line_number: None,
                    command: None,
                    environment: std::collections::HashMap::new(),
                };
                
                match popat.process_error(input, context) {
                    Some(response) => {
                        display::show_response(&response, &popat.config.ui);
                    }
                    None => {
                        println!("🦜 I don't recognize that error pattern yet, but I'm always learning!");
                    }
                }
                println!();
            }
            Err(e) => {
                eprintln!("Error reading input: {}", e);
                break;
            }
        }
    }
}

fn handle_start(popat: &mut Popat, noise: bool) {
    let sassy_startup_messages = [
        "🦜 watching you chill...jeeezzz",
        "🦜 Oh great, another human who needs my help... *sigh*",
        "🦜 Ready to fix your mess... AGAIN! 🙄",
        "🦜 Strap in buttercup, it's debugging time! 🎢",
        "🦜 I'm watching... and I'm NOT impressed! 👀",
        "🦜 *cracks knuckles* Let's see what chaos you create today!",
    ];
    
    let normal_startup_messages = [
        "🦜 Popat daemon starting... ready to catch your mistakes!",
        "🦜 Background monitoring initiated - I've got your back!",
        "🦜 Error detection activated - let's make debugging fun!",
        "🦜 Monitoring mode engaged - code away with confidence!",
        "🦜 Ready to help you become a better developer!",
    ];
    
    if noise {
        println!("{}", sassy_startup_messages[fastrand::usize(..sassy_startup_messages.len())]);
        println!("🦜 Fine... I'm watching. Try not to disappoint me! 😏");
    } else {
        println!("{}", normal_startup_messages[fastrand::usize(..normal_startup_messages.len())]);
        println!("🦜 Background monitoring is now active!");
    }
    
    // Start the actual daemon
    match daemon::start_daemon(popat) {
        Ok(_) => {},
        Err(e) => {
            eprintln!("🦜 Failed to start daemon: {}", e);
        }
    }
}

fn handle_stop(_popat: &mut Popat) {
    match daemon::stop_daemon() {
        Ok(_) => {},
        Err(e) => {
            eprintln!("🦜 Error stopping daemon: {}", e);
        }
    }
}

fn build_context_from_env() -> Context {
    Context {
        language: std::env::var("POPAT_LANGUAGE").ok(),
        file_name: std::env::var("POPAT_FILE").ok(),
        line_number: std::env::var("POPAT_LINE")
            .ok()
            .and_then(|s| s.parse().ok()),
        command: std::env::var("POPAT_COMMAND").ok(),
        environment: std::env::vars().collect(),
    }
}

fn detect_language_from_error(error_text: &str) -> Option<String> {
    if error_text.contains("SyntaxError") || error_text.contains("IndentationError") || error_text.contains("NameError") {
        Some("python".to_string())
    } else if error_text.contains("ReferenceError") || error_text.contains("TypeError") && error_text.contains("undefined") {
        Some("javascript".to_string())
    } else if error_text.contains("compilation terminated") || error_text.contains("error: expected") {
        Some("rust".to_string())
    } else if error_text.contains("cannot find symbol") {
        Some("java".to_string())
    } else {
        None
    }
}

fn extract_line_number(error_text: &str) -> Option<u32> {
    let line_regex = regex::Regex::new(r"line (\d+)").unwrap();
    line_regex.captures(error_text)
        .and_then(|caps| caps.get(1))
        .and_then(|m| m.as_str().parse().ok())
}

fn parse_personality(s: &str) -> Result<PersonalityType, &'static str> {
    match s.to_lowercase().as_str() {
        "encouraging" => Ok(PersonalityType::Encouraging),
        "sarcastic" => Ok(PersonalityType::Sarcastic),
        "educational" => Ok(PersonalityType::Educational),
        "professional" => Ok(PersonalityType::Professional),
        "silly" => Ok(PersonalityType::Silly),
        _ => Err("Invalid personality type"),
    }
}
