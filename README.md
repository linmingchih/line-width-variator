# Line Width Variator

A tool for generating line width variations (wavy lines) in Ansys EDB files to simulate manufacturing roughness and analyze its impact on signal integrity.

## Features

*   **Offline Generation**: Preview variations in real-time without modifying the original EDB file.
*   **Interactive Visualization**: View the generated wavy lines directly in the application.
*   **Statistics Panel**: Analyze the statistical properties of the generated variations (e.g., standard deviation, mean width).
*   **Signal Net Filtering**: Automatically identifies and applies variations only to signal nets.
*   **Non-Destructive Workflow**: Original EDB files remain untouched. Changes are only applied when you use "Save As".
*   **Session Restoration**: Automatically re-opens the original EDB after saving a variation, allowing for rapid iteration.

## Prerequisites

*   **Ansys Electronics Desktop**: Installed and licensed (2024.1 or later recommended).
*   **Python**: 3.10 or later.
*   **uv**: A fast Python package installer and resolver. (The `run.bat` script will attempt to install it if missing).

## Installation & Setup

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd line-width-variator
    ```

2.  **Run the Application**:
    Simply double-click `run.bat` on Windows.
    
    Alternatively, run via terminal:
    ```bash
    run.bat
    ```

    The script will automatically:
    *   Check for `uv` and install it if necessary.
    *   Sync the Python environment and dependencies.
    *   Launch the application.

## Usage

1.  **Open EDB**:
    *   Click the **Open** button in the left sidebar.
    *   Select an existing `.aedb` folder.

2.  **Select Primitive**:
    *   Click on a trace in the main view to select it.
    *   The **Stats Panel** (bottom center) will show its current properties.

3.  **Configure Settings**:
    *   Use the **Settings Panel** (left sidebar) to adjust generation parameters:
        *   `Sigma_w (%)`: Amplitude of width variation relative to the mean width.
        *   `L_c`: Correlation length.
        *   `Model`: Statistical model (Gaussian, Exponential, Matern32, etc.).
        *   `ds_arc`: Discretization step for the arcs.
        *   `n_resample`: Number of resampling points.
        *   `w_min` / `w_max`: Minimum and maximum width constraints (%).

4.  **Generate**:
    *   Click the **Generate** button at the bottom of the Settings Panel.
    *   The view will update to show the wavy lines.
    *   The Stats Panel will update with the new statistics for the selected primitive.

5.  **Save Variation**:
    *   Click **Save As** in the left sidebar.
    *   Choose a new location/name for the `.aedb` file (e.g., `project_var1.aedb`).
    *   The application will save the variations to the new file and then automatically restore your session to the original EDB, so you can continue experimenting.

## Development

To run in development mode with hot-reloading:

1.  **Frontend**:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

2.  **Backend**:
    ```bash
    # In a separate terminal, root directory
    uv run app.py
    ```
