from __future__ import annotations

import io
import os
from typing import Any, Mapping, Optional, List, Dict

import requests

from .logging import get_logger


class CPZAIClient:
    """Client for accessing CPZ AI platform with user-specific credentials.
    
    All user scoping and permissions are handled automatically by the API
    based on the provided CPZ_AI_API_KEY and CPZ_AI_API_SECRET credentials.
    """
    
    def __init__(self, api_key: str, secret_key: str, url: str = "https://api-ai.cpz-lab.com/cpz") -> None:
        self.url = url.rstrip("/")
        self.api_key = api_key
        self.secret_key = secret_key
        self.logger = get_logger()

    @staticmethod
    def from_env(environ: Optional[Mapping[str, str]] = None) -> "CPZAIClient":
        env = environ or os.environ
        url = env.get("CPZ_AI_URL", "https://api-ai.cpz-lab.com/cpz")
        api_key = env.get("CPZ_AI_API_KEY", "")
        secret_key = env.get("CPZ_AI_API_SECRET", "")
        # User identity and permissions are auto-resolved from the API credentials
        return CPZAIClient(api_key=api_key, secret_key=secret_key, url=url)

    def _headers(self) -> dict[str, str]:
        return {
            "X-CPZ-Key": self.api_key,
            "X-CPZ-Secret": self.secret_key,
            "Content-Type": "application/json",
        }

    def health(self) -> bool:
        """Check if the CPZ AI Platform is accessible"""
        try:
            resp = requests.get(f"{self.url}/rest/v1/", headers=self._headers(), timeout=10)
            return resp.status_code < 500
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_platform_health_error", error=str(exc))
            return False

    def get_strategies(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get user's strategies from strategies table"""
        try:
            params = {"limit": limit, "offset": offset}
            
            # User scoping is handled by the API based on credentials
            
            resp = requests.get(
                f"{self.url}/rest/v1/strategies",
                headers=self._headers(),
                params=params,
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json()
            else:
                self.logger.error("cpz_ai_get_strategies_error", status=resp.status_code, response=resp.text)
                return []
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_get_strategies_exception", error=str(exc))
            return []

    def get_strategy(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific strategy by ID"""
        try:
            resp = requests.get(
                f"{self.url}/rest/v1/strategies",
                headers=self._headers(),
                params={"id": f"eq.{strategy_id}"},
                timeout=10
            )
            if resp.status_code == 200:
                strategies = resp.json()
                return strategies[0] if strategies else None
            else:
                self.logger.error("cpz_ai_get_strategy_error", status=resp.status_code, response=resp.text)
                return None
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_get_strategy_exception", error=str(exc))
            return None

    def create_strategy(self, strategy_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new strategy"""
        try:
            # User scoping is handled by the API based on credentials
            # No need to manually set user_id
            
            resp = requests.post(
                f"{self.url}/rest/v1/strategies",
                headers=self._headers(),
                json=strategy_data,
                timeout=10
            )
            if resp.status_code == 201:
                return resp.json()[0] if resp.json() else None
            else:
                self.logger.error("cpz_ai_create_strategy_error", status=resp.status_code, response=resp.text)
                return None
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_create_strategy_exception", error=str(exc))
            return None

    def update_strategy(self, strategy_id: str, strategy_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing strategy"""
        try:
            resp = requests.patch(
                f"{self.url}/rest/v1/strategies",
                headers=self._headers(),
                params={"id": f"eq.{strategy_id}"},
                json=strategy_data,
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json()[0] if resp.json() else None
            else:
                self.logger.error("cpz_ai_update_strategy_error", status=resp.status_code, response=resp.text)
                return None
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_update_strategy_exception", error=str(exc))
            return None

    def delete_strategy(self, strategy_id: str) -> None:
        """Delete a strategy"""
        try:
            resp = requests.delete(
                f"{self.url}/rest/v1/strategies",
                headers=self._headers(),
                params={"id": f"eq.{strategy_id}"},
                timeout=10
            )
            return resp.status_code == 200
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_delete_strategy_error", error=str(exc))
            return False

    def get_files(self, bucket_name: str = "default") -> List[Dict[str, Any]]:
        """Get files from a storage bucket"""
        try:
            # User scoping is handled by the API based on credentials
            # Use the bucket name as provided
            
            resp = requests.get(
                f"{self.url}/storage/v1/object/list/{bucket_name}",
                headers=self._headers(),
                timeout=10
            )
            if resp.status_code == 200:
                files = resp.json()
                
                # Files are automatically scoped by the API based on credentials
                
                return files
            else:
                self.logger.error("cpz_ai_get_files_error", status=resp.status_code, response=resp.text)
                return []
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_get_files_exception", error=str(exc))
            return []

    def get_file(self, bucket_name: str, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file metadata from storage"""
        try:
            resp = requests.get(
                f"{self.url}/storage/v1/object/info/{bucket_name}/{file_path}",
                headers=self._headers(),
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json()
            else:
                self.logger.error("cpz_ai_get_file_error", status=resp.status_code, response=resp.text)
                return None
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_get_file_exception", error=str(exc))
            return None

    def upload_file(self, bucket_name: str, file_path: str, file_content: bytes, content_type: str = "application/octet-stream") -> Optional[Dict[str, Any]]:
        """Upload a file to storage"""
        try:
            # User scoping is handled by the API based on credentials
            # Use bucket and file path as provided
            
            headers = self._headers()
            headers["Content-Type"] = content_type
            
            resp = requests.post(
                f"{self.url}/storage/v1/object/{bucket_name}/{file_path}",
                headers=headers,
                data=file_content,
                timeout=30
            )
            if resp.status_code == 200:
                return resp.json()
            else:
                self.logger.error("cpz_ai_upload_file_error", status=resp.status_code, response=resp.text)
                return None
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_upload_file_exception", error=str(exc))
            return None

    def upload_csv_file(self, bucket_name: str, file_path: str, csv_content: str, encoding: str = "utf-8") -> Optional[Dict[str, Any]]:
        """Upload a CSV file to storage"""
        try:
            csv_bytes = csv_content.encode(encoding)
            return self.upload_file(bucket_name, file_path, csv_bytes, "text/csv")
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_upload_csv_exception", error=str(exc))
            return None

    def upload_dataframe(self, bucket_name: str, file_path: str, df: Any, format: str = "csv", **kwargs) -> Optional[Dict[str, Any]]:
        """Upload a pandas DataFrame to storage"""
        try:
            if format.lower() == "csv":
                csv_content = df.to_csv(index=False, **kwargs)
                return self.upload_csv_file(bucket_name, file_path, csv_content)
            elif format.lower() == "json":
                json_content = df.to_json(orient="records", **kwargs)
                json_bytes = json_content.encode("utf-8")
                return self.upload_file(bucket_name, file_path, json_bytes, "application/json")
            elif format.lower() == "parquet":
                # Convert DataFrame to parquet bytes
                buffer = io.BytesIO()
                df.to_parquet(buffer, index=False, **kwargs)
                buffer.seek(0)
                return self.upload_file(bucket_name, file_path, buffer.getvalue(), "application/octet-stream")
            else:
                raise ValueError(f"Unsupported format: {format}. Use 'csv', 'json', or 'parquet'")
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_upload_dataframe_exception", error=str(exc))
            return None

    def download_file(self, bucket_name: str, file_path: str) -> Optional[bytes]:
        """Download a file from storage"""
        try:
            # User scoping is handled by the API based on credentials
            
            resp = requests.get(
                f"{self.url}/storage/v1/object/{bucket_name}/{file_path}",
                headers=self._headers(),
                timeout=30
            )
            if resp.status_code == 200:
                return resp.content
            else:
                self.logger.error("cpz_ai_download_file_error", status=resp.status_code, response=resp.text)
                return None
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_download_file_exception", error=str(exc))
            return None

    def download_csv_to_dataframe(self, bucket_name: str, file_path: str, encoding: str = "utf-8", **kwargs) -> Optional[Any]:
        """Download a CSV file and load it into a pandas DataFrame"""
        try:
            import pandas as pd
            
            file_content = self.download_file(bucket_name, file_path)
            if file_content:
                csv_content = file_content.decode(encoding)
                return pd.read_csv(io.StringIO(csv_content), **kwargs)
            return None
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_download_csv_exception", error=str(exc))
            return None

    def download_json_to_dataframe(self, bucket_name: str, file_path: str, **kwargs) -> Optional[Any]:
        """Download a JSON file and load it into a pandas DataFrame"""
        try:
            import pandas as pd
            
            file_content = self.download_file(bucket_name, file_path)
            if file_content:
                json_content = file_content.decode("utf-8")
                return pd.read_json(json_content, **kwargs)
            return None
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_download_json_exception", error=str(exc))
            return None

    def download_parquet_to_dataframe(self, bucket_name: str, file_path: str, **kwargs) -> Optional[Any]:
        """Download a Parquet file and load it into a pandas DataFrame"""
        try:
            import pandas as pd
            
            file_content = self.download_file(bucket_name, file_path)
            if file_content:
                buffer = io.BytesIO(file_content)
                return pd.read_parquet(buffer, **kwargs)
            return None
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_download_parquet_exception", error=str(exc))
            return None

    def list_files_in_bucket(self, bucket_name: str, prefix: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        """List files in a storage bucket with optional prefix filtering"""
        try:
            # User scoping is handled by the API based on credentials
            
            params = {"limit": limit}
            if prefix:
                params["prefix"] = prefix
                
            resp = requests.get(
                f"{self.url}/storage/v1/object/list/{bucket_name}",
                headers=self._headers(),
                params=params,
                timeout=10
            )
            if resp.status_code == 200:
                files = resp.json()
                
                # Files are automatically scoped by the API based on credentials
                
                return files
            else:
                self.logger.error("cpz_ai_list_files_error", status=resp.status_code, response=resp.text)
                return []
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_list_files_exception", error=str(exc))
            return []

    def create_bucket(self, bucket_name: str, public: bool = False) -> bool:
        """Create a new storage bucket"""
        try:
            # User scoping is handled by the API based on credentials
            
            bucket_data = {
                "name": bucket_name,
                "public": public
            }
            
            resp = requests.post(
                f"{self.url}/storage/v1/bucket",
                headers=self._headers(),
                json=bucket_data,
                timeout=10
            )
            return resp.status_code == 200
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_create_bucket_exception", error=str(exc))
            return False

    def delete_file(self, bucket_name: str, file_path: str) -> bool:
        """Delete a file from storage"""
        try:
            # User scoping is handled by the API based on credentials
            
            resp = requests.delete(
                f"{self.url}/storage/v1/object/{bucket_name}/{file_path}",
                headers=self._headers(),
                timeout=10
            )
            return resp.status_code == 200
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_delete_file_error", error=str(exc))
            return False

    def list_tables(self) -> list[str]:
        """List available tables in the CPZ AI Platform"""
        try:
            resp = requests.get(f"{self.url}/rest/v1/", headers=self._headers(), timeout=10)
            if resp.status_code == 200 and isinstance(resp.json(), dict):
                return sorted(resp.json().keys())
        except Exception as exc:  # noqa: BLE001
            self.logger.warning("cpz_ai_list_tables_error", error=str(exc))
        return []

    def get_trading_credentials(self, broker: str, environment: str, account_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get trading credentials for a broker/environment/account combination"""
        try:
            params = {
                "broker": f"eq.{broker}",
                "environment": f"eq.{environment}",
                "status": "eq.active"
            }
            
            # User scoping is handled by the API based on credentials
            
            if account_id:
                params["account_id"] = f"eq.{account_id}"
            
            resp = requests.get(
                f"{self.url}/rest/v1/trading_credentials",
                headers=self._headers(),
                params=params,
                timeout=10
            )
            if resp.status_code == 200:
                credentials = resp.json()
                return credentials[0] if credentials else None
            else:
                self.logger.error("cpz_ai_get_trading_credentials_error", status=resp.status_code, response=resp.text)
                return None
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_get_trading_credentials_exception", error=str(exc))
            return None

    def create_order(self, order_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new order in the orders table"""
        try:
            # User scoping is handled by the API based on credentials
            
            resp = requests.post(
                f"{self.url}/rest/v1/orders",
                headers=self._headers(),
                json=order_data,
                timeout=10
            )
            if resp.status_code == 201:
                return resp.json()[0] if resp.json() else None
            else:
                self.logger.error("cpz_ai_create_order_error", status=resp.status_code, response=resp.text)
                return None
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_create_order_exception", error=str(exc))
            return None

    def update_order(self, order_id: str, order_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing order"""
        try:
            resp = requests.patch(
                f"{self.url}/rest/v1/orders",
                headers=self._headers(),
                params={"id": f"eq.{order_id}"},
                json=order_data,
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json()[0] if resp.json() else None
            else:
                self.logger.error("cpz_ai_update_order_error", status=resp.status_code, response=resp.text)
                return None
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_update_order_exception", error=str(exc))
            return None

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get an order by ID"""
        try:
            resp = requests.get(
                f"{self.url}/rest/v1/orders",
                headers=self._headers(),
                params={"id": f"eq.{order_id}"},
                timeout=10
            )
            if resp.status_code == 200:
                orders = resp.json()
                return orders[0] if orders else None
            else:
                self.logger.error("cpz_ai_get_order_error", status=resp.status_code, response=resp.text)
                return None
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_get_order_exception", error=str(exc))
            return None

    def get_order_by_client_id(self, client_order_id: str) -> Optional[Dict[str, Any]]:
        """Get an order by client_order_id (for idempotency)"""
        try:
            resp = requests.get(
                f"{self.url}/rest/v1/orders",
                headers=self._headers(),
                params={"client_order_id": f"eq.{client_order_id}"},
                timeout=10
            )
            if resp.status_code == 200:
                orders = resp.json()
                return orders[0] if orders else None
            else:
                self.logger.error("cpz_ai_get_order_by_client_id_error", status=resp.status_code, response=resp.text)
                return None
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_get_order_by_client_id_exception", error=str(exc))
            return None

    def echo(self) -> dict[str, Any]:
        """Test connection to CPZ AI Platform"""
        try:
            resp = requests.get(f"{self.url}/rest/v1/", headers=self._headers(), timeout=10)
            return {"status": resp.status_code, "ok": resp.ok}
        except Exception as exc:  # noqa: BLE001
            return {"status": 0, "ok": False, "error": str(exc)}


# Legacy alias for backward compatibility (will be removed in future versions)
# Use CPZAIClient instead
