# README.md or project documentation
## Bachelor's Degree Final Year Project
### Configuration File

1. **Create `config.txt`:**
   - Create a new file named `config.txt` in the same directory as the Python script.
   - Open `config.txt` in a text editor.

2. **Add Telegram Token and Chat ID:**
   - In `config.txt`, add your Telegram bot token and chat ID:
     ```
     # config.txt
     TELEGRAM_TOKEN=your_telegram_bot_token_here
     CHAT_ID=your_chat_id_here
     ```
     Replace `your_telegram_bot_token_here` and `your_chat_id_here` with your actual Telegram bot token and chat ID.

3. **Update Git Ignore:**
   - If you don't have a `.gitignore` file, create one in the project root.
   - Open VS Code, press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS), type "Git: Add .gitignore," and select the option.
   - Choose a template or create a custom one. Ensure it includes an entry for `config.txt`:
     ```
     # .gitignore
     config.txt
     ```

4. **Modify Code:**
   - In your Python script, replace the lines where `TOKEN` and `CHAT_ID` are set with the following code at the beginning:
     ```python
     import configparser

     # Load Telegram configurations from the config file
     config = configparser.ConfigParser()
     config.read('config.txt')

     TOKEN = config.get('TELEGRAM', 'TELEGRAM_TOKEN')
     CHAT_ID = config.get('TELEGRAM', 'CHAT_ID')
     ```
     Adjust your existing code to use `TOKEN` and `CHAT_ID` instead of hardcoding the actual values.

5. **Important:**
   - Do not commit `config.txt` to version control. It's listed in `.gitignore` to avoid accidentally sharing sensitive information.
