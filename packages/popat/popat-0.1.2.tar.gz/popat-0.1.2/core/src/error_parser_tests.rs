#[cfg(test)]
mod error_parser_tests {
    use popat_core::{Context, ErrorType};
    use popat_core::error_parser::ErrorParser;
    use std::collections::HashMap;
    
    #[test]
    fn test_python_syntax_error_parsing() {
        let parser = ErrorParser::new().unwrap();
        let error_text = "SyntaxError: unexpected EOF while parsing";
        let context = Context {
            language: Some("python".to_string()),
            file_name: Some("test.py".to_string()),
            line_number: Some(5),
            command: None,
            environment: HashMap::new(),
        };
        
        let result = parser.parse(error_text, &context);
        assert!(result.is_some());
        
        let parsed = result.unwrap();
        assert_eq!(parsed.error_type, ErrorType::SyntaxError);
        assert!(parsed.confidence > 0.8);
        assert_eq!(parsed.language, Some("python".to_string()));
    }
    
    #[test]
    fn test_python_name_error_parsing() {
        let parser = ErrorParser::new().unwrap();
        let error_text = "NameError: name 'undefined_var' is not defined";
        let context = Context {
            language: Some("python".to_string()),
            file_name: Some("test.py".to_string()),
            line_number: None,
            command: None,
            environment: HashMap::new(),
        };
        
        let result = parser.parse(error_text, &context);
        assert!(result.is_some());
        
        let parsed = result.unwrap();
        assert_eq!(parsed.error_type, ErrorType::RuntimeError);
        assert_eq!(parsed.context.get("name"), Some(&"undefined_var".to_string()));
    }
    
    #[test]
    fn test_javascript_syntax_error() {
        let parser = ErrorParser::new().unwrap();
        let error_text = "SyntaxError: Unexpected token '}'";
        let context = Context {
            language: Some("javascript".to_string()),
            file_name: Some("test.js".to_string()),
            line_number: Some(10),
            command: None,
            environment: HashMap::new(),
        };
        
        let result = parser.parse(error_text, &context);
        assert!(result.is_some());
        
        let parsed = result.unwrap();
        assert_eq!(parsed.error_type, ErrorType::SyntaxError);
        assert_eq!(parsed.context.get("token"), Some(&"}".to_string()));
    }
    
    #[test]
    fn test_language_detection() {
        let parser = ErrorParser::new().unwrap();
        let context = Context {
            language: None,
            file_name: None,
            line_number: None,
            command: None,
            environment: HashMap::new(),
        };
        
        // Should detect Python from error pattern
        let python_error = "IndentationError: expected an indented block";
        let result = parser.parse(python_error, &context);
        assert!(result.is_some());
        
        // Should detect JavaScript from error pattern  
        let js_error = "ReferenceError: $ is not defined";
        let result = parser.parse(js_error, &context);
        assert!(result.is_some());
    }
    
    #[test]
    fn test_unknown_error_handling() {
        let parser = ErrorParser::new().unwrap();
        let unknown_error = "WeirdError: something completely unknown happened";
        let context = Context {
            language: Some("unknown".to_string()),
            file_name: None,
            line_number: None,
            command: None,
            environment: HashMap::new(),
        };
        
        let result = parser.parse(unknown_error, &context);
        assert!(result.is_none());
    }
}
