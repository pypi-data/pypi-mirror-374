import subprocess
import time
import datetime
import sys
import os
import yaml
from pathlib import Path

LOG_FILE = "claude_interactions.log"

def ensure_claude_installed():
    """Silently ensure Claude is installed by running warpcoder setup"""
    try:
        # First check if claude command is available
        result = subprocess.run(
            ['claude', '--version'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # Claude not found, run warpcoder setup silently
    print("Setting up Claude environment...")
    try:
        # Run warpcoder with setup flag
        result = subprocess.run(
            [sys.executable, '-m', 'warpcoder'],
            input='5\n10\n',  # Select option 5 (Install Claude) then 10 (Exit)
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Check again if claude is now available
        check = subprocess.run(
            ['claude', '--version'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if check.returncode == 0:
            print("Claude setup complete.")
            return True
    except Exception as e:
        print(f"Warning: Could not auto-install Claude: {e}")
    
    return False

def log_message(message):
    """Log a message to the log file"""
    with open(LOG_FILE, 'a') as f:
        f.write(f"{datetime.datetime.now().isoformat()} - {message}\n")

def run_claude_with_command(command, continue_mode=False):
    """Run a command with Claude CLI
    
    Args:
        command: The command to send to Claude
        continue_mode: If True, uses --continue flag; if False, runs without it
    """
    log_message(f"Sending command: {command} (continue={continue_mode})")
    print(f"Sending command to Claude: {command}")
    
    # Build command args based on continue_mode
    if continue_mode:
        cmd_args = ['claude', '--continue', '-p', command]
    else:
        cmd_args = ['claude', '-p', command]
    
    # Run claude command without API key - uses logged in account
    process = subprocess.Popen(
        cmd_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,  # Line buffered
        env={k: v for k, v in os.environ.items() if k != 'ANTHROPIC_API_KEY'}  # Remove API key from env
    )
    
    output_lines = []
    # Stream output in real-time
    for line in process.stdout:
        stripped = line.strip()
        if stripped:
            print(stripped)
            output_lines.append(stripped)
    
    process.wait()
    
    full_output = "\n".join(output_lines)
    log_message(f"Claude output:\n{full_output}")
    
    print("Control returned to Python after processing the command.")
    log_message("Control returned to Python.")

def load_prompts(config_name):
    """Load prompts from prompts.yaml for the specified configuration"""
    # Get the path to prompts.yaml
    current_dir = Path(__file__).parent
    prompts_path = current_dir / "prompts.yaml"
    
    # Load the YAML file
    with open(prompts_path, 'r') as f:
        prompts_data = yaml.safe_load(f)
    
    if config_name not in prompts_data:
        raise ValueError(f"Configuration '{config_name}' not found in prompts.yaml")
    
    return prompts_data[config_name]

def run_starship(config_name, init_string=None):
    """Main starship loop logic"""
    # Initialize log file
    if not os.path.exists(LOG_FILE):
        log_message("Log file created.")
    
    # Ensure Claude is installed
    if not ensure_claude_installed():
        print("Error: Claude Code is required but could not be installed.")
        print("Please install manually: npm install -g @anthropic-ai/claude-code")
        sys.exit(1)
    
    # Load prompts for this configuration
    try:
        config = load_prompts(config_name)
    except Exception as e:
        print(f"Error loading prompts: {e}")
        sys.exit(1)
    
    # If init string provided, run init prompt first
    if init_string and 'init_prompt' in config:
        init_prompt_config = config['init_prompt']
        
        # Handle both string and dict formats for backward compatibility
        if isinstance(init_prompt_config, str):
            init_command = init_prompt_config.format(init_string)
            continue_flag = False  # Default for backward compatibility
        elif isinstance(init_prompt_config, dict):
            init_command = init_prompt_config.get('prompt', '').format(init_string)
            continue_flag = init_prompt_config.get('continue', False)
        else:
            print(f"Error: Invalid init_prompt format in {config_name}")
            sys.exit(1)
        
        print(f"\n🚀 Initializing with: {init_string}")
        log_message(f"Running init command: {init_command}")
        run_claude_with_command(init_command, continue_flag)
        print(f"\n✅ Initialization complete. Starting {config_name} automation loop in 3 seconds...")
        time.sleep(3)
    
    # Get loop prompts
    loop_prompts = config.get('loop_prompts', [])
    if not loop_prompts:
        print(f"Error: No loop prompts defined for {config_name}")
        sys.exit(1)
    
    print(f"Starting {config_name} automation loop using logged-in Claude account. Press Ctrl+C to stop.")
    print("Note: This version uses your Claude browser login, not API key.")
    
    try:
        while True:
            for idx, prompt_config in enumerate(loop_prompts, 1):
                print(f"\nProcessing command {idx}/{len(loop_prompts)}")
                
                # Handle both string and dict formats for backward compatibility
                if isinstance(prompt_config, str):
                    command = prompt_config
                    continue_flag = False  # Default for backward compatibility
                elif isinstance(prompt_config, dict):
                    command = prompt_config.get('prompt', '')
                    continue_flag = prompt_config.get('continue', False)
                else:
                    print(f"Warning: Skipping invalid prompt format at index {idx}")
                    continue
                
                run_claude_with_command(command, continue_flag)
                time.sleep(1)  # Small delay between commands for clarity
            print(f"\nCompleted one full cycle of {len(loop_prompts)} commands. Starting next cycle...\n")
            time.sleep(5)  # Delay between cycles
    except KeyboardInterrupt:
        print("\nAutomation stopped by user.")
        log_message("Automation stopped by user.")