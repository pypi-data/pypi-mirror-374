pub mod config;
pub mod error_parser;
pub mod humor_engine;
pub mod learning;

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub enum ErrorType {
    SyntaxError,
    RuntimeError,
    CompilationError,
    LinkerError,
    IOError,
    Unknown,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum PersonalityType {
    Encouraging,
    Sarcastic,
    Educational,
    Professional,
    Silly,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum SkillLevel {
    Beginner,
    Intermediate,
    Advanced,
    Expert,
}

#[derive(Debug, Clone)]
pub struct Context {
    pub language: Option<String>,
    pub file_name: Option<String>,
    pub line_number: Option<u32>,
    pub command: Option<String>,
    pub environment: HashMap<String, String>,
}

#[derive(Debug, Clone)]
pub struct ParsedError {
    pub error_type: ErrorType,
    pub confidence: f32,
    pub line_number: Option<u32>,
    pub column: Option<u32>,
    pub message: String,
    pub context: HashMap<String, String>,
    pub language: Option<String>,
}

#[derive(Debug, Clone)]
pub struct HumorResponse {
    pub message: String,
    pub quick_fix: Option<String>,
    pub pro_tip: Option<String>,
    pub emoji: Option<String>,
    pub personality: PersonalityType,
}

#[derive(Clone)]
pub struct Popat {
    pub config: config::PopatConfig,
    pub learning_engine: learning::LearningEngine,
    error_parser: error_parser::ErrorParser,
    humor_engine: humor_engine::HumorEngine,
}

impl Popat {
    pub fn new() -> Result<Self, Box<dyn std::error::Error>> {
        let config = config::PopatConfig::load()?;
        let learning_engine = learning::LearningEngine::new("popat.db")?;
        let error_parser = error_parser::ErrorParser::new()?;
        let humor_engine = humor_engine::HumorEngine::new()?;
        Ok(Popat {
            config,
            learning_engine,
            error_parser,
            humor_engine,
        })
    }

    pub fn process_error(&mut self, error_text: &str, context: Context) -> Option<HumorResponse> {
        if let Some(parsed_error) = self.error_parser.parse(error_text, &context) {
            let profile = self.learning_engine.get_current_profile();
            let response = self.humor_engine.generate_response(&parsed_error, &profile);
            Some(response)
        } else {
            None
        }
    }
}
