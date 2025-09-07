use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;
use directories::ProjectDirs;

use crate::{PersonalityType, SkillLevel};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PopatConfig {
    pub personality: PersonalityType,
    pub skill_level: SkillLevel,
    pub languages: Vec<String>,
    pub integration: IntegrationConfig,
    pub ui: UIConfig,
    pub privacy: PrivacyConfig,
}

impl Default for PopatConfig {
    fn default() -> Self {
        PopatConfig {
            personality: PersonalityType::Encouraging,
            skill_level: SkillLevel::Beginner,
            languages: vec!["python", "javascript", "rust", "java", "c++", "go"]
                .into_iter()
                .map(String::from)
                .collect(),
            integration: IntegrationConfig::default(),
            ui: UIConfig::default(),
            privacy: PrivacyConfig::default(),
        }
    }
}

impl PopatConfig {
    pub fn load() -> Result<Self, Box<dyn std::error::Error>> {
        let path = config_path()?;
        if path.exists() {
            let content = fs::read_to_string(path)?;
            let config = toml::from_str(&content)?;
            Ok(config)
        } else {
            Ok(PopatConfig::default())
        }
    }

    pub fn save(&self) -> Result<(), Box<dyn std::error::Error>> {
        let path = config_path()?;
        if let Some(parent) = path.parent() {
            fs::create_dir_all(parent)?;
        }
        let content = toml::to_string_pretty(self)?;
        fs::write(path, content)?;
        Ok(())
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IntegrationConfig {
    pub shell_hooks: bool,
    pub auto_suggest: bool,
    pub real_time_analysis: bool,
}

impl Default for IntegrationConfig {
    fn default() -> Self {
        IntegrationConfig {
            shell_hooks: true,
            auto_suggest: true,
            real_time_analysis: false,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UIConfig {
    pub colored_output: bool,
    pub emoji_support: bool,
    pub compact_mode: bool,
}

impl Default for UIConfig {
    fn default() -> Self {
        UIConfig {
            colored_output: true,
            emoji_support: true,
            compact_mode: false,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PrivacyConfig {
    pub anonymous_analytics: bool,
    pub error_logging: bool,
    pub learning_data_retention_days: u32,
}

impl Default for PrivacyConfig {
    fn default() -> Self {
        PrivacyConfig {
            anonymous_analytics: true,
            error_logging: true,
            learning_data_retention_days: 30,
        }
    }
}

fn config_path() -> Result<PathBuf, Box<dyn std::error::Error>> {
    if let Some(proj_dirs) = ProjectDirs::from("com", "popat", "popat") {
        Ok(proj_dirs.config_dir().join("config.toml"))
    } else {
        Err("Could not determine config directory".into())
    }
}
