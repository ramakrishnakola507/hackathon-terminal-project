import os
import subprocess
import shlex
import psutil
import re
import shutil
from flask import Flask, request, jsonify, render_template_string

# --- Flask App Initialization ---
app = Flask(__name__)
current_working_directory = [os.getcwd()]

# --- HTML, CSS, and JavaScript for the Frontend ---
# No changes needed in the frontend. It's already enhanced.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI-Powered Web Terminal</title>
    <style>
        body { background-color: #121212; color: #e0e0e0; font-family: 'Fira Code', 'Consolas', monospace; font-size: 15px; margin: 0; padding: 20px; }
        h1 { color: #00aaff; border-bottom: 1px solid #333; padding-bottom: 10px; font-weight: 500;}
        #terminal { width: 100%; height: 70vh; background-color: #0a0a0a; border: 1px solid #333; border-radius: 8px; overflow-y: auto; padding: 15px; box-sizing: border-box; line-height: 1.6; }
        .terminal-line { white-space: pre-wrap; word-wrap: break-word; }
        .prompt { color: #00aaff; font-weight: bold; }
        .command { color: #f0e68c; }
        .output { color: #e0e0e0; }
        .error { color: #ff6b6b; }
        .ai-output { color: #82aaff; font-style: italic; }
        #input-form { display: flex; margin-top: 15px; }
        #prompt-label { color: #00ddff; padding-right: 10px; font-weight: bold; }
        #command-input { flex-grow: 1; background-color: transparent; border: none; color: #e0e0e0; font-family: inherit; font-size: inherit; outline: none; }
        .help-text { color: #888; margin-top: 15px; font-size: 13px; }
        .help-text code { background-color: #222; padding: 3px 6px; border-radius: 4px; color: #a9b7c6; }
    </style>
</head>
<body>
    <h1>AI-Powered Web Terminal</h1>
    <div id="terminal">
        <div class="terminal-line output">Welcome! Type 'help' for commands or use natural language (e.g., 'ai create a folder named reports').</div>
    </div>
    <form id="input-form">
        <label for="command-input" id="prompt-label">></label>
        <input type="text" id="command-input" autocomplete="off" autofocus>
    </form>
    <div class="help-text">
        <p><strong>Features:</strong> Command History (↑/↓), Tab Completion, and AI Commands (<code>ai ...</code>)</p>
    </div>

    <script>
        const terminal = document.getElementById('terminal');
        const form = document.getElementById('input-form');
        const input = document.getElementById('command-input');
        
        const commandHistory = [];
        let historyIndex = -1;
        const availableCommands = ['ls', 'cd', 'pwd', 'mkdir', 'rm', 'sysinfo', 'help', 'clear', 'ai'];

        input.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowUp') {
                e.preventDefault();
                if (historyIndex < commandHistory.length - 1) {
                    historyIndex++;
                    input.value = commandHistory[commandHistory.length - 1 - historyIndex];
                }
            } else if (e.key === 'ArrowDown') {
                e.preventDefault();
                if (historyIndex > 0) {
                    historyIndex--;
                    input.value = commandHistory[commandHistory.length - 1 - historyIndex];
                } else {
                    historyIndex = -1;
                    input.value = '';
                }
            } else if (e.key === 'Tab') {
                e.preventDefault();
                const currentVal = input.value.toLowerCase();
                const matchingCommands = availableCommands.filter(c => c.startsWith(currentVal));
                if (matchingCommands.length > 0) {
                    const currentIndex = matchingCommands.indexOf(currentVal);
                    const nextIndex = (currentIndex + 1) % matchingCommands.length;
                    input.value = matchingCommands[nextIndex];
                }
            } else {
                historyIndex = -1;
            }
        });

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const commandText = input.value.trim();
            if (!commandText) return;

            commandHistory.push(commandText);
            historyIndex = -1;
            
            appendTerminalLine(`> ${commandText}`, 'prompt', 'command');
            input.value = '';

            if (commandText.toLowerCase() === 'clear') {
                terminal.innerHTML = '';
                return;
            }

            try {
                const response = await fetch('/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: commandText })
                });
                const data = await response.json();
                if (data.ai_translation) appendTerminalLine(`AI Action: [${data.ai_translation}]`, 'ai-output');
                if (data.output) appendTerminalLine(data.output, 'output');
                if (data.error) appendTerminalLine(data.error, 'error');
            } catch (err) {
                appendTerminalLine(`Client-side error: ${err}`, 'error');
            }
        });

        function appendTerminalLine(text, ...classNames) {
            const line = document.createElement('div');
            line.className = 'terminal-line';
            line.classList.add(...classNames);
            line.textContent = text;
            terminal.appendChild(line);
            terminal.scrollTop = terminal.scrollHeight;
        }
    </script>
</body>
</html>
"""

# --- AI Natural Language Parser (UPGRADED) ---
def parse_natural_language(nl_command):
    """
    Translates natural language queries into a structured command tuple (action, args).
    This is far more robust than translating to a simple string.
    """
    nl_command = nl_command.lower().strip()
    
    # Pattern: create/make a folder/directory named/called [name]
    match = re.search(r"(create|make).*(folder|directory)\s(?:named|called)?\s*['\"]?([\w\.-]+)['\"]?", nl_command)
    if match:
        return ('create_folder', [match.group(3)], f"Create folder '{match.group(3)}'")
        
    # Pattern: delete/remove the file/folder [name]
    match = re.search(r"(delete|remove).*(file|folder|directory)\s(?:named|called)?\s*['\"]?([\w\.-]+)['\"]?", nl_command)
    if match:
        # We need to check if it's a file or folder later
        return ('delete', [match.group(3)], f"Delete '{match.group(3)}'")
        
    # Pattern: move [file1] to [folder1]
    match = re.search(r"move\s*['\"]?([\w\.-]+)['\"]?\s*to\s*['\"]?([\w\.-]+)['\"]?", nl_command)
    if match:
        return ('move', [match.group(1), match.group(2)], f"Move '{match.group(1)}' to '{match.group(2)}'")

    return (None, None, None) # No match found


# --- Backend Logic (UPGRADED) ---
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/execute', methods=['POST'])
def execute_command():
    data = request.json
    command_str = data.get('command', '')
    output, error, ai_translation = "", "", None
    is_ai_command = False

    if not command_str:
        return jsonify({'error': 'No command provided.'})

    if command_str.lower().strip().startswith('ai '):
        is_ai_command = True
        nl_query = command_str.strip()[3:] # Get text after 'ai '
        action, args, ai_translation = parse_natural_language(nl_query)
        if not action:
            error = f"AI could not understand: '{nl_query}'"
            return jsonify({'output': output, 'error': error, 'ai_translation': 'Understanding failed'})
    
    try:
        if is_ai_command:
            # --- Execute AI Action using Python's cross-platform libraries ---
            target_path = os.path.join(current_working_directory[0], args[0])
            if action == 'create_folder':
                os.makedirs(target_path, exist_ok=True)
                output = f"Folder '{args[0]}' created successfully."
            elif action == 'delete':
                if os.path.isfile(target_path):
                    os.remove(target_path)
                    output = f"File '{args[0]}' deleted successfully."
                elif os.path.isdir(target_path):
                    shutil.rmtree(target_path) # Use shutil to delete non-empty folders
                    output = f"Folder '{args[0]}' and its contents deleted successfully."
                else:
                    error = f"Error: '{args[0]}' not found."
            elif action == 'move':
                source_path = os.path.join(current_working_directory[0], args[0])
                dest_path = os.path.join(current_working_directory[0], args[1])
                shutil.move(source_path, dest_path)
                output = f"Moved '{args[0]}' to '{args[1]}' successfully."
        else:
            # --- Standard Command Execution ---
            command_parts = shlex.split(command_str)
            main_command = command_parts[0].lower()

            if main_command == 'pwd': output = os.getcwd()
            elif main_command == 'ls': output = "\n".join(os.listdir(current_working_directory[0]))
            elif main_command == 'cd':
                # (cd logic remains the same)
                if len(command_parts) > 1:
                    new_dir = os.path.expanduser(command_parts[1])
                    if not os.path.isabs(new_dir): new_dir = os.path.join(current_working_directory[0], new_dir)
                    os.chdir(new_dir)
                    current_working_directory[0] = os.getcwd()
                    output = f"Changed directory to: {current_working_directory[0]}"
            elif main_command == 'help':
                output = "Available Commands:\n ls, pwd, cd, mkdir, rm, sysinfo, clear, help, ai [query]"
            elif main_command == 'sysinfo':
                output = f"CPU: {psutil.cpu_percent(interval=1)}% | Memory: {psutil.virtual_memory().percent}%"
            else:
                # Fallback to subprocess for mkdir, etc.
                result = subprocess.run(command_str, capture_output=True, text=True, cwd=current_working_directory[0], shell=True)
                if result.stdout: output = result.stdout
                if result.stderr: error = result.stderr

    except Exception as e:
        error = f"An unexpected error occurred: {str(e)}"

    return jsonify({'output': output, 'error': error, 'ai_translation': ai_translation})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)

