MOCK_PIPELINES = [
    {
        'pipeline_id': 'PL_001',
        'name': 'sales_daily_etl',
        'status': 'FAILED',
        'error': 'Connection timeout to source database',
        'last_run': '2026-02-24 02:15:00',
        'database': 'Snowflake'
    },
    {
        'pipeline_id': 'PL_002',
        'name': 'inventory_sync',
        'status': 'SUCCESS',
        'error': None,
        'last_run': '2026-02-24 02:30:00',
        'database': 'Azure SQL'
    },
    {
        'pipeline_id': 'PL_003',
        'name': 'customer_data_warehouse',
        'status': 'FAILED',
        'error': "Schema mismatch: column 'revenue' not found",
        'last_run': '2026-02-24 01:45:00',
        'database': 'Snowflake'
    },
    {
        'pipeline_id': 'PL_004',
        'name': 'marketing_attribution',
        'status': 'SUCCESS',
        'error': None,
        'last_run': '2026-02-24 02:45:00',
        'database': 'Azure SQL'
    },
    {
        'pipeline_id': 'PL_005',
        'name': 'finance_reporting_etl',
        'status': 'FAILED',
        'error': 'Insufficient permissions on S3 bucket',
        'last_run': '2026-02-24 01:30:00',
        'database': 'Snowflake'
    }
]

DEPENDENCY_MAP = {
    'sales_daily_etl': {
        'upstream_sources': ['S3 raw sales bucket', 'Salesforce CRM API'],
        'downstream_dependents': ['finance_reporting_etl', 'executive_dashboard', 'sales_forecast_model'],
        'shared_infrastructure': ['Snowflake warehouse XL', 'Azure Data Factory']
    },
    'customer_data_warehouse': {
        'upstream_sources': ['CRM database', 'support_tickets_etl', 'web_events_stream'],
        'downstream_dependents': ['marketing_attribution', 'churn_prediction_model', 'customer_360_report'],
        'shared_infrastructure': ['Snowflake warehouse XL', 'Azure Data Factory']
    },
    'finance_reporting_etl': {
        'upstream_sources': ['sales_daily_etl', 'accounts_payable_db', 'S3 finance bucket'],
        'downstream_dependents': ['board_reporting_dashboard', 'regulatory_compliance_export', 'CFO_weekly_report'],
        'shared_infrastructure': ['Snowflake warehouse XL', 'S3 finance bucket']
    }
}