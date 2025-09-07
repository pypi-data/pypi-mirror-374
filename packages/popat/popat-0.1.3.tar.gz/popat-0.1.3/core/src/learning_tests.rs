#[cfg(test)]
mod learning_tests {
    use popat_core::{
        ErrorType, SkillLevel,
        learning::{LearningEngine, ErrorInteraction, UserProfile},
    };
    use tempfile::NamedTempFile;
    use std::collections::HashMap;
    
    #[test]
    fn test_user_profile_creation() {
        let temp_db = NamedTempFile::new().unwrap();
        let mut engine = LearningEngine::new(temp_db.path().to_str().unwrap()).unwrap();
        
        let profile = engine.get_current_profile();
        assert_eq!(profile.skill_level, SkillLevel::Beginner);
        assert_eq!(profile.total_errors_seen, 0);
    }
    
    #[test]
    fn test_interaction_recording() {
        let temp_db = NamedTempFile::new().unwrap();
        let mut engine = LearningEngine::new(temp_db.path().to_str().unwrap()).unwrap();
        
        let interaction = ErrorInteraction {
            timestamp: chrono::Utc::now(),
            error_type: ErrorType::SyntaxError,
            language: "python".to_string(),
            resolved: true,
            resolution_time: Some(std::time::Duration::from_secs(30)),
        };
        
        engine.record_interaction(interaction);
        
        let profile = engine.get_current_profile();
        assert_eq!(profile.total_errors_seen, 1);
        assert_eq!(profile.total_errors_resolved, 1);
        assert_eq!(profile.error_history.len(), 1);
        assert_eq!(*profile.languages_used.get("python").unwrap(), 1);
    }
    
    #[test]
    fn test_skill_level_progression() {
        let temp_db = NamedTempFile::new().unwrap();
        let mut engine = LearningEngine::new(temp_db.path().to_str().unwrap()).unwrap();
        
        // Record many successful interactions
        for i in 0..10 {
            let interaction = ErrorInteraction {
                timestamp: chrono::Utc::now(),
                error_type: ErrorType::SyntaxError,
                language: "python".to_string(),
                resolved: true,
                resolution_time: Some(std::time::Duration::from_secs(15)), // Fast resolution
            };
            engine.record_interaction(interaction);
        }
        
        let profile = engine.get_current_profile();
        // Should have progressed beyond Beginner
        assert!(matches!(profile.skill_level, SkillLevel::Intermediate | SkillLevel::Advanced | SkillLevel::Expert));
    }
}
