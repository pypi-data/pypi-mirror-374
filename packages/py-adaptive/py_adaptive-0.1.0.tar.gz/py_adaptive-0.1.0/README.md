## Create a Virtual Environment

It is highly recommended to create a Python virtual environment locally to run
these scripts in Visual Studio Code. This helps isolate dependencies and avoid
conflicts with other Python projects.

### How to create a virtual environment in Visual Studio Code

1. Open the Command Palette in Visual Studio Code by pressing `Cmd+Shift+P`
   (macOS) or `Ctrl+Shift+P` (Windows/Linux).
2. Type and select `Python: Create Environment`.
3. Choose `Venv` as the environment type and select the Python interpreter you
   want to use.
4. VS Code will create the virtual environment and prompt you to select it as
   the interpreter for the workspace.
5. To install dependencies, open the Command Palette again and run:
   - `Terminal: Create New Terminal` (if you don't have one open)
   - Then run:
     ```bash
     pip install -r requirements.txt
     ```
6. Make sure the Python interpreter selected in VS Code is from the `venv`
   environment for best results.

### Recommended VS Code Extensions

- **Python (by Microsoft):** Adds rich support for the Python language,
  including features like IntelliSense, linting, debugging, and more.
- **Black Formatter (by Microsoft):** Automatically formats your Python code to
  follow best practices and PEP 8 style guide.

To install these extensions:

1. Open the Command Palette (`Cmd+Shift+P` or `Ctrl+Shift+P`).
2. Type `Extensions: Install Extensions` and press Enter.
3. Search for `Python` and install the extension by Microsoft.
4. Search for `Black Formatter` and install the extension by Microsoft.

### Testing
1. Create a ```.env``` file in the root folder
2. Add the following attributes into the file
```yaml
KEYCLOAK_REALM_NAME=sandkasse
KEYCLOAK_CLIENT_ID=
KEYCLOAK_URL=https://sso.gaiageo.dev/
KEYCLOAK_CLIENT_SECRET=
ADAPTIVE_URL=https://sandkasse.avadaptive.dev/
DATASET_ALIAS=python-test
```
3. KEYCLOAK_CLIENT_ID and KEYCLOAK_CLIENT_SECRET can be found in Bitwarden under Py-adaptive test client

