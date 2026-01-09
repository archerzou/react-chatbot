import os
import logging
from typing import Optional, List, Dict, Any
from datetime import date
from databricks import sql
from databricks.sdk.core import Config

logger = logging.getLogger(__name__)

# Table configuration
TABLE_NAME_SEARCH = "dev_structured.analytics.measureresponses_cleaned"
TABLE_NAME_REPORT = "dev_structured.analytics.measureresponses_ai_final"

# Get warehouse ID from environment
DATABRICKS_WAREHOUSE_ID = os.environ.get("DATABRICKS_WAREHOUSE_ID")

# Lazy initialization of Databricks config to avoid import-time failures
_databricks_cfg = None


def _get_databricks_config() -> Config:
    """
    Get Databricks configuration with lazy initialization.
    The SDK automatically detects credentials from environment variables
    (DATABRICKS_HOST, DATABRICKS_CLIENT_ID, DATABRICKS_CLIENT_SECRET)
    which are injected by Databricks Apps for service principal authentication.
    """
    global _databricks_cfg
    if _databricks_cfg is None:
        _databricks_cfg = Config()
    return _databricks_cfg


def get_connection():
    """
    Get a connection to Databricks SQL Warehouse.
    Following the official Databricks Apps cookbook pattern:
    https://apps-cookbook.dev/docs/fastapi/building_endpoints/tables_read
    
    The SDK automatically handles authentication using credentials from
    environment variables injected by Databricks Apps.
    """
    if not DATABRICKS_WAREHOUSE_ID:
        raise ValueError("DATABRICKS_WAREHOUSE_ID environment variable is not set")
    
    cfg = _get_databricks_config()
    http_path = f"/sql/1.0/warehouses/{DATABRICKS_WAREHOUSE_ID}"
    return sql.connect(
        server_hostname=cfg.host,
        http_path=http_path,
        credentials_provider=lambda: cfg.authenticate,
    )


class DatabricksService:
    """Service for handling all Databricks SQL Warehouse queries"""
    
    def __init__(self):
        self.warehouse_id = DATABRICKS_WAREHOUSE_ID
        
        if not self.warehouse_id:
            logger.warning("DATABRICKS_WAREHOUSE_ID not set - using mock data for development")
    
    def _execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a SQL query and return results as list of dictionaries"""
        if not self.warehouse_id:
            logger.warning("No warehouse ID configured - returning empty results")
            return []
        
        try:
            conn = get_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    return [dict(zip(columns, row)) for row in rows]
            finally:
                conn.close()
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise
    
    def search_clients(
        self,
        client_name: Optional[str] = None,
        client_nhi: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Search client data from Databricks table with partial matching.
        At least one search parameter must be provided.
        Returns: List of client records
        """
        conditions = []
        
        if client_name and client_name.strip():
            escaped_name = client_name.strip().replace("'", "''")
            conditions.append(f"LOWER(client_name) LIKE LOWER('%{escaped_name}%')")
        
        if client_nhi and client_nhi.strip():
            escaped_nhi = client_nhi.strip().replace("'", "''")
            conditions.append(f"LOWER(client_nhi) LIKE LOWER('%{escaped_nhi}%')")
        
        if start_date:
            date_str = start_date.strftime('%Y-%m-%d')
            conditions.append(f"DATE(create_date) >= '{date_str}'")
        
        if end_date:
            date_str = end_date.strftime('%Y-%m-%d')
            conditions.append(f"DATE(create_date) <= '{date_str}'")
        
        if not conditions:
            return []
        
        where_clause = " AND ".join(conditions)
        
        query = f"""
        SELECT 
            koo_clientid,
            koo_contactid,
            client_name,
            client_nhi,
            create_date,
            response_house,
            response_impa,
            response_mmh
        FROM {TABLE_NAME_SEARCH}
        WHERE {where_clause}
        ORDER BY create_date DESC
        LIMIT 100
        """
        
        logger.info(f"Executing search query: {query}")
        
        try:
            results = self._execute_query(query)
            # Convert date objects to strings for JSON serialization
            for row in results:
                if row.get('create_date'):
                    if hasattr(row['create_date'], 'strftime'):
                        row['create_date'] = row['create_date'].strftime('%Y-%m-%d')
                    elif hasattr(row['create_date'], 'isoformat'):
                        row['create_date'] = row['create_date'].isoformat()[:10]
            return results
        except Exception as e:
            logger.error(f"Error searching clients: {str(e)}")
            raise
    
    def get_report_data(self, client_id: str) -> Optional[Dict[str, Any]]:
        """
        Load report data from Databricks table by koo_clientid.
        Returns: Report data dictionary or None if not found
        """
        escaped_client_id = client_id.replace("'", "''")
        
        query = f"""
        SELECT 
            koo_clientid,
            client_name,
            client_nhi,
            dhb,
            domicile,
            gender,
            ethnicity,
            primary_caregiver,
            well_child_level_of_need,
            housing_concerns,
            housing_risk_categories,
            is_disability_discussed,
            disability_categories,
            family_member_disability,
            mmh_concerns,
            mental_health_categories,
            family_mental_concerns,
            family_mental_health_categories,
            family_member_impact,
            house_summary,
            impa_summary,
            mmh_summary
        FROM {TABLE_NAME_REPORT}
        WHERE koo_clientid = '{escaped_client_id}'
        LIMIT 1
        """
        
        logger.info(f"Executing report query for client: {client_id}")
        
        try:
            results = self._execute_query(query)
            if results:
                return results[0]
            return None
        except Exception as e:
            logger.error(f"Error loading report data: {str(e)}")
            raise
