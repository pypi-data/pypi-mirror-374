use crate::{ErrorType, HumorResponse, ParsedError, PersonalityType};
use crate::learning::UserProfile;

#[derive(Clone)]
pub struct HumorEngine;

impl HumorEngine {
    pub fn new() -> Result<Self, Box<dyn std::error::Error>> {
        Ok(HumorEngine)
    }

    pub fn generate_response(&self, error: &ParsedError, profile: &UserProfile) -> HumorResponse {
        let personality = profile.preferred_personality.clone();
        
        // If user has a common mistake pattern, use that personality
        let mut adjusted_personality = personality.clone();
        if let Some(common_mistake) = profile.common_mistakes.first() {
            if error.error_type == *common_mistake {
                // Adjust personality based on common mistakes
                adjusted_personality = match personality {
                    PersonalityType::Encouraging => PersonalityType::Encouraging,
                    PersonalityType::Sarcastic => PersonalityType::Sarcastic,
                    PersonalityType::Educational => PersonalityType::Educational,
                    PersonalityType::Professional => PersonalityType::Professional,
                    PersonalityType::Silly => PersonalityType::Silly,
                };
            }
        }
        
        // Enhanced error detection based on error message content
        let (message, quick_fix, pro_tip) = if error.language == Some("python".to_string()) {
            self.python_specific_response(error, &adjusted_personality)
        } else {
            match error.error_type {
                ErrorType::SyntaxError => self.syntax_error_response(error, &adjusted_personality),
                ErrorType::RuntimeError => self.runtime_error_response(error, &adjusted_personality),
                _ => (
                    "I'm not sure what to make of this, but I'm sure you'll figure it out!".to_string(),
                    None,
                    None,
                ),
            }
        };
        
        HumorResponse {
            message,
            quick_fix,
            pro_tip,
            emoji: Some("🦜".to_string()),
            personality: adjusted_personality,
        }
    }
    
    fn python_specific_response(
        &self,
        error: &ParsedError,
        personality: &PersonalityType,
    ) -> (String, Option<String>, Option<String>) {
        let error_msg = &error.message;
        
        // Detect specific Python error types by message content
        if error_msg.contains("NameError") {
            self.python_name_error_response(error, personality)
        } else if error_msg.contains("TypeError") {
            self.python_type_error_response(error, personality)
        } else if error_msg.contains("ValueError") {
            self.python_value_error_response(error, personality)
        } else if error_msg.contains("KeyError") {
            self.python_key_error_response(error, personality)
        } else if error_msg.contains("IndexError") {
            self.python_index_error_response(error, personality)
        } else if error_msg.contains("AttributeError") {
            self.python_attribute_error_response(error, personality)
        } else if error_msg.contains("ZeroDivisionError") {
            self.python_zero_division_response(error, personality)
        } else if error_msg.contains("IndentationError") || error_msg.contains("TabError") {
            self.python_indentation_error_response(error, personality)
        } else if error_msg.contains("ImportError") || error_msg.contains("ModuleNotFoundError") {
            self.python_import_error_response(error, personality)
        } else if error_msg.contains("FileNotFoundError") {
            self.python_file_not_found_response(error, personality)
        } else if error_msg.contains("RecursionError") {
            self.python_recursion_error_response(error, personality)
        } else if error_msg.contains("AssertionError") {
            self.python_assertion_error_response(error, personality)
        } else if error_msg.contains("UnboundLocalError") {
            self.python_unbound_local_response(error, personality)
        } else if error_msg.contains("PermissionError") {
            self.python_permission_error_response(error, personality)
        } else if error_msg.contains("OverflowError") {
            self.python_overflow_error_response(error, personality)
        } else if error_msg.contains("MemoryError") {
            self.python_memory_error_response(error, personality)
        } else if error_msg.contains("KeyboardInterrupt") {
            self.python_keyboard_interrupt_response(error, personality)
        } else if error.error_type == ErrorType::SyntaxError {
            self.syntax_error_response(error, personality)
        } else {
            self.runtime_error_response(error, personality)
        }
    }
    
    // ================================
    // PYTHON ERROR HANDLERS
    // ================================
    
    fn python_name_error_response(
        &self,
        error: &ParsedError,
        personality: &PersonalityType,
    ) -> (String, Option<String>, Option<String>) {
        let name = error.context.get("name").cloned().unwrap_or_else(|| "variable".to_string());
        
        // Common fix suggestions for all personalities
        let common_fixes = [
            format!("Define '{}' before using it: {} = some_value", name, name),
            format!("Check if you meant a different variable name"),
            format!("Import '{}' if it's from another module", name),
        ];
        
        // Common pro tips for all personalities
        let common_tips = [
            "💡 Pro tip: Use your IDE's autocomplete to avoid typos".to_string(),
            " YYS Smart: Most editors highlight undefined variables".to_string(),
            "🚀 Boss tip: Initialize variables when you declare them".to_string(),
        ];
        
        match personality {
            PersonalityType::Encouraging => {
                let messages = vec![
                    format!("You're so close! Just need to define '{}' first! ✨", name),
                    format!("Almost there! '{}' just needs to be declared! 🎆", name),
                    format!("One small step: define '{}' and you're golden! 🌟", name),
                ];
                
                (
                    messages[fastrand::usize(..messages.len())].clone(),
                    Some(common_fixes[fastrand::usize(..common_fixes.len())].clone()),
                    Some(common_tips[fastrand::usize(..common_tips.len())].clone()),
                )
            }
            PersonalityType::Sarcastic => {
                let messages = vec![
                    format!("Oh please... '{}' doesn't exist and you know it! 🙄", name),
                    format!("Really? You're looking for '{}' that was never born? 😏", name),
                    format!("Breaking news: '{}' was never declared! Shocking! 📢", name),
                ];
                
                (
                    messages[fastrand::usize(..messages.len())].clone(),
                    Some(common_fixes[fastrand::usize(..common_fixes.len())].clone()),
                    Some(common_tips[fastrand::usize(..common_tips.len())].clone()),
                )
            }
            PersonalityType::Educational => {
                let messages = vec![
                    format!("NameError occurs when Python can't find '{}' in the current scope", name),
                    format!("Variable '{}' needs to be defined before it can be used", name),
                    format!("Scope issue: '{}' is not accessible in this context", name),
                ];
                
                (
                    messages[fastrand::usize(..messages.len())].clone(),
                    Some(common_fixes[fastrand::usize(..common_fixes.len())].clone()),
                    Some(common_tips[fastrand::usize(..common_tips.len())].clone()),
                )
            }
            PersonalityType::Professional => {
                let messages = vec![
                    format!("NameError: Variable '{}' is not defined in the current scope", name),
                ];
                
                (
                    messages[fastrand::usize(..messages.len())].clone(),
                    Some(common_fixes[fastrand::usize(..common_fixes.len())].clone()),
                    Some(common_tips[fastrand::usize(..common_tips.len())].clone()),
                )
            }
            PersonalityType::Silly => {
                let messages = vec![
                    format!("'{}' went on a vacation! 🏖️", name),
                    format!("'{}' is playing hide and seek! 🦜🕵️‍♀️", name),
                    format!("'{}' is in the Bermuda Triangle! 🌊", name),
                ];
                
                (
                    messages[fastrand::usize(..messages.len())].clone(),
                    Some(common_fixes[fastrand::usize(..common_fixes.len())].clone()),
                    Some(common_tips[fastrand::usize(..common_tips.len())].clone()),
                )
            }
        }
    }
    
    fn python_type_error_response(
        &self,
        _error: &ParsedError,
        personality: &PersonalityType,
    ) -> (String, Option<String>, Option<String>) {
        let (messages, fixes, tips) = match personality {
            PersonalityType::Encouraging => (
                vec![
                    "You're mixing types, but that's totally fixable! 🎆".to_string(),
                    "Close! Just need to match the data types! ✨".to_string(),
                    "Type mismatch detected - easy fix coming up! 🔧".to_string(),
                ],
                vec![
                    "Convert types: str() for strings, int() for numbers".to_string(),
                    "Check if you're adding different data types".to_string(),
                    "Use type conversion functions like float(), bool()".to_string(),
                ],
                vec![
                    "💡 Tip: Python is strict about mixing types!".to_string(),
                    " YYS Smart: Use type hints for clarity!".to_string(),
                    "✨ Pro: f-strings handle type conversion automatically!".to_string(),
                ]
            ),
            PersonalityType::Sarcastic => (
                vec![
                    "Oh, trying to add a string to a number? How... creative! 😏".to_string(),
                    "Sure, let's just mix oil and water while we're at it! 🙄".to_string(),
                    "Python isn't that flexible, friend! 😃".to_string(),
                ],
                vec![
                    "Convert your types like a civilized programmer".to_string(),
                    "Try str() or int() - revolutionary concepts!".to_string(),
                    "Maybe check what type your variables actually are?".to_string(),
                ],
                vec![
                    "😏 Reality check: Types matter in Python!".to_string(),
                    "🙄 Sassy tip: 'hello' + 5 doesn't work in any universe!".to_string(),
                    "🤷‍♂️ Math class: Numbers and strings are different!".to_string(),
                ]
            ),
            _ => (
                vec!["TypeError: Incompatible data types used together.".to_string()],
                vec!["Use appropriate type conversion functions".to_string()],
                vec!["Tip: Check variable types before operations".to_string()],
            ),
        };
        
        let message = messages[fastrand::usize(..messages.len())].clone();
        let fix = Some(fixes[fastrand::usize(..fixes.len())].clone());
        let tip = Some(tips[fastrand::usize(..tips.len())].to_string());
        
        (message, fix, tip)
    }

    fn python_key_error_response(
        &self,
        error: &ParsedError,
        personality: &PersonalityType,
    ) -> (String, Option<String>, Option<String>) {
        let key = error.context.get("key").cloned().unwrap_or_else(|| "missing_key".to_string());
        
        let (messages, fixes, tips) = match personality {
            PersonalityType::Encouraging => (
                vec![
                    format!("Key '{}' is playing hide and seek! Let's find it! 🔍", key),
                    format!("Dictionary doesn't have '{}', but we can fix that! ✨", key),
                ],
                vec![
                    format!("Check if '{}' exists: '{}' in dict", key, key),
                    format!("Use dict.get('{}', default_value)", key),
                    "Print dict.keys() to see available keys".to_string(),
                ],
                vec![
                    "💡 Tip: Use .get() method for safe key access!".to_string(),
                    "🔑 Smart: Check keys before accessing!".to_string(),
                ]
            ),
            PersonalityType::Sarcastic => (
                vec![
                    format!("Wow, '{}' doesn't exist in your dictionary. Shocking! 😮", key),
                    format!("Did you just assume '{}' would be there? Bold! 😏", key),
                ],
                vec![
                    "Maybe CHECK if the key exists first?".to_string(),
                    format!("Try dict.get('{}') like a responsible coder", key),
                ],
                vec![
                    "🙄 Pro tip: Dictionaries aren't magical wish-granters!".to_string(),
                    "😏 Reality: Keys must exist to be accessed!".to_string(),
                ]
            ),
            _ => (
                vec![format!("KeyError: Key '{}' not found in dictionary.", key)],
                vec!["Use safe key access methods".to_string()],
                vec!["Tip: Always validate key existence".to_string()],
            ),
        };
        
        let message = messages[fastrand::usize(..messages.len())].clone();
        let fix = Some(fixes[fastrand::usize(..fixes.len())].clone());
        let tip = Some(tips[fastrand::usize(..tips.len())].to_string());
        
        (message, fix, tip)
    }

    fn python_index_error_response(
        &self,
        error: &ParsedError,
        personality: &PersonalityType,
    ) -> (String, Option<String>, Option<String>) {
        let index = error.context.get("index").cloned().unwrap_or_else(|| "specified".to_string());
        
        // Common fix suggestions for all personalities
        let common_fixes = vec![
            format!("Check list length with len() before accessing index {}", index),
            format!("Use a valid index between 0 and len(list)-1"),
            format!("Consider using list slicing to avoid index errors"),
        ];
        
        // Common pro tips for all personalities
        let common_tips = vec![
            "💡 Pro tip: Use enumerate() when iterating for safe index access".to_string(),
            "🚀 Boss tip: Validate indexes before use in complex logic!".to_string(),
            "🎯 Smart tip: Consider using get() method with default value!".to_string(),
        ];
        
        match personality {
            PersonalityType::Encouraging => {
                let messages = vec![
                    format!("You're accessing index {} which is out of bounds! Let's fix this! 🌟", index),
                    format!("Almost there! Index {} is beyond the list length! 🎯", index),
                    format!("One small fix: index {} needs to be within range! 🛠️", index),
                ];
                
                (
                    messages[fastrand::usize(..messages.len())].clone(),
                    Some(common_fixes[fastrand::usize(..common_fixes.len())].clone()),
                    Some(common_tips[fastrand::usize(..common_tips.len())].clone()),
                )
            }
            PersonalityType::Sarcastic => {
                let messages = vec![
                    format!("Wow, index {} really wanted to be special! 🙄", index),
                    format!("Index {} broke the laws of physics! Shocking! 📢", index),
                    format!("Out of bounds? Never heard of her! 😏"),
                ];
                
                (
                    messages[fastrand::usize(..messages.len())].clone(),
                    Some(common_fixes[fastrand::usize(..common_fixes.len())].clone()),
                    Some(common_tips[fastrand::usize(..common_tips.len())].clone()),
                )
            }
            PersonalityType::Educational => {
                let messages = vec![
                    format!("IndexError occurs when accessing index {} in a sequence", index),
                    "Python sequences are zero-indexed and have finite length".to_string(),
                    "Index must be an integer within [0, len(sequence)-1]".to_string(),
                ];
                
                (
                    messages[fastrand::usize(..messages.len())].clone(),
                    Some(common_fixes[fastrand::usize(..common_fixes.len())].clone()),
                    Some(common_tips[fastrand::usize(..common_tips.len())].clone()),
                )
            }
            PersonalityType::Professional => {
                let messages = vec![
                    format!("IndexError: Index is out of range for the sequence"),
                ];
                
                (
                    messages[fastrand::usize(..messages.len())].clone(),
                    Some(common_fixes[fastrand::usize(..common_fixes.len())].clone()),
                    Some(common_tips[fastrand::usize(..common_tips.len())].clone()),
                )
            }
            PersonalityType::Silly => {
                let messages = vec![
                    format!("Index {} went on a vacation! 🏖️", index),
                    format!("Index {} is playing hide and seek! 🦜🕵️‍♀️", index),
                    format!("Index {} is in the Bermuda Triangle! 🌊", index),
                ];
                
                (
                    messages[fastrand::usize(..messages.len())].clone(),
                    Some(common_fixes[fastrand::usize(..common_fixes.len())].clone()),
                    Some(common_tips[fastrand::usize(..common_tips.len())].clone()),
                )
            }
        }
    }
    
    fn python_value_error_response(
        &self,
        error: &ParsedError,
        personality: &PersonalityType,
    ) -> (String, Option<String>, Option<String>) {
        let message = &error.message;
        
        // Common fix suggestions for all personalities
        let common_fixes = vec![
            "Check the value format for this operation".to_string(),
            "Use a valid value for this function".to_string(),
            "Consider using try-except for error handling".to_string(),
        ];
        
        // Common pro tips for all personalities
        let common_tips = vec![
            "💡 Pro tip: Validate values before use".to_string(),
            "🚀 Boss tip: Use proper value handling in complex logic!".to_string(),
            "🎯 Smart tip: Consider using validation functions!".to_string(),
        ];
        
        if message.contains("invalid literal for int()") {
            let base = error.context.get("base").cloned().unwrap_or("10".to_string());
            let value = error.context.get("value").cloned().unwrap_or("value".to_string());
            
            // Specific fix suggestions for this ValueError
            let specific_fixes = vec![
                format!("Convert '{}' to a valid base {} number", value, base),
                "Use try-except to handle conversion errors gracefully".to_string(),
                "Check input format before conversion".to_string(),
            ];
            
            // Specific pro tips for this ValueError
            let specific_tips = vec![
                "💡 Pro tip: Validate input format before conversion".to_string(),
                "🚀 Boss tip: Use regex to validate number formats!".to_string(),
                "🎯 Smart tip: Consider using int() with proper error handling!".to_string(),
            ];
            
            match personality {
                PersonalityType::Encouraging => {
                    let messages = vec![
                        format!("You're trying to convert '{}' to an integer but it's not base {}", value, base),
                        format!("Almost there! '{}' isn't a valid number in base {}", value, base),
                        format!("One small fix: '{}' needs to be a valid base {} number", value, base),
                    ];
                    
                    (
                        messages[fastrand::usize(..messages.len())].clone(),
                        Some(specific_fixes[fastrand::usize(..specific_fixes.len())].clone()),
                        Some(specific_tips[fastrand::usize(..specific_tips.len())].clone()),
                    )
                }
                PersonalityType::Sarcastic => {
                    let messages = vec![
                        format!("Wow, '{}' really wanted to be a base {} number! 🙄", value, base),
                        format!("Invalid literal for int()? Never heard of validation! 📢"),
                    ];
                    
                    (
                        messages[fastrand::usize(..messages.len())].clone(),
                        Some(specific_fixes[fastrand::usize(..specific_fixes.len())].clone()),
                        Some(specific_tips[fastrand::usize(..specific_tips.len())].clone()),
                    )
                }
                PersonalityType::Educational => {
                    let messages = vec![
                        format!("ValueError occurs when converting invalid literal '{}' to int(base {})", value, base),
                        format!("int() requires valid number format for the specified base"),
                        format!("Base {} conversion requires valid characters for that base", base),
                    ];
                    
                    (
                        messages[fastrand::usize(..messages.len())].clone(),
                        Some(specific_fixes[fastrand::usize(..specific_fixes.len())].clone()),
                        Some(specific_tips[fastrand::usize(..specific_tips.len())].clone()),
                    )
                }
                PersonalityType::Professional => {
                    let messages = vec![
                        format!("ValueError: Invalid literal '{}' for int() with base {}", value, base),
                    ];
                    
                    (
                        messages[fastrand::usize(..messages.len())].clone(),
                        Some(specific_fixes[fastrand::usize(..specific_fixes.len())].clone()),
                        Some(specific_tips[fastrand::usize(..specific_tips.len())].clone()),
                    )
                }
                PersonalityType::Silly => {
                    let messages = vec![
                        format!("'{}' went on a vacation from base {}! 🏖️", value, base),
                        format!("'{}' is playing hide and seek in base {}! 🦜🕵️‍♀️", value, base),
                        format!("'{}' is in the Bermuda Triangle of base {}! 🌊", value, base),
                    ];
                    
                    (
                        messages[fastrand::usize(..messages.len())].clone(),
                        Some(specific_fixes[fastrand::usize(..specific_fixes.len())].clone()),
                        Some(specific_tips[fastrand::usize(..specific_tips.len())].clone()),
                    )
                }
            }
        } else {
            // Default case for other ValueError messages
            match personality {
                PersonalityType::Encouraging => (
                    "You're close! This value isn't working as expected! 🌟".to_string(),
                    Some(common_fixes[fastrand::usize(..common_fixes.len())].clone()),
                    Some(common_tips[fastrand::usize(..common_tips.len())].clone()),
                ),
                PersonalityType::Sarcastic => (
                    "Wow, this value really wanted to be special! 🙄".to_string(),
                    Some(common_fixes[fastrand::usize(..common_fixes.len())].clone()),
                    Some(common_tips[fastrand::usize(..common_tips.len())].clone()),
                ),
                PersonalityType::Educational => (
                    "ValueError occurs when a value doesn't work for an operation".to_string(),
                    Some(common_fixes[fastrand::usize(..common_fixes.len())].clone()),
                    Some(common_tips[fastrand::usize(..common_tips.len())].clone()),
                ),
                PersonalityType::Professional => (
                    "ValueError: Value is not valid for this operation".to_string(),
                    Some(common_fixes[fastrand::usize(..common_fixes.len())].clone()),
                    Some(common_tips[fastrand::usize(..common_tips.len())].clone()),
                ),
                PersonalityType::Silly => (
                    "Value went on a vacation! 🏖️".to_string(),
                    Some(common_fixes[fastrand::usize(..common_fixes.len())].clone()),
                    Some(common_tips[fastrand::usize(..common_tips.len())].clone()),
                ),
            }
        }
    }
    
    fn python_attribute_error_response(&self, error: &ParsedError, personality: &PersonalityType) -> (String, Option<String>, Option<String>) {
        let attribute = error.context.get("attribute").cloned().unwrap_or_else(|| "method".to_string());
        let object_type = error.context.get("object").cloned().unwrap_or_else(|| "object".to_string());
        
        let (messages, fixes, tips) = match personality {
            PersonalityType::Encouraging => (
                vec![
                    format!("The attribute '{}' is just hiding! We'll find it! 🔍", attribute),
                    format!("{} doesn't have '{}', but we can work around this! ✨", object_type, attribute),
                    "Attribute not found? No worries, let's explore the object! 🧭".to_string(),
                ],
                vec![
                    format!("Check if '{}' is spelled correctly", attribute),
                    format!("Use dir({}) to see available attributes", object_type),
                    "Verify you're calling the method on the right object type".to_string(),
                ],
                vec![
                    "💡 Tip: Use dir() to explore object capabilities!".to_string(),
                    " YYS Smart: Check documentation for correct method names!".to_string(),
                ]
            ),
            PersonalityType::Sarcastic => (
                vec![
                    format!("Oh, so '{}' doesn't have '{}'? Mind-blowing! 🙄", object_type, attribute),
                    format!("Did you just make up the method '{}'? Creative! 😏", attribute),
                    "Trying to use methods that don't exist? Bold strategy! 🤷‍♂️".to_string(),
                ],
                vec![
                    "Maybe CHECK what methods actually exist first?".to_string(),
                    "Try reading the documentation - revolutionary concept!".to_string(),
                    "Use dir() or help() to see real methods, not imaginary ones!".to_string(),
                ],
                vec![
                    "😏 Reality: Objects only have the methods they actually have!".to_string(),
                    "🙄 Shocker: You can't call methods that don't exist!".to_string(),
                ]
            ),
            PersonalityType::Educational => (
                vec![
                    format!("AttributeError: '{}' object has no attribute '{}'", object_type, attribute),
                    "This error occurs when trying to access a non-existent attribute or method.".to_string(),
                ],
                vec![
                    "Use hasattr(obj, 'attribute') to check if attribute exists".to_string(),
                    "Verify object type with type(obj) or isinstance()".to_string(),
                    "Check documentation for correct method names and signatures".to_string(),
                ],
                vec![
                    "🎓 Learning: Every object type has specific attributes".to_string(),
                    "📚 Knowledge: Use introspection tools to explore objects".to_string(),
                ]
            ),
            PersonalityType::Professional => (
                vec![
                    format!("AttributeError: Object type '{}' does not support attribute '{}'", object_type, attribute),
                ],
                vec![
                    "Verify object interface and available methods".to_string(),
                    "Implement proper type checking before method calls".to_string(),
                ],
                vec![
                    "Recommendation: Use static analysis tools to catch these early".to_string(),
                ]
            ),
            PersonalityType::Silly => (
                vec![
                    format!("BEEP BOOP! '{}' went looking for '{}' but found only empty space! 🚀🌌", object_type, attribute),
                    format!("*SQUAWK* Method '{}' is playing hide and seek and WON! 🦜🙈", attribute),
                    "Your object is missing some parts! Did you buy it from IKEA? 🪴🛠️".to_string(),
                ],
                vec![
                    "Give your object a full inspection with dir()!".to_string(),
                    "Maybe your method went on vacation?".to_string(),
                    "Try summoning the correct method with proper spelling!".to_string(),
                ],
                vec![
                    "🎪 Silly tip: Objects are like toolboxes - check what's inside!".to_string(),
                    "🦄 Fun fact: Attributes don't grow on trees!".to_string(),
                ]
            ),
        };
        
        let message = messages[fastrand::usize(..messages.len())].clone();
        let fix = Some(fixes[fastrand::usize(..fixes.len())].clone());
        let tip = Some(tips[fastrand::usize(..tips.len())].clone());
        
        (message, fix, tip)
    }
    
    fn python_zero_division_response(&self, error: &ParsedError, personality: &PersonalityType) -> (String, Option<String>, Option<String>) {
        let _operation = error.context.get("operation").cloned().unwrap_or_else(|| "division".to_string());
        
        let (messages, fixes, tips) = match personality {
            PersonalityType::Encouraging => (
                vec![
                    "Oops! Division by zero is a classic mistake! Easy fix! 📝".to_string(),
                    "Math doesn't like dividing by zero, but we can handle this! ✨".to_string(),
                    "Zero denominator detected - let's add some validation! 🔢".to_string(),
                ],
                vec![
                    "Check if denominator is zero before dividing: if b != 0:".to_string(),
                    "Use try-except to handle division by zero gracefully".to_string(),
                    "Add conditional logic to avoid zero denominators".to_string(),
                ],
                vec![
                    "💡 Tip: Always validate denominators in division!".to_string(),
                    " YYS Smart: Division by zero is undefined in mathematics!".to_string(),
                ]
            ),
            PersonalityType::Sarcastic => (
                vec![
                    "Oh, dividing by zero? Trying to break math itself? 🙄".to_string(),
                    "Congrats! You just tried to divide by zero. Math is crying! 😭".to_string(),
                    "Zero called - it doesn't want to be a denominator today! 📞".to_string(),
                ],
                vec![
                    "Maybe CHECK if you're dividing by zero first?".to_string(),
                    "Revolutionary idea: validate your denominators!".to_string(),
                    "Try using numbers other than zero for division!".to_string(),
                ],
                vec![
                    "😏 Reality: Zero division breaks the universe!".to_string(),
                    "🙄 Fun fact: Mathematicians hate this one trick!".to_string(),
                ]
            ),
            PersonalityType::Educational => (
                vec![
                    "ZeroDivisionError: Division by zero is mathematically undefined.".to_string(),
                    "This error occurs when the denominator in a division operation equals zero.".to_string(),
                ],
                vec![
                    "Implement zero-checking: if denominator != 0: result = a / b".to_string(),
                    "Use conditional statements to handle edge cases".to_string(),
                    "Consider what should happen when denominator is zero (return None, default value, etc.)".to_string(),
                ],
                vec![
                    "🎓 Learning: Division by zero is undefined in mathematics".to_string(),
                    "📚 Knowledge: Always validate mathematical operations".to_string(),
                ]
            ),
            PersonalityType::Professional => (
                vec![
                    "ZeroDivisionError: Cannot perform division operation with zero denominator.".to_string(),
                ],
                vec![
                    "Implement denominator validation before division operations".to_string(),
                    "Add appropriate error handling for edge cases".to_string(),
                ],
                vec![
                    "Recommendation: Use defensive programming for mathematical operations".to_string(),
                ]
            ),
            PersonalityType::Silly => (
                vec![
                    "BEEP BOOP! You broke the math machine with zero! 🤖🔥".to_string(),
                    "*SQUAWK* Zero refuses to be a denominator! It's on strike! 🦜🪝".to_string(),
                    "Math.exe has stopped working due to zero division! 💻❌".to_string(),
                ],
                vec![
                    "Give zero a different job - it doesn't like being a denominator!".to_string(),
                    "Teach your numbers to avoid zero in the denominator!".to_string(),
                    "Send zero to timeout until it agrees to cooperate!".to_string(),
                ],
                vec![
                    "🎪 Silly tip: Zero is like kryptonite to division!".to_string(),
                    "🦄 Fun fact: Calculators get confused by zero division too!".to_string(),
                ]
            ),
        };
        
        let message = messages[fastrand::usize(..messages.len())].clone();
        let fix = Some(fixes[fastrand::usize(..fixes.len())].clone());
        let tip = Some(tips[fastrand::usize(..tips.len())].to_string());
        
        (message, fix, tip)
    }
    
    fn python_indentation_error_response(&self, error: &ParsedError, personality: &PersonalityType) -> (String, Option<String>, Option<String>) {
        let _line = error.context.get("line").cloned().unwrap_or_else(|| "unknown".to_string());
        
        let (messages, fixes, tips) = match personality {
            PersonalityType::Encouraging => (
                vec![
                    "Indentation troubles? Python can be picky, but you've got this! 📌".to_string(),
                    "Just a spacing issue - easily fixed! ✨".to_string(),
                    "Python loves consistent indentation, let's give it what it wants! 🚀".to_string(),
                ],
                vec![
                    "Use consistent indentation throughout your code (4 spaces recommended)".to_string(),
                    "Check for mixed tabs and spaces - pick one and stick with it".to_string(),
                    "Align your code blocks properly with the same indentation level".to_string(),
                ],
                vec![
                    "💡 Tip: Configure your editor to show whitespace characters!".to_string(),
                    " YYS Smart: Use an auto-formatter like black or autopep8!".to_string(),
                ]
            ),
            PersonalityType::Sarcastic => (
                vec![
                    "Oh, Python's whitespace obsession strikes again! 🙄".to_string(),
                    "Indentation error? In Python? What are the odds! 😏".to_string(),
                    "Let me guess - tabs vs spaces warfare? 🤷‍♂️".to_string(),
                ],
                vec![
                    "Maybe try CONSISTENT spacing? Novel concept!".to_string(),
                    "Pick tabs OR spaces, not a chaotic mix of both!".to_string(),
                    "Use an editor that understands Python indentation!".to_string(),
                ],
                vec![
                    "😏 Reality: Python judges your whitespace choices!".to_string(),
                    "🙄 Pro tip: Indentation isn't just for looks in Python!".to_string(),
                ]
            ),
            PersonalityType::Educational => (
                vec![
                    "IndentationError: Python uses indentation to define code blocks.".to_string(),
                    "Inconsistent indentation detected - Python requires uniform spacing.".to_string(),
                ],
                vec![
                    "Use exactly 4 spaces for each indentation level (PEP 8 standard)".to_string(),
                    "Avoid mixing tabs and spaces - configure your editor properly".to_string(),
                    "Ensure all code in the same block has identical indentation".to_string(),
                ],
                vec![
                    "🎓 Learning: Python's indentation is part of its syntax".to_string(),
                    "📚 Knowledge: PEP 8 recommends 4 spaces per indentation level".to_string(),
                ]
            ),
            PersonalityType::Professional => (
                vec![
                    "IndentationError: Inconsistent or incorrect code block indentation.".to_string(),
                ],
                vec![
                    "Implement consistent indentation scheme across codebase".to_string(),
                    "Configure development environment for Python standards".to_string(),
                ],
                vec![
                    "Recommendation: Use automated formatting tools for consistency".to_string(),
                ]
            ),
            PersonalityType::Silly => (
                vec![
                    "BEEP BOOP! Your code's spacing is doing the cha-cha! 🤖💃".to_string(),
                    "*SQUAWK* Python is having a whitespace meltdown! 🦜😱".to_string(),
                    "Your indentation is more mixed up than a jigsaw puzzle! 🧩🔍".to_string(),
                ],
                vec![
                    "Teach your spaces to march in formation!".to_string(),
                    "Give your code a good straightening with proper indentation!".to_string(),
                    "Send your tabs and spaces to couples therapy!".to_string(),
                ],
                vec![
                    "🎪 Silly tip: Python is a neat freak about spacing!".to_string(),
                    "🦄 Fun fact: Tabs and spaces are mortal enemies in Python!".to_string(),
                ]
            ),
        };
        
        let message = messages[fastrand::usize(..messages.len())].clone();
        let fix = Some(fixes[fastrand::usize(..fixes.len())].clone());
        let tip = Some(tips[fastrand::usize(..tips.len())].to_string());
        
        (message, fix, tip)
    }
    
    fn python_import_error_response(&self, error: &ParsedError, personality: &PersonalityType) -> (String, Option<String>, Option<String>) {
        let module = error.context.get("module").cloned().unwrap_or_else(|| "module".to_string());
        
        let (messages, fixes, tips) = match personality {
            PersonalityType::Encouraging => (
                vec![
                    format!("Can't import '{}'? No worries, we'll get it sorted! 📦", module),
                    "Import issues are super common - let's fix this together! ✨".to_string(),
                    format!("Module '{}' is playing hard to get, but we can find it! 🔍", module),
                ],
                vec![
                    format!("Check if '{}' is installed: pip list | grep {}", module, module),
                    format!("Install the module: pip install {}", module),
                    "Verify the module name spelling and check your Python path".to_string(),
                ],
                vec![
                    "💡 Tip: Use 'pip list' to see installed packages!".to_string(),
                    " YYS Smart: Check PyPI for the correct package name!".to_string(),
                ]
            ),
            PersonalityType::Sarcastic => (
                vec![
                    format!("Oh, '{}' doesn't exist? What a shocker! 🙄", module),
                    format!("Let me guess - you forgot to install '{}'? 😏", module),
                    "Import error? In Python? Never seen that before! 🤷‍♂️".to_string(),
                ],
                vec![
                    "Maybe try INSTALLING the package first? Revolutionary!".to_string(),
                    "Check if you spelled the module name correctly - crazy idea!".to_string(),
                    "Use 'pip install' like the rest of the civilized world!".to_string(),
                ],
                vec![
                    "😏 Reality: Modules don't install themselves!".to_string(),
                    "🙄 Fun fact: pip is your friend, use it!".to_string(),
                ]
            ),
            PersonalityType::Educational => (
                vec![
                    format!("ImportError: Module '{}' could not be found or imported.", module),
                    "This error occurs when Python cannot locate the specified module.".to_string(),
                ],
                vec![
                    "Verify module installation with 'pip list' or 'conda list'".to_string(),
                    "Check PYTHONPATH environment variable for module location".to_string(),
                    "Ensure correct virtual environment is activated".to_string(),
                ],
                vec![
                    "🎓 Learning: Python searches specific paths for modules".to_string(),
                    "📚 Knowledge: Virtual environments isolate package installations".to_string(),
                ]
            ),
            PersonalityType::Professional => (
                vec![
                    format!("ImportError: Module '{}' not found in Python path.", module),
                ],
                vec![
                    "Verify package installation and dependencies".to_string(),
                    "Check project requirements and environment configuration".to_string(),
                ],
                vec![
                    "Recommendation: Use requirements.txt for dependency management".to_string(),
                ]
            ),
            PersonalityType::Silly => (
                vec![
                    format!("BEEP BOOP! Module '{}' is hiding in the digital jungle! 🤖🌳", module),
                    format!("*SQUAWK* '{}' has vanished into the import void! 🦜🌌", module),
                    "Your module went on an adventure and forgot to come back! 🎢🗺️".to_string(),
                ],
                vec![
                    "Send a search party with 'pip install' to find your module!".to_string(),
                    "Maybe your module is lost in the package dimension?".to_string(),
                    "Try summoning it with the ancient pip incantation!".to_string(),
                ],
                vec![
                    "🎪 Silly tip: Modules are like shy pets - they need proper homes!".to_string(),
                    "🦄 Fun fact: pip is like a module delivery service!".to_string(),
                ]
            ),
        };
        
        let message = messages[fastrand::usize(..messages.len())].clone();
        let fix = Some(fixes[fastrand::usize(..fixes.len())].clone());
        let tip = Some(tips[fastrand::usize(..tips.len())].clone());
        
        (message, fix, tip)
    }
    
    fn python_file_not_found_response(&self, _error: &ParsedError, _personality: &PersonalityType) -> (String, Option<String>, Option<String>) {
        ("FileNotFoundError: The file you're looking for doesn't exist! 🗂️".to_string(), Some("Check file path and name spelling".to_string()), Some("💡 Tip: Use os.path.exists() to check first!".to_string()))
    }
    
    fn python_recursion_error_response(&self, _error: &ParsedError, _personality: &PersonalityType) -> (String, Option<String>, Option<String>) {
        ("RecursionError: Infinite recursion detected! 🌀".to_string(), Some("Add base case to stop recursion".to_string()), Some("💡 Tip: Every recursive function needs an exit condition!".to_string()))
    }
    
    fn python_assertion_error_response(&self, _error: &ParsedError, _personality: &PersonalityType) -> (String, Option<String>, Option<String>) {
        ("AssertionError: Your assumption was wrong! 🤔".to_string(), Some("Check the assertion condition".to_string()), Some("💡 Tip: Assertions are for debugging, not error handling!".to_string()))
    }
    
    fn python_unbound_local_response(&self, _error: &ParsedError, _personality: &PersonalityType) -> (String, Option<String>, Option<String>) {
        ("UnboundLocalError: Variable referenced before assignment! 🔄".to_string(), Some("Initialize variable before use in function".to_string()), Some("💡 Tip: Python sees assignment as creating a local variable!".to_string()))
    }
    
    fn python_permission_error_response(&self, _error: &ParsedError, _personality: &PersonalityType) -> (String, Option<String>, Option<String>) {
        ("PermissionError: Access denied! 🚫".to_string(), Some("Check file/directory permissions".to_string()), Some("💡 Tip: Run with appropriate privileges or check ownership!".to_string()))
    }
    
    fn python_overflow_error_response(&self, _error: &ParsedError, _personality: &PersonalityType) -> (String, Option<String>, Option<String>) {
        ("OverflowError: Number too large! 📈".to_string(), Some("Use smaller numbers or different data types".to_string()), Some("💡 Tip: Consider using Decimal for precision!".to_string()))
    }
    
    fn python_memory_error_response(&self, _error: &ParsedError, _personality: &PersonalityType) -> (String, Option<String>, Option<String>) {
        ("MemoryError: Out of memory! 💾".to_string(), Some("Reduce data size or optimize memory usage".to_string()), Some("💡 Tip: Process data in chunks or use generators!".to_string()))
    }
    
    fn python_keyboard_interrupt_response(&self, _error: &ParsedError, personality: &PersonalityType) -> (String, Option<String>, Option<String>) {
        let (messages, fixes, tips) = match personality {
            PersonalityType::Encouraging => (
                vec![
                    "Ctrl+C pressed! You're in control! 🎮".to_string(),
                    "Keyboard interrupt - you stopped the show! ✨".to_string(),
                    "Manual stop detected - that's totally normal! 🔄".to_string(),
                ],
                vec![
                    "This is expected when you press Ctrl+C to stop execution".to_string(),
                    "Use try-except KeyboardInterrupt for graceful shutdown".to_string(),
                    "Add cleanup code in finally blocks if needed".to_string(),
                ],
                vec![
                    "💡 Tip: Handle KeyboardInterrupt for clean exits!".to_string(),
                    " YYS Smart: Use signal handlers for advanced control!".to_string(),
                ]
            ),
            PersonalityType::Sarcastic => (
                vec![
                    "Oh, you pressed Ctrl+C? What a revelation! 🙄".to_string(),
                    "Keyboard interrupt? Let me guess - you got impatient! 😏".to_string(),
                    "Manual stop? Couldn't wait for the program to finish? 🤷‍♂️".to_string(),
                ],
                vec![
                    "This is what happens when you interrupt things!".to_string(),
                    "Maybe let programs finish next time?".to_string(),
                    "Try the patience virtue - it's surprisingly effective!".to_string(),
                ],
                vec![
                    "😏 Reality: Ctrl+C stops things - who knew!".to_string(),
                    "🙄 Fun fact: Patience is a virtue!".to_string(),
                ]
            ),
            PersonalityType::Educational => (
                vec![
                    "KeyboardInterrupt: User manually stopped execution with Ctrl+C.".to_string(),
                    "This is a normal way to stop running programs.".to_string(),
                ],
                vec![
                    "Handle KeyboardInterrupt exceptions for graceful program termination".to_string(),
                    "Use signal handling for more sophisticated interrupt management".to_string(),
                    "Implement cleanup procedures in finally blocks".to_string(),
                ],
                vec![
                    "🎓 Learning: KeyboardInterrupt is a built-in exception".to_string(),
                    "📚 Knowledge: Ctrl+C sends SIGINT signal to programs".to_string(),
                ]
            ),
            PersonalityType::Professional => (
                vec![
                    "KeyboardInterrupt: Manual program termination requested.".to_string(),
                ],
                vec![
                    "Implement proper exception handling for user interruptions".to_string(),
                    "Ensure graceful shutdown procedures".to_string(),
                ],
                vec![
                    "Recommendation: Always handle KeyboardInterrupt in long-running processes".to_string(),
                ]
            ),
            PersonalityType::Silly => (
                vec![
                    "BEEP BOOP! Emergency stop button activated! 🤖🛑".to_string(),
                    "*SQUAWK* You pulled the plug on the digital circus! 🦜🎪".to_string(),
                    "Program.exe has left the chat! Thanks for the timeout! 💻👋".to_string(),
                ],
                vec![
                    "Your program got stage fright and ran away!".to_string(),
                    "Maybe your code needed a coffee break anyway!".to_string(),
                    "Send a thank you note to Ctrl+C for the rescue!".to_string(),
                ],
                vec![
                    "🎪 Silly tip: Ctrl+C is like a digital escape hatch!".to_string(),
                    "🦄 Fun fact: Programs dream of running forever!".to_string(),
                ]
            ),
        };
        
        let message = messages[fastrand::usize(..messages.len())].clone();
        let fix = Some(fixes[fastrand::usize(..fixes.len())].clone());
        let tip = Some(tips[fastrand::usize(..tips.len())].to_string());
        
        (message, fix, tip)
    }

    fn syntax_error_response(
        &self,
        _error: &ParsedError,
        personality: &PersonalityType,
    ) -> (String, Option<String>, Option<String>) {
        let sassy_messages = [
            "Well well well... what do we have here? 🤔",
            "Oh honey, that syntax needs some serious help! 💅",
            "Bruh... did autocorrect write this code? 😏", 
            "I've seen better syntax in my sleep! 😴",
            "This code is giving me second-hand embarrassment! 😬",
        ];
        
        let encouraging_messages = [
            "You're SO close! Just one tiny fix needed! ✨",
            "Almost there champ! One small adjustment! 🌟",
            "Hey, we all make typos - you got this! 💪",
            "Just a little syntax hiccup, easily fixed! 🔧",
            "You're doing great! One quick correction coming up! 🚀",
        ];
        
        let educational_messages = [
            "Let's break this down step by step! 🎓",
            "Here's what's happening with your syntax... 📚",
            "Time for a quick syntax lesson! 🧑‍🏫",
            "Understanding this error will make you stronger! 💡",
            "Let me explain what's going wrong here... 📖",
        ];
        
        let message = match personality {
            PersonalityType::Encouraging => {
                encouraging_messages[fastrand::usize(..encouraging_messages.len())].to_string()
            }
            PersonalityType::Sarcastic => {
                sassy_messages[fastrand::usize(..sassy_messages.len())].to_string()
            }
            PersonalityType::Educational => {
                educational_messages[fastrand::usize(..educational_messages.len())].to_string()
            }
            PersonalityType::Professional => "Syntax error detected in code structure.".to_string(),
            PersonalityType::Silly => {
                let silly_messages = [
                    "SQUAWK! Your parentheses are having a fight! 🦜⚔️",
                    "Beep boop! Syntax malfunction detected! 🤖",
                    "*confused parrot noises* What even is this?! 🦜❓", 
                    "My circuits are confused by this code! 🔌💫",
                    "Alert! Alert! Code emergency in progress! 🚨",
                ];
                silly_messages[fastrand::usize(..silly_messages.len())].to_string()
            }
        };

        let quick_fixes = [
            "Check for missing parentheses, brackets, or quotes",
            "Look for unmatched brackets or braces", 
            "Verify all strings are properly closed",
            "Check if you forgot a comma or semicolon",
            "Make sure indentation is consistent",
        ];
        
        let pro_tips = [
            "💡 Pro tip: Most editors highlight matching brackets!",
            "🔥 Hot tip: Use a linter to catch these early!",
            "✨ Ninja tip: Auto-formatters can prevent this!",
            "🎯 Smart tip: Copy-paste errors are super common!",
            "🚀 Boss tip: Take breaks - tired eyes miss syntax errors!", 
        ];
        
        let quick_fix = Some(quick_fixes[fastrand::usize(..quick_fixes.len())].to_string());
        let pro_tip = Some(pro_tips[fastrand::usize(..pro_tips.len())].to_string());

        (message, quick_fix, pro_tip)
    }

    fn runtime_error_response(
        &self,
        error: &ParsedError,
        personality: &PersonalityType,
    ) -> (String, Option<String>, Option<String>) {
        let name = error.context.get("name").cloned().unwrap_or_else(|| "something".to_string());
        
        let sassy_runtime_messages = [
            format!("Oh please... '{}' doesn't exist and you know it! 🙄", name),
            format!("Seriously? You're looking for '{}' that doesn't exist? 🤦", name),
            format!("'{}' called in sick today. Try again tomorrow! 😏", name),
            format!("Breaking news: '{}' was never declared! Shocking! 📢", name),
            format!("GPS can't find '{}' because it doesn't exist! 🗺️", name),
        ];
        
        let encouraging_runtime_messages = [
            format!("Almost there! Just need to define '{}' first! 🎆", name),
            format!("You're doing great! '{}' just needs to be declared! ✨", name),
            format!("So close! Let's get '{}' properly set up! 🚀", name),
            format!("One small step: define '{}' and you're golden! 🌟", name),
            format!("You've got this! '{}' is just missing its introduction! 💫", name),
        ];
        
        let educational_runtime_messages = [
            format!("Variable '{}' needs to be declared before use. Let me explain...", name),
            format!("The identifier '{}' is not in scope. Here's how to fix it:", name),
            format!("Runtime error: '{}' is undefined. Let's understand why:", name),
            format!("Scope issue detected with '{}'. Here's the solution:", name),
            format!("Declaration missing for '{}'. Learning moment:", name),
        ];
        
        let message = match personality {
            PersonalityType::Encouraging => {
                encouraging_runtime_messages[fastrand::usize(..encouraging_runtime_messages.len())].clone()
            }
            PersonalityType::Sarcastic => {
                sassy_runtime_messages[fastrand::usize(..sassy_runtime_messages.len())].clone()
            }
            PersonalityType::Educational => {
                educational_runtime_messages[fastrand::usize(..educational_runtime_messages.len())].clone()
            }
            PersonalityType::Professional => format!("Runtime error: '{}' is not defined.", name),
            PersonalityType::Silly => {
                let silly_runtime_messages = [
                    format!("BEEP BOOP! '{}' has left the building! 🤖🏢", name),
                    format!("*dramatic gasp* '{}' has vanished into thin air! 😱💫", name),
                    format!("Where in the world is '{}'? Carmen Sandiego knows! 🕵️‍♀️", name),
                    format!("'{}' went on vacation without telling anyone! 🏖️", name),
                    format!("SQUAWK! '{}' flew the coop! 🦜🚀", name),
                ];
                silly_runtime_messages[fastrand::usize(..silly_runtime_messages.len())].clone()
            }
        };

        let quick_fixes = [
            format!("Declare '{}' before using it", name),
            format!("Check the spelling of '{}'", name), 
            format!("Import '{}' if it's from another module", name),
            format!("Initialize '{}' with a value", name),
            format!("Verify '{}' is in the correct scope", name),
        ];
        
        let pro_tips = [
            "💡 Pro tip: Use your IDE's autocomplete to avoid typos!",
            "🔥 Hot tip: Most editors show undefined variables in red!",
            "✨ Ninja tip: Declare variables at the top for clarity!",
            "🎯 Smart tip: Use meaningful variable names!",
            "🚀 Boss tip: Initialize variables when you declare them!",
        ];
        
        let quick_fix = Some(quick_fixes[fastrand::usize(..quick_fixes.len())].clone());
        let pro_tip = Some(pro_tips[fastrand::usize(..pro_tips.len())].to_string());

        (message, quick_fix, pro_tip)
    }
}