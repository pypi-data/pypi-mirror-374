#[cfg(test)]
mod humor_engine_tests {
    use popat_core::{
        ErrorType, PersonalityType, SkillLevel, ParsedError, 
        humor_engine::HumorEngine,
        learning::UserProfile,
    };
    use std::collections::HashMap;
    
    #[test]
    fn test_humor_generation_personality() {
        let mut engine = HumorEngine::new().unwrap();
        
        let error = ParsedError {
            error_type: ErrorType::SyntaxError,
            confidence: 0.9,
            line_number: Some(5),
            column: None,
            message: "SyntaxError: unexpected EOF".to_string(),
            context: HashMap::new(),
            language: Some("python".to_string()),
        };
        
        let profile = UserProfile {
            skill_level: SkillLevel::Beginner,
            preferred_personality: PersonalityType::Sarcastic,
            error_history: vec![],
            languages_used: HashMap::new(),
            common_mistakes: vec![],
            total_errors_seen: 0,
            total_errors_resolved: 0,
        };
        
        let response = engine.generate_response(&error, &profile);
        
        assert_eq!(response.personality, PersonalityType::Sarcastic);
        assert!(response.message.len() > 0);
        assert!(response.quick_fix.is_some());
    }
    
    #[test]
    fn test_skill_level_appropriate_responses() {
        let mut engine = HumorEngine::new().unwrap();
        
        let error = ParsedError {
            error_type: ErrorType::RuntimeError,
            confidence: 0.9,
            line_number: None,
            column: None,
            message: "NameError: name 'test' is not defined".to_string(),
            context: {
                let mut ctx = HashMap::new();
                ctx.insert("name".to_string(), "test".to_string());
                ctx
            },
            language: Some("python".to_string()),
        };
        
        // Test beginner response
        let beginner_profile = UserProfile {
            skill_level: SkillLevel::Beginner,
            preferred_personality: PersonalityType::Encouraging,
            error_history: vec![],
            languages_used: HashMap::new(),
            common_mistakes: vec![],
            total_errors_seen: 1,
            total_errors_resolved: 0,
        };
        
        let beginner_response = engine.generate_response(&error, &beginner_profile);
        assert!(beginner_response.message.contains("test"));
        assert!(beginner_response.pro_tip.is_some());
        
        // Test expert response
        let expert_profile = UserProfile {
            skill_level: SkillLevel::Expert,
            preferred_personality: PersonalityType::Professional,
            error_history: vec![],
            languages_used: HashMap::new(),
            common_mistakes: vec![],
            total_errors_seen: 100,
            total_errors_resolved: 95,
        };
        
        let expert_response = engine.generate_response(&error, &expert_profile);
        // Expert responses should be more concise and professional
        assert!(expert_response.personality == PersonalityType::Professional);
    }
}
