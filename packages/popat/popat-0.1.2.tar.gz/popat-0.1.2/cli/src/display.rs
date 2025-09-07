use crossterm::{
    style::{Color, ResetColor, SetForegroundColor},
    ExecutableCommand,
};
use popat_core::{HumorResponse, config::UIConfig};
use std::io::{self};

pub fn show_response(response: &HumorResponse, ui_config: &UIConfig) {
    let mut stdout = io::stdout();
    
    if ui_config.colored_output {
        let _ = stdout.execute(SetForegroundColor(Color::Cyan));
    }
    
    // Show the main humorous message with enhanced styling
    if ui_config.emoji_support {
        if let Some(emoji) = &response.emoji {
            print!("{} ", emoji);
        }
    }
    
    // Add some attitude to the output
    match response.personality {
        popat_core::PersonalityType::Sarcastic => {
            if ui_config.colored_output {
                let _ = stdout.execute(SetForegroundColor(Color::Magenta));
            }
            println!("Popat says: {}", response.message);
        }
        popat_core::PersonalityType::Silly => {
            if ui_config.colored_output {
                let _ = stdout.execute(SetForegroundColor(Color::Yellow));
            }
            println!("Popat squawks: {}", response.message);
        }
        _ => {
            println!("Popat says: {}", response.message);
        }
    }
    
    if ui_config.colored_output {
        let _ = stdout.execute(ResetColor);
    }
    
    // Show quick fix if available
    if let Some(quick_fix) = &response.quick_fix {
        if ui_config.colored_output {
            let _ = stdout.execute(SetForegroundColor(Color::Green));
        }
        println!("🔧 Quick fix: {}", quick_fix);
        if ui_config.colored_output {
            let _ = stdout.execute(ResetColor);
        }
    }
    
    // Show pro tip if available
    if let Some(pro_tip) = &response.pro_tip {
        if ui_config.colored_output {
            let _ = stdout.execute(SetForegroundColor(Color::Blue));
        }
        println!("{}", pro_tip);
        if ui_config.colored_output {
            let _ = stdout.execute(ResetColor);
        }
    }
    
    println!();
}

pub fn show_config(config: &popat_core::config::PopatConfig) {
    println!("🦜 Popat Configuration");
    println!("======================");
    println!();
    println!("Personality: {:?}", config.personality);
    println!("Supported Languages: {}", config.languages.join(", "));
    println!();
    println!("Integration:");
    println!("  Shell Hooks: {}", config.integration.shell_hooks);
    println!("  Auto Suggest: {}", config.integration.auto_suggest);
    println!("  Real-time Analysis: {}", config.integration.real_time_analysis);
    println!();
    println!("UI:");
    println!("  Colored Output: {}", config.ui.colored_output);
    println!("  Emoji Support: {}", config.ui.emoji_support);
    println!("  Compact Mode: {}", config.ui.compact_mode);
    println!();
    println!("Privacy:");
    println!("  Anonymous Analytics: {}", config.privacy.anonymous_analytics);
    println!("  Error Logging: {}", config.privacy.error_logging);
    println!("  Data Retention: {} days", config.privacy.learning_data_retention_days);
}
