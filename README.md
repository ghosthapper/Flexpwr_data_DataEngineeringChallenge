# FlexPower Data Engineering Project

## Overview
This project contains a set of data engineering tasks for analyzing and processing Virtual Power Plant (VPP) data, including forecasting, best-of-infeed calculations, trading analysis, invoice generation, and performance reporting.

## Quick Start
1. Set up your Python environment (Python 3.8+ recommended)
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Run all tasks:
   ```bash
   python run_all_tasks.py
   ```
4. View dashboards:
   ```bash
   python run_all_streamlit.py
   ```

## Tasks Overview

### Task 1: Forecasting
- **Purpose**: Generate power production forecasts for VPP assets
- **Files**: 
  - `Task1/Forecasting.py` - Main forecasting script
  - `Task1/simple_forecast_viz.py` - Forecast visualization dashboard
- **Output**: Asset and portfolio level forecasts in CSV format
- **Dashboard**: http://localhost:8500

### Task 2: Best-of-Infeed Analysis
- **Purpose**: Compare forecast vs. actual measurements to determine best power values
- **Files**:
  - `Task2/best_of_infeed.py` - Main analysis script
  - `Task2/task2_streamlit.py` - Analysis dashboard
- **Output**: Asset and portfolio best-of-infeed data with metrics
- **Dashboard**: http://localhost:8501

### Task 3: Trading Analysis
- **Purpose**: Analyze trading performance and calculate metrics
- **Files**:
  - `Task3/Trading.py` - Trading analysis script
  - `Task3/streamlit.py` - Trading dashboard
- **Output**: Trade performance metrics and analysis
- **Dashboard**: http://localhost:8502

### Task 5: Invoice Generator
- **Purpose**: Generate invoices based on asset performance
- **Files**:
  - `Task5/invoice_generator.py` - Invoice generation script
  - `Task5/streamlit.py` - Invoice visualization dashboard
- **Output**: Generated invoices in JSON format
- **Dashboard**: http://localhost:8503

### Task 6: Performance Reporting
- **Purpose**: Generate comprehensive performance reports
- **Files**:
  - `Task6/task6_performance_report.py` - Performance analysis script
  - `Task6/steamlit.py` - Performance dashboard
- **Output**: Detailed performance metrics and reports
- **Dashboard**: http://localhost:8504

## Project Structure
```
FlexPower/
├── DataEngineeringChallenge/          # Source Data
│   └── DataEngineeringChallenge/
│       ├── src/
│       │   ├── crm/                   # Customer data
│       │   ├── distribution_system_operator/
│       │   │   └── redispatch/        # Grid operator data
│       │   ├── exchange/
│       │   │   ├── private_trades/    # Private trade data
│       │   │   └── public_trades/     # Public market data
│       │   ├── imbalance/            # System imbalance data
│       │   └── vpp/
│       │       ├── forecasts/        # Asset forecasts
│       │       └── live_measured_infeed/  # Live measurements
│       └── README.md
├── Task1/                 # Forecasting
│   ├── Forecasting.py    # Main forecasting logic
│   ├── simple_forecast_viz.py  # Visualization dashboard
│   └── output/           # Generated forecasts
├── Task2/                 # Best-of-Infeed
│   ├── best_of_infeed.py  # Analysis script
│   ├── task2_streamlit.py # Analysis dashboard
│   └── output/           # Best-of-infeed results
├── Task3/                 # Trading
│   ├── Trading.py        # Trading analysis
│   ├── streamlit.py      # Trading dashboard
│   └── output/           # Trading metrics
├── Task5/                 # Invoice Generator
│   ├── invoice_generator.py  # Invoice generation
│   ├── streamlit.py      # Invoice dashboard
│   └── output/           # Generated invoices
├── Task6/                 # Performance Reports
│   ├── task6_performance_report.py  # Analysis script
│   ├── steamlit.py       # Performance dashboard
│   └── output/           # Reports and metrics
├── tests/                 # Unit Tests
│   ├── test_tasks.py     # Task output tests
│   ├── test_file_structure.py  # Directory tests
│   └── test_files.py     # File presence tests
├── run_all_tasks.py      # Script to run all tasks
├── run_all_streamlit.py  # Script to launch all dashboards
└── requirements.txt      # Project dependencies
```

## Source Data Overview

### VPP Data (`src/vpp/`)
- **Live Measurements** (`live_measured_infeed/`)
  - Format: JSON files
  - Content: Actual power production data
  - Fields: timestamps (ms), values (kW)
  - Time resolution: ~1-minute intervals
  - Example assets: WND-DE-001, SOL-DE-002

- **Forecasts** (`forecasts/`)
  - Format: JSON files
  - Content: Power production forecasts
  - Resolution: 15-minute intervals
  - Horizon: Day-ahead forecasts

### Market Data (`src/exchange/`)
- **Private Trades** (`private_trades/`)
  - Format: JSON files
  - Content: Bilateral trading records
  - Fields: price, volume, execution time
  - Time resolution: Per trade

- **Public Trades** (`public_trades/`)
  - Format: JSON files
  - Content: Market clearing data
  - Fields: market prices, volumes
  - Time resolution: 15-minute intervals

### Grid Data (`src/distribution_system_operator/`)
- **Redispatch** (`redispatch/`)
  - Format: JSON files
  - Content: Grid operator instructions
  - Fields: setpoints, timestamps
  - Time resolution: As needed basis

### Reference Data (`src/crm/`)
- **Asset Information**
  - Format: JSON files
  - Content: Asset master data
  - Fields: capacity, type, location
  - Update frequency: Static

### System Data (`src/imbalance/`)
- **Imbalance Information**
  - Format: JSON files
  - Content: System balance data
  - Fields: imbalance volumes, prices
  - Time resolution: 15-minute intervals

## Data Flow and Dependencies

1. **Task1 (Forecasting)**
   - Input: `src/vpp/forecasts/*.json`
   - Output: `Task1/output/asset_forecasts.csv`
   - Dependencies: None

2. **Task2 (Best-of-Infeed)**
   - Input: 
     - `Task1/output/asset_forecasts.csv`
     - `src/vpp/live_measured_infeed/*.json`
   - Output: 
     - `Task2/output/asset_best_of_infeed_20250608.csv`
     - `Task2/output/portfolio_best_of_infeed_20250608.csv`

3. **Task3 (Trading)**
   - Input:
     - `Task2/output/portfolio_best_of_infeed_20250608.csv`
     - `src/exchange/private_trades/*.json`
     - `src/exchange/public_trades/*.json`
   - Output: `Task3/output/trading_metrics.csv`

4. **Task5 (Invoice Generator)**
   - Input:
     - `Task3/output/trading_metrics.csv`
     - `src/distribution_system_operator/redispatch/*.json`
   - Output: `Task5/output/invoice_*.json`

5. **Task6 (Performance Reports)**
   - Input: All previous task outputs
   - Output:
     - `Task6/output/performance_data_20250608.csv`
     - `Task6/output/portfolio_metrics_20250608.json`

## Running Individual Tasks

### 1. Forecasting
```bash
cd Task1
python Forecasting.py
streamlit run simple_forecast_viz.py
```

### 2. Best-of-Infeed
```bash
cd Task2
python best_of_infeed.py
streamlit run task2_streamlit.py
```

### 3. Trading Analysis
```bash
cd Task3
python Trading.py
streamlit run streamlit.py
```

### 5. Invoice Generator
```bash
cd Task5
python invoice_generator.py
streamlit run streamlit.py
```

### 6. Performance Reports
```bash
cd Task6
python task6_performance_report.py
streamlit run steamlit.py
```

## Running Tests
```bash
python -m pytest tests/
```

## Dependencies
The project requires several Python packages:
- pandas
- numpy
- matplotlib
- streamlit
- pytest
- json
- datetime

See `requirements.txt` for specific versions.

## Data Flow
1. Task1 generates forecasts
2. Task2 uses Task1's forecasts to calculate best-of-infeed
3. Task3 analyzes trading based on Task2's results
4. Task5 generates invoices using data from previous tasks
5. Task6 creates comprehensive performance reports

## Common Issues & Solutions

### Dashboard Port Conflicts
If you see a port conflict error when running dashboards:
1. Stop any running Streamlit apps
2. Change the port in `run_all_streamlit.py`
3. Retry running the dashboards

### Missing Data Files
If you see "File not found" errors:
1. Ensure you've run the tasks in order
2. Check that all required input files exist
3. Run `run_all_tasks.py` to regenerate all outputs

### Python Environment Issues
If you encounter import errors:
1. Verify your Python version (3.8+ recommended)
2. Reinstall requirements: `pip install -r requirements.txt`
3. Create a new virtual environment if needed

## 🤖 AI Help
Need assistance? Use ChatGPT or Claude AI for quick solutions.

## Support
For issues and questions:
1. Check the common issues section above
2. Run the test suite to verify your setup
3. Check task-specific documentation in each folder

