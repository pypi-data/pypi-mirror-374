# lcw_data_platform_scaffold/scaffold.py

import os

import click

PRODUCTS = {
    "PulseOps": "Appointment_Rota_Management",
    "CliniMetrics": "Clinical_Data_Reporting_KPIs",
    "TeamGauge": "Staff_Performance_Monitoring",
    "InsightAI": "AI_ML_Insights_Predictive_Analytics",
    "PatientConnect": "Patient_Communication_Engagement"
}

BLUEPRINT = [
    "docs",
    "data-ingestion/data-factory/pipelines",
    "data-ingestion/data-factory/datasets",
    "data-ingestion/data-factory/linked-services",
    "data-ingestion/data-factory/triggers",
    "data-ingestion/databricks/notebooks",
    "data-ingestion/databricks/jobs",
    "data-ingestion/databricks/init-scripts",
    "data-ingestion/azure-functions/src",
    "data-ingestion/event-hub/event-schema.json",
    "data-ingestion/event-hub/producer-consumer-scripts",
    "data-processing/notebooks",
    "data-processing/scripts",
    "data-processing/configs",
    "analytics/synapse/dedicated-sql-scripts",
    "analytics/synapse/pipelines",
    "analytics/power-bi/reports",
    "analytics/power-bi/dashboards",
    "analytics/power-bi/pbix-files",
    "governance-observability/unity-catalog",
    "governance-observability/purview",
    "governance-observability/monitoring",
    "governance-observability/key-vault",
    "tests/unit",
    "tests/integration",
    "tests/data-quality",
    "devops/cicd-pipelines",
    "devops/github-workflows",
    "devops/arm-templates",
    "devops/scripts",
    "configs/environment",
    "configs/logging"
]

@click.command()
@click.option('--parent', default='lcw-data-platform-applications', help='Parent directory for data products')
def scaffold_projects(parent):
    os.makedirs(parent, exist_ok=True)
    for pname, description in PRODUCTS.items():
        product_folder = f"{parent}/{pname}_{description}"
        print(f"Scaffolding {product_folder} ...")
        for path in BLUEPRINT:
            dir_path = os.path.join(product_folder, path)
            # If path ends with .json, .yml, etc. make file, else folder
            if path.endswith('.json') or path.endswith('.yml') or path.endswith('.pbix') or path.endswith('.md') or path.endswith('.py') or path.endswith('.sql'):
                os.makedirs(os.path.dirname(dir_path), exist_ok=True)
                open(dir_path, 'a').close()
            else:
                os.makedirs(dir_path, exist_ok=True)
        # Populate with basic stub files for key artefacts
        open(os.path.join(product_folder, 'docs', 'README.md'), 'a').close()
        open(os.path.join(product_folder, 'devops', 'cicd-pipelines', 'azure-pipelines.yml'), 'a').close()
        open(os.path.join(product_folder, 'devops', 'github-workflows', 'deploy.yml'), 'a').close()
        open(os.path.join(product_folder, 'analytics', 'power-bi', 'pbix-files', 'example.pbix'), 'a').close()
        open(os.path.join(product_folder, 'tests', 'unit', 'unit_test.py'), 'a').close()
        open(os.path.join(product_folder, 'analytics', 'synapse', 'dedicated-sql-scripts', 'scripts.sql'), 'a').close()
        open(os.path.join(product_folder, 'data-ingestion', 'databricks', 'notebooks', 'ETL_notebook.py'), 'a').close()
    print(f"All data products scaffolded under '{parent}'.")

if __name__ == '__main__':
    scaffold_projects()
