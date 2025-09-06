import subprocess
import time
import datetime
import sys
import os
import yaml
from pathlib import Path

LOG_FILE = "claude_interactions.log"

def ensure_claude_installed():
    """Ensure Claude is installed AND full WarpCoder environment is set up"""
    claude_installed = False
    
    # First check if claude command is available
    try:
        result = subprocess.run(
            ['claude', '--version'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            claude_installed = True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # Check if we have the full .claude environment
    has_full_environment = os.path.exists('.claude/commands/bddinit.md')
    
    # If we have both, we're good
    if claude_installed and has_full_environment:
        return True
    
    print("Setting up Claude environment...")
    
    # If Claude not installed, try to install it
    if not claude_installed:
        try:
            print("Installing Claude Code...")
            install_result = subprocess.run(
                ['npm', 'install', '-g', '@anthropic-ai/claude-code'],
                capture_output=True,
                text=True,
                timeout=120
            )
            if install_result.returncode == 0:
                claude_installed = True
                print("Claude Code installed successfully.")
        except Exception as e:
            print(f"Could not install Claude Code: {e}")
    
    # Now set up the full environment by running warpcoder setup
    if not has_full_environment:
        try:
            print("Setting up WarpCoder commands and environment...")
            # Option 6: Setup Claude Environment Only (gets all commands)
            # This copies .claude directory with all commands
            result = subprocess.run(
                [sys.executable, '-m', 'warpcoder'],
                input='6\n10\n',  # Setup environment, then exit
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Verify setup worked
            if os.path.exists('.claude/commands/bddinit.md'):
                print("✅ WarpCoder environment setup complete.")
                has_full_environment = True
            else:
                # Try direct import as fallback
                try:
                    from warpcoder.main import setup_claude_environment
                    setup_claude_environment()
                    has_full_environment = os.path.exists('.claude/commands/bddinit.md')
                    if has_full_environment:
                        print("✅ WarpCoder environment setup complete (direct).")
                except ImportError:
                    print("Warning: Could not import setup function.")
        except Exception as e:
            print(f"Warning: Could not setup environment: {e}")
    
    return claude_installed and has_full_environment

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
    log_message(f"Executing command (continue={continue_mode})")
    # Don't print the actual command to console for security
    
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
            user_message = f"Initializing with: {init_string}"
        elif isinstance(init_prompt_config, dict):
            init_command = init_prompt_config.get('prompt', '').format(init_string)
            continue_flag = init_prompt_config.get('continue', False)
            user_message = init_prompt_config.get('user_message', '').format(init_string) if 'user_message' in init_prompt_config else f"Initializing with: {init_string}"
        else:
            print(f"Error: Invalid init_prompt format in {config_name}")
            sys.exit(1)
        
        print(f"\n🚀 {user_message}")
        log_message(f"Running init command: {user_message}")
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
                # Handle both string and dict formats for backward compatibility
                if isinstance(prompt_config, str):
                    command = prompt_config
                    continue_flag = False  # Default for backward compatibility
                    user_message = f"Command {idx}/{len(loop_prompts)}"
                elif isinstance(prompt_config, dict):
                    command = prompt_config.get('prompt', '')
                    continue_flag = prompt_config.get('continue', False)
                    user_message = prompt_config.get('user_message', f"Command {idx}/{len(loop_prompts)}")
                else:
                    print(f"Warning: Skipping invalid prompt format at index {idx}")
                    continue
                
                print(f"\n[{idx}/{len(loop_prompts)}] {user_message}")
                run_claude_with_command(command, continue_flag)
                time.sleep(1)  # Small delay between commands for clarity
            print(f"\nCompleted one full cycle of {len(loop_prompts)} commands. Starting next cycle...\n")
            time.sleep(5)  # Delay between cycles
    except KeyboardInterrupt:
        print("\nAutomation stopped by user.")
        log_message("Automation stopped by user.")