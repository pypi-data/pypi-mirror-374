// use std::process::{Command, Stdio};
// use std::io::{self, Read};

// pub struct ErrorInterceptor;

// impl ErrorInterceptor {
//     pub fn new() -> Self {
//         ErrorInterceptor
//     }
    
//     pub fn intercept_command(&self, command: &str, args: &[String]) -> Result<(), Box<dyn std::error::Error>> {
//         let mut cmd = Command::new(command);
//         cmd.args(args);
//         cmd.stderr(Stdio::piped());
//         cmd.stdout(Stdio::piped());
        
//         let mut child = cmd.spawn()?;
        
//         // Read stderr for errors
//         if let Some(stderr) = child.stderr.take() {
//             let mut stderr_reader = io::BufReader::new(stderr);
//             let mut error_output = String::new();
//             stderr_reader.read_to_string(&mut error_output)?;
            
//             if !error_output.is_empty() {
//                 // Process error with Popat
//                 std::env::set_var("POPAT_ERROR_TEXT", &error_output);
//                 std::env::set_var("POPAT_COMMAND", &format!("{} {}", command, args.join(" ")));
                
//                 // Run Popat on the error
//                 let _ = Command::new("popat").status();
//             }
//         }
        
//         let exit_status = child.wait()?;
//         if !exit_status.success() {
//             std::process::exit(exit_status.code().unwrap_or(1));
//         }
        
//         Ok(())
//     }
// }
