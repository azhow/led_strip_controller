# How to Install (Developer)

## Python Backend
1. Create a python venv like this:
    ```
    python -m venv ./python_env
    ```
2. Then activate the created environment.
3. Install required python dependencies with:
    ```
    pip install -r python_deps.txt
    ```

## Electron Frontend
1. Install nodejs and npm for your system.
2. Change current directory:
    ```
    cd .\app-ui
    ```
3. Run the following command to install dependencies and start the project:
    ```
    yarn start
    ```