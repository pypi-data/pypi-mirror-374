use crate::{Context, ErrorType, ParsedError};
use regex::Regex;
use std::collections::HashMap;

#[derive(Clone)]
pub struct ErrorParser {
    rules: Vec<ParsingRule>,
}

#[derive(Clone)]
struct ParsingRule {
    language: String,
    error_type: ErrorType,
    regex: Regex,
    capture_groups: HashMap<String, usize>,
}

impl ErrorParser {
    pub fn new() -> Result<Self, Box<dyn std::error::Error>> {
        let rules = load_rules()?;
        Ok(ErrorParser { rules })
    }

    pub fn parse(&self, error_text: &str, context: &Context) -> Option<ParsedError> {
        for rule in &self.rules {
            if let Some(lang) = &context.language {
                if lang != &rule.language {
                    continue;
                }
            }

            if let Some(captures) = rule.regex.captures(error_text) {
                let mut parsed_context = HashMap::new();
                for (name, group_index) in &rule.capture_groups {
                    if let Some(value) = captures.get(*group_index) {
                        parsed_context.insert(name.clone(), value.as_str().to_string());
                    }
                }

                return Some(ParsedError {
                    error_type: rule.error_type.clone(),
                    confidence: 0.9, // Simplified for now
                    line_number: context.line_number,
                    column: None,
                    message: error_text.to_string(),
                    context: parsed_context,
                    language: Some(rule.language.clone()),
                });
            }
        }
        None
    }
}

fn load_rules() -> Result<Vec<ParsingRule>, Box<dyn std::error::Error>> {
    // Create a vector of parsing rules
    let mut rules = Vec::new();
    // ================================
    // COMPREHENSIVE PYTHON ERROR PATTERNS
    // ================================
    
    // 1. SYNTAX ERRORS - The most common Python errors
        
    
    // General SyntaxError
    rules.push(ParsingRule {
        language: "python".to_string(),
        error_type: ErrorType::SyntaxError,
        regex: Regex::new(r"SyntaxError: (?P<message>.+)")?,
        capture_groups: [("message".to_string(), 1)].iter().cloned().collect(),
    });
    
    // IndentationError
    rules.push(ParsingRule {
        language: "python".to_string(),
        error_type: ErrorType::SyntaxError,
        regex: Regex::new(r"IndentationError: (?P<message>.+)")?,
        capture_groups: [("message".to_string(), 1)].iter().cloned().collect(),
    });
    
    // TabError
    rules.push(ParsingRule {
        language: "python".to_string(),
        error_type: ErrorType::SyntaxError,
        regex: Regex::new(r"TabError: (?P<message>.+)")?,
        capture_groups: [("message".to_string(), 1)].iter().cloned().collect(),
    });
    
    // 2. RUNTIME ERRORS - Variable and name issues
    
    // NameError - undefined variable
    rules.push(ParsingRule {
        language: "python".to_string(),
        error_type: ErrorType::RuntimeError,
        regex: Regex::new(r"NameError: name '(?P<name>.+)' is not defined")?,
        capture_groups: [("name".to_string(), 1)].iter().cloned().collect(),
    });
    
    // AttributeError - missing attribute/method
    rules.push(ParsingRule {
        language: "python".to_string(),
        error_type: ErrorType::RuntimeError,
        regex: Regex::new(r"AttributeError: '(?P<type>.+)' object has no attribute '(?P<attr>.+)'")?,
        capture_groups: [("type".to_string(), 1), ("attr".to_string(), 2)].iter().cloned().collect(),
    });
    
    // AttributeError - None type
    rules.push(ParsingRule {
        language: "python".to_string(),
        error_type: ErrorType::RuntimeError,
        regex: Regex::new(r"AttributeError: 'NoneType' object has no attribute '(?P<attr>.+)'")?,
        capture_groups: [("attr".to_string(), 1)].iter().cloned().collect(),
    });
    
    // TypeError - wrong type
    rules.push(ParsingRule {
        language: "python".to_string(),
        error_type: ErrorType::RuntimeError,
        regex: Regex::new(r"TypeError: (?P<message>.+)")?,
        capture_groups: [("message".to_string(), 1)].iter().cloned().collect(),
    });
    
    // ValueError - wrong value
    rules.push(ParsingRule {
        language: "python".to_string(),
        error_type: ErrorType::RuntimeError,
        regex: Regex::new(r"ValueError: (?P<message>.+)")?,
        capture_groups: [("message".to_string(), 1)].iter().cloned().collect(),
    });
    
    // KeyError - missing dictionary key
    rules.push(ParsingRule {
        language: "python".to_string(),
        error_type: ErrorType::RuntimeError,
        regex: Regex::new(r"KeyError: '(?P<key>.+)'")?,
        capture_groups: [("key".to_string(), 1)].iter().cloned().collect(),
    });
    
    // IndexError - list index out of range
    rules.push(ParsingRule {
        language: "python".to_string(),
        error_type: ErrorType::RuntimeError,
        regex: Regex::new(r"IndexError: list index out of range$?(?P<index>-?\d+)?$?")?,
        capture_groups: [("index".to_string(), 1)].iter().cloned().collect(),
    });

    // IndexError - string index out of range
    rules.push(ParsingRule {
        language: "python".to_string(),
        error_type: ErrorType::RuntimeError,
        regex: Regex::new(r"IndexError: string index out of range")?,
        capture_groups: HashMap::new(),
    });

    // ValueError - invalid literal for int()
    rules.push(ParsingRule {
        language: "python".to_string(),
        error_type: ErrorType::RuntimeError,
        regex: Regex::new(r"ValueError: invalid literal for int\(\) with base (?P<base>\d+): '(?P<value>.+)'$")?,
        capture_groups: [("base".to_string(), 1), ("value".to_string(), 2)].iter().cloned().collect(),
    });

    // TypeError - unsupported operand type(s) for +
    rules.push(ParsingRule {
        language: "python".to_string(),
        error_type: ErrorType::RuntimeError,
        regex: Regex::new(r"TypeError: unsupported operand type\(s\) for \+: '(?P<type1>.+)' and '(?P<type2>.+)'$")?,
        capture_groups: [("type1".to_string(), 1), ("type2".to_string(), 2)].iter().cloned().collect(),
    });

    // 5. ZERO DIVISION AND MATH ERRORS

    // ZeroDivisionError
    rules.push(ParsingRule {
        language: "python".to_string(),
        error_type: ErrorType::RuntimeError,
        regex: Regex::new(r"ZeroDivisionError: (?P<message>.+)")?, // Fixed incomplete escape sequence
        capture_groups: [("message".to_string(), 1)].iter().cloned().collect(),
    });
    
    // OverflowError
    rules.push(ParsingRule {
        language: "python".to_string(),
        error_type: ErrorType::RuntimeError,
        regex: Regex::new(r"OverflowError: (?P<message>.+)")?,
        capture_groups: [("message".to_string(), 1)].iter().cloned().collect(),
    });
    
    // 6. RECURSION AND MEMORY ERRORS
    
    // RecursionError
    rules.push(ParsingRule {
        language: "python".to_string(),
        error_type: ErrorType::RuntimeError,
        regex: Regex::new(r"RecursionError: (?P<message>.+)")?,
        capture_groups: [("message".to_string(), 1)].iter().cloned().collect(),
    });
    
    // MemoryError
    rules.push(ParsingRule {
        language: "python".to_string(),
        error_type: ErrorType::RuntimeError,
        regex: Regex::new(r"MemoryError")?,
        capture_groups: HashMap::new(),
    });
    
    // 7. UNICODE AND ENCODING ERRORS
    
    // UnicodeDecodeError
    rules.push(ParsingRule {
        language: "python".to_string(),
        error_type: ErrorType::RuntimeError,
        regex: Regex::new(r"UnicodeDecodeError: '(?P<codec>.+)' codec can't decode byte (?P<byte>.+)")?,
        capture_groups: [("codec".to_string(), 1), ("byte".to_string(), 2)].iter().cloned().collect(),
    });
    
    // UnicodeEncodeError
    rules.push(ParsingRule {
        language: "python".to_string(),
        error_type: ErrorType::RuntimeError,
        regex: Regex::new(r"UnicodeEncodeError: '(?P<codec>.+)' codec can't encode character")?,
        capture_groups: [("codec".to_string(), 1)].iter().cloned().collect(),
    });
    
    // 8. ASSERTION AND STOPITERATION ERRORS
    
    // AssertionError
    rules.push(ParsingRule {
        language: "python".to_string(),
        error_type: ErrorType::RuntimeError,
        regex: Regex::new(r"AssertionError: (?P<message>.+)")?,
        capture_groups: [("message".to_string(), 1)].iter().cloned().collect(),
    });
    
    // AssertionError without message
    rules.push(ParsingRule {
        language: "python".to_string(),
        error_type: ErrorType::RuntimeError,
        regex: Regex::new(r"AssertionError$")?,
        capture_groups: HashMap::new(),
    });
    
    // StopIteration
    rules.push(ParsingRule {
        language: "python".to_string(),
        error_type: ErrorType::RuntimeError,
        regex: Regex::new(r"StopIteration")?,
        capture_groups: HashMap::new(),
    });
    
    // 9. KEYBOARD INTERRUPT AND SYSTEM ERRORS
    
    // KeyboardInterrupt
    rules.push(ParsingRule {
        language: "python".to_string(),
        error_type: ErrorType::RuntimeError,
        regex: Regex::new(r"KeyboardInterrupt")?,
        capture_groups: HashMap::new(),
    });
    
    // SystemExit
    rules.push(ParsingRule {
        language: "python".to_string(),
        error_type: ErrorType::RuntimeError,
        regex: Regex::new(r"SystemExit: (?P<code>.+)")?,
        capture_groups: [("code".to_string(), 1)].iter().cloned().collect(),
    });
    
    // 10. SPECIFIC SYNTAX ERROR PATTERNS
    
    // EOFError - unexpected end of file
    rules.push(ParsingRule {
        language: "python".to_string(),
        error_type: ErrorType::SyntaxError,
        regex: Regex::new(r"EOFError: (?P<message>.+)")?,
        capture_groups: [("message".to_string(), 1)].iter().cloned().collect(),
    });
    
    // UnboundLocalError
    rules.push(ParsingRule {
        language: "python".to_string(),
        error_type: ErrorType::RuntimeError,
        regex: Regex::new(r"UnboundLocalError: local variable '(?P<var>.+)' referenced before assignment")?,
        capture_groups: [("var".to_string(), 1)].iter().cloned().collect(),
    });
    
    // NotImplementedError
    rules.push(ParsingRule {
        language: "python".to_string(),
        error_type: ErrorType::RuntimeError,
        regex: Regex::new(r"NotImplementedError: (?P<message>.+)")?,
        capture_groups: [("message".to_string(), 1)].iter().cloned().collect(),
    });
    
    // NotImplementedError without message
    rules.push(ParsingRule {
        language: "python".to_string(),
        error_type: ErrorType::RuntimeError,
        regex: Regex::new(r"NotImplementedError$")?,
        capture_groups: HashMap::new(),
    });
    
    // ================================
    // JAVASCRIPT/NODE.JS ERROR PATTERNS
    // ================================

    // JavaScript ReferenceError
    rules.push(ParsingRule {
        language: "javascript".to_string(),
        error_type: ErrorType::RuntimeError,
        regex: Regex::new(r"ReferenceError: (?P<name>.+) is not defined")?,
        capture_groups: [("name".to_string(), 1)].iter().cloned().collect(),
    });
    
    // JavaScript SyntaxError
    rules.push(ParsingRule {
        language: "javascript".to_string(),
        error_type: ErrorType::SyntaxError,
        regex: Regex::new(r"SyntaxError: Unexpected token '(?P<token>.+)'")?,
        capture_groups: [("token".to_string(), 1)].iter().cloned().collect(),
    });
    
    // JavaScript SyntaxError - missing closing parenthesis
    rules.push(ParsingRule {
        language: "javascript".to_string(),
        error_type: ErrorType::SyntaxError,
        regex: Regex::new(r"SyntaxError: (?P<message>missing .+ after .+)")?,
        capture_groups: [("message".to_string(), 1)].iter().cloned().collect(),
    });

    Ok(rules)
}
