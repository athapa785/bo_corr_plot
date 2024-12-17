# **BO Corr Plot**

**BO Corr Plot** is a graphical tool for **Bayesian Optimization** with real-time visualization. It enables the optimization of EPICS PVs using Gaussian Processes (GPs). If EPICS PVs are unavailable, the tool falls back to mock data, ensuring robust functionality for testing and experimentation.

The GUI is built using **PyQt5** and interactive plots are powered by **PyQtGraph**.

---

## **Key Features**

- **Real-Time Bayesian Optimization**: 
   - Optimize an objective function using Gaussian Process Regression (GPR).
   - Supports **EI (Expected Improvement)** and **UCB (Upper Confidence Bound)** acquisition functions.

- **EPICS Integration**: 
   - Use **EPICS PVs** for real-world input and objective values.
   - Robust fallback to **mock data** when EPICS connections are unavailable or invalid.

- **Dynamic Parameter Control**:
   - Set input PV ranges, initial values, and exploration percentages.
   - Adjust optimization parameters such as the number of iterations and acquisition function parameters (`xi` for EI or `kappa` for UCB).

- **Interactive Visualization**:
   - Real-time updates of optimization progress.
   - Plot Gaussian Process predictions, sampled points, confidence intervals, and acquisition functions.

- **User-Friendly GUI**:
   - Built with PyQt5 and styled with **QDarkStyle** for a modern look.
   - Intuitive controls for easy experimentation and optimization.

---

## **Installation**

### Prerequisites

- **Python 3.8 or higher**  
- EPICS libraries (if using EPICS PVs)

### Steps to Install

1. **Clone the repository**:
   ```bash
   git clone https://github.com/athapa785/bo_corr_plot.git
   cd bo_corr_plot

2. **Create a virtual environment:**
   ```bash
    python -m venv .venv
    source .venv/bin/activate   # On Windows: .venv\Scripts\activate

3. **Install the project:**
    ```bash
    pip install .

## Install in Editable Mode:

If you want to make changes to the code and test them in real time, install the project in editable mode:

    ```bash
    pip install -e .

This links the project directory to the Python environment, so changes to the source code are reflected immediately without needing to reinstall.

---

### Usage

1. **Start the Application:**

- Simply run the following command to start the GUI:
    ```bash
    bo-corr-plot

2. **Input Field:**

- *Input PV:* The EPICS Process Variable for the input parameter.
- *Objective PV:* The EPICS PV for the objective being optimized.
- *Fallback Mode:* If no PVs are provided, mock data will be used automatically.

3.	**Parameter Configuration:**

- Set the initial value, minimum and maximum ranges for the input.
- Adjust the ±% spinbox to control the range dynamically.
- Define the wait time (in seconds) between iterations.

4.	**Optimization Controls:**

- Specify the *number of iterations*.
- Choose an *acquisition function*:
	- EI: Expected Improvement.
	- UCB: Upper Confidence Bound.
- Adjust the *exploration parameter* (xi for EI, kappa for UCB).

5.	**Run Optimization:**

- Click the “Run Optimization” button to start the process.
- View real-time updates in the interactive plots.

6.	**Set Parameters:**
- Use buttons like *“Set Param to Best X”* and *“Set Param to Pred. Best X”* to dynamically adjust the input range.


---

### Dependencies

The project dependencies are managed in the pyproject.toml file. Key dependencies include:

- *Python 3.8+*
- *PyQt5*: For GUI development.
- *PyQtGraph:* For real-time interactive plotting.
- *NumPy: *Numerical computations.
- *scikit-learn:* Gaussian Process Regression.
- *qdarkstyle:* Modern dark theme for the GUI.
- *pyepics:* For EPICS integration (optional).


---

### Contact

For questions or suggestions, feel free to reach out at **aaditya@slac.stanford.edu** or **athapa@stanford.edu**.