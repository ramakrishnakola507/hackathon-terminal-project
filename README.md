AI-Powered Web Terminal
A full-stack, browser-based command terminal developed for the CodeMate Hackathon (Sept 2025). This application provides a secure and responsive interface to execute standard shell commands, enhanced with an AI-powered natural language parser, command history, and auto-completion.

To add your own screenshot, take a picture of the running application and replace the link above.

View the Live Demo Here

https://github.com/ramakrishnakola507/hackathon-terminal-project

Features
This project successfully implements all mandatory and optional hackathon requirements, resulting in a feature-rich and robust application.

🚀 Advanced Features
AI-Powered Commands: Use natural language to perform actions. The custom-built AI parser translates queries like "ai create a folder named reports" into safe, executable commands.

Command History: Easily navigate through your previously used commands by pressing the Up and Down arrow keys.

Tab Auto-Completion: Increase your efficiency by typing the start of a command and pressing Tab to cycle through matches.

System Monitoring: Get a quick overview of system health with the sysinfo command, which displays real-time CPU and Memory usage.

⚙️ Core Functionality
Cross-Platform Compatibility: Core commands like ls, cd, pwd, mkdir, and rm are handled internally with Python, ensuring they work flawlessly on Windows, macOS, and Linux.

Secure Execution: The backend is designed to be secure, using Python's libraries for file system operations to prevent command injection vulnerabilities.

Responsive Interface: The UI is clean, modern, and fully responsive, providing a seamless experience on any device.

Robust Error Handling: The terminal provides clear and informative feedback for invalid commands or operational errors.

Tech Stack
Backend: Python, Flask

Frontend: HTML5, CSS3, Vanilla JavaScript

Libraries: psutil (for system monitoring)

Deployment: Vercel, Git

Local Setup & Installation
To run this project on your local machine, follow these steps:

Clone the repository:

git clone [https://github.com/ramakrishnakola507/hackathon-terminal-project.git](https://github.com/ramakrishnakola507/hackathon-terminal-project.git)
cd your-repository-name

Create a virtual environment (recommended):

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

Install the dependencies:

pip install -r requirements.txt

Run the application:

python index.py

Open your web browser and navigate to http://127.0.0.1:8080.

Deployment
This application is configured for seamless deployment on Vercel. The vercel.json file in the repository root defines the build configuration, and the requirements.txt file manages the Python dependencies. Any push to the main branch will automatically trigger a new deployment.
