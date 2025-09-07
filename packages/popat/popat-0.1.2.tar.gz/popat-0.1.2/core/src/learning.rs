use crate::{ErrorType, PersonalityType, SkillLevel};
use chrono::{DateTime, Utc};
use rusqlite::{Connection, Result};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::time::Duration;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserProfile {
    pub skill_level: SkillLevel,
    pub preferred_personality: PersonalityType,
    pub error_history: Vec<ErrorInteraction>,
    pub languages_used: HashMap<String, u32>,
    pub common_mistakes: Vec<ErrorType>,
    pub total_errors_seen: u32,
    pub total_errors_resolved: u32,
}

impl Default for UserProfile {
    fn default() -> Self {
        UserProfile {
            skill_level: SkillLevel::Beginner,
            preferred_personality: PersonalityType::Encouraging,
            error_history: Vec::new(),
            languages_used: HashMap::new(),
            common_mistakes: Vec::new(),
            total_errors_seen: 0,
            total_errors_resolved: 0,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ErrorInteraction {
    pub timestamp: DateTime<Utc>,
    pub error_type: ErrorType,
    pub language: String,
    pub resolved: bool,
    pub resolution_time: Option<Duration>,
    pub message: String,
}

pub struct LearningEngine {
    conn: Connection,
}

impl LearningEngine {
    pub fn new(db_path: &str) -> Result<Self> {
        let conn = Connection::open(db_path)?;
        conn.execute(
            "CREATE TABLE IF NOT EXISTS interactions (
                timestamp TEXT NOT NULL,
                error_type TEXT NOT NULL,
                language TEXT NOT NULL,
                resolved INTEGER NOT NULL,
                resolution_time INTEGER,
                error_message TEXT
            )",
            [],
        )?;
        Ok(LearningEngine { conn })
    }

    pub fn record_interaction(&mut self, interaction: ErrorInteraction, error_message: &str) {
        self.conn
            .execute(
                "INSERT INTO interactions (timestamp, error_type, language, resolved, resolution_time, error_message)
                 VALUES (?1, ?2, ?3, ?4, ?5, ?6)",
                (
                    interaction.timestamp.to_rfc3339(),
                    serde_json::to_string(&interaction.error_type).unwrap(),
                    interaction.language,
                    interaction.resolved,
                    interaction.resolution_time.map(|d| d.as_secs() as i64),
                    error_message,
                ),
            )
            .unwrap();
    }

    pub fn get_current_profile(&self) -> UserProfile {
        let mut stmt = self
            .conn
            .prepare("SELECT timestamp, error_type, language, resolved, resolution_time, error_message FROM interactions")
            .unwrap();
        let interactions = stmt
            .query_map([], |row| {
                Ok(ErrorInteraction {
                    timestamp: row.get::<_, String>(0)?.parse().unwrap(),
                    error_type: serde_json::from_str(&row.get::<_, String>(1)?).unwrap(),
                    language: row.get(2)?,
                    resolved: row.get(3)?,
                    resolution_time: row.get::<_, Option<i64>>(4)?.map(|s| Duration::from_secs(s as u64)),
                    message: row.get(5)?,
                })
            })
            .unwrap()
            .map(|i| i.unwrap())
            .collect::<Vec<_>>();

        let mut profile = UserProfile::default();
        profile.error_history = interactions;
        profile.total_errors_seen = profile.error_history.len() as u32;
        profile.total_errors_resolved = profile
            .error_history
            .iter()
            .filter(|i| i.resolved)
            .count() as u32;

        for interaction in &profile.error_history {
            *profile
                .languages_used
                .entry(interaction.language.clone())
                .or_insert(0) += 1;
        }

        // Analyze common mistakes
        let mut error_counts = HashMap::new();
        for interaction in &profile.error_history {
            *error_counts
                .entry(interaction.error_type.clone())
                .or_insert(0) += 1;
        }
        
        // Sort errors by frequency
        let mut error_vec: Vec<_> = error_counts.into_iter().collect();
        error_vec.sort_by(|a, b| b.1.cmp(&a.1));
        
        // Take top 5 common mistakes
        profile.common_mistakes = error_vec
            .into_iter()
            .take(5)
            .map(|(error_type, _)| error_type)
            .collect();

        // Update skill level based on experience
        if profile.total_errors_seen > 10 {
            profile.skill_level = SkillLevel::Intermediate;
        }
        if profile.total_errors_seen > 50 {
            profile.skill_level = SkillLevel::Advanced;
        }
        if profile.total_errors_seen > 100 {
            profile.skill_level = SkillLevel::Expert;
        }
        
        // Update preferred personality based on error patterns
        if profile.total_errors_seen > 20 {
            // If user makes many index errors, switch to Educational
            let index_errors = profile.error_history.iter()
                .filter(|i| i.error_type == ErrorType::RuntimeError && i.message.contains("IndexError"))
                .count();
            if index_errors > 5 {
                profile.preferred_personality = PersonalityType::Educational;
            }
            
            // If user makes many type errors, switch to Professional
            let type_errors = profile.error_history.iter()
                .filter(|i| i.error_type == ErrorType::RuntimeError && i.message.contains("TypeError"))
                .count();
            if type_errors > 5 {
                profile.preferred_personality = PersonalityType::Professional;
            }
            
            // If user makes many syntax errors, switch to Encouraging
            let syntax_errors = profile.error_history.iter()
                .filter(|i| i.error_type == ErrorType::SyntaxError)
                .count();
            if syntax_errors > 5 {
                profile.preferred_personality = PersonalityType::Encouraging;
            }
            
            // If user makes many value errors, switch to Sarcastic
            let value_errors = profile.error_history.iter()
                .filter(|i| i.error_type == ErrorType::RuntimeError && i.message.contains("ValueError"))
                .count();
            if value_errors > 5 {
                profile.preferred_personality = PersonalityType::Sarcastic;
            }
        }
        
        profile
    }
}

impl Clone for LearningEngine {
    fn clone(&self) -> Self {
        // Create a new connection to the same database
        LearningEngine::new("popat.db").unwrap_or_else(|_| {
            // Fallback to in-memory database if file fails
            LearningEngine::new(":memory:").unwrap()
        })
    }
}
