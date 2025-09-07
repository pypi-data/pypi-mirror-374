# LCW Data Platform Scaffold

A comprehensive scaffolding tool for creating standardized data engineering project structures across various cloud providers, with initial focus on Azure Data Platform services.

## Overview

This tool automatically generates a consistent directory structure for data engineering projects, incorporating best practices for organizing Azure data platform resources including Data Factory, Databricks, Synapse Analytics, and related services.

## Target Audience

- Data Engineers
- Data Architects
- DevOps Engineers
- Cloud Solutions Architects
  working with Azure Data Platform services and looking to maintain consistent project structures across multiple data products.

## Prerequisites

- Python 3.8 or higher
- pip or poetry for package management

## Installation

Using pip:

```bash
pip install lcw-data-platform-scaffold
```

Using poetry:

```bash
poetry add lcw-data-platform-scaffold
```

## Usage

### Basic Usage

The tool can be run using the CLI command:

```bash
lcw-dps --parent your-parent-directory
```

If no parent directory is specified, it defaults to 'lcw-data-platform-applications'.

### Example

```bash
lcw-dps --parent my-data-products
```

This will create the following structure for each product:

```
my-data-products/
├── PulseOps_Appointment_Rota_Management/
├── CliniMetrics_Clinical_Data_Reporting_KPIs/
├── TeamGauge_Staff_Performance_Monitoring/
├── InsightAI_AI_ML_Insights_Predictive_Analytics/
└── PatientConnect_Patient_Communication_Engagement/
```

Each product directory contains a comprehensive structure including:

- Data ingestion components (Data Factory, Databricks, Azure Functions)
- Data processing layers
- Analytics (Synapse, Power BI)
- Governance and observability
- DevOps configurations
- Tests
- Documentation

## Project Structure

Each data product is scaffolded with the following structure:

```
product-name/
├── docs/
├── data-ingestion/
│   ├── data-factory/
│   ├── databricks/
│   ├── azure-functions/
│   └── event-hub/
├── data-processing/
├── analytics/
│   ├── synapse/
│   └── power-bi/
├── governance-observability/
├── tests/
├── devops/
└── configs/
```

## Configuration

The tool comes pre-configured with standard Azure data platform components but can be customized through:

- Modifying the `PRODUCTS` dictionary in scaffold.py
- Adjusting the `BLUEPRINT` list for different directory structures

## Dependencies

- Python >= 3.8
- click >= 8.1

## Development

To contribute to this project:

```bash
# Clone the repository
git clone https://github.com/yourusername/lcw_data_platform_scaffold.git

# Install development dependencies
poetry install

# Run tests
poetry run pytest
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Author

Amitesh Bhattacharya

## Support

For issues and feature requests, please create an issue in the project repository.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
