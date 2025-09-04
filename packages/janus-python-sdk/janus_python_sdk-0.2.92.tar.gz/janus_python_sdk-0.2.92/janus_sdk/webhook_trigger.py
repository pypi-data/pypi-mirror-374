import httpx
import asyncio
import time
from datetime import datetime

class WebhookTrigger:
    def __init__(self, n8n_base_url: str, api_key: str):
        self.base_url = n8n_base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient()
    
    async def trigger_workflow(self, workflow_id: str, payload: dict) -> dict:
        """Trigger N8N workflow via webhook and return final result"""
        
        # 1. POST to N8N webhook endpoint
        response = await self.client.post(
            f"{self.base_url}/webhook/{workflow_id}",
            json=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Webhook trigger failed: {response.status_code}",
                "response": response.text
            }
        
        # 2. Get execution ID from N8N response
        execution_id = response.json().get("executionId")
        if not execution_id:
            return {
                "success": False,
                "error": "No execution ID returned from N8N",
                "response": response.json()
            }
        
        # 3. Poll N8N until completion
        final_result = await self._wait_for_completion(execution_id)
        
        return {
            "success": True,
            "execution_id": execution_id,
            "final_result": final_result
        }
    
    async def _wait_for_completion(self, execution_id: str, timeout: int = 300) -> dict:
        """Poll N8N execution until it completes"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                status_response = await self.client.get(
                    f"{self.base_url}/executions/{execution_id}",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                
                if status_response.status_code == 200:
                    execution_data = status_response.json()
                    status = execution_data.get("status")
                    
                    if status in ["success", "error", "crashed"]:
                        return {
                            "status": status,
                            "data": execution_data.get("data"),
                            "execution_time": execution_data.get("executionTime"),
                            "finished_at": execution_data.get("finishedAt")
                        }
                
                # Wait 2 seconds before next poll
                await asyncio.sleep(2)
                
            except Exception as e:
                return {
                    "status": "error",
                    "error": f"Polling failed: {str(e)}"
                }
        
        return {
            "status": "timeout",
            "error": f"Execution timed out after {timeout} seconds"
        }
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


async def create_webhook_target_agent(n8n_base_url: str, api_key: str, workflow_id: str, payload: dict):
    """Create a target agent function for use with run_simulations"""
    trigger = WebhookTrigger(n8n_base_url, api_key)
    
    async def target_agent(simulation_idx: int) -> str:
        """Target agent that triggers N8N workflow via webhook"""
        result = await trigger.trigger_workflow(workflow_id, payload)
        
        if result["success"]:
            # Extract the final data from N8N response
            final_data = result["final_result"].get("data", {})
            return str(final_data)  # Convert to string for compatibility
        else:
            return f"Error: {result['error']}"
    
    return target_agent
