import httpx
import asyncio
import time
from datetime import datetime
from .multimodal import MultimodalOutput, FileAttachment

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
    
    async def target_agent(simulation_idx: int) -> MultimodalOutput:
        """Target agent that triggers N8N workflow via webhook"""
        result = await trigger.trigger_workflow(workflow_id, payload)
        
        if result["success"]:
            final_data = result["final_result"].get("data", {})
            execution_time = result["final_result"].get("execution_time")
            status = result["final_result"].get("status")
            
            # Handle different output types from N8N
            if isinstance(final_data, dict):
                # Extract text summary if available
                text_summary = final_data.get("summary") or final_data.get("message") or "Workflow completed successfully"
                
                # Extract files if available
                files = []
                if "files" in final_data:
                    for file_data in final_data["files"]:
                        if isinstance(file_data, dict) and "content" in file_data:
                            files.append(FileAttachment(
                                name=file_data.get("name", "file"),
                                content=file_data["content"].encode() if isinstance(file_data["content"], str) else file_data["content"],
                                mime_type=file_data.get("mime_type", "application/octet-stream"),
                                size=len(file_data["content"])
                            ))
                
                return MultimodalOutput(
                    text=text_summary,
                    json_data=final_data,
                    files=files if files else None,
                    metadata={
                        "execution_time": execution_time,
                        "status": status,
                        "workflow_id": workflow_id,
                        "simulation_idx": simulation_idx
                    }
                )
            elif isinstance(final_data, str):
                return MultimodalOutput(
                    text=final_data,
                    metadata={
                        "execution_time": execution_time,
                        "status": status,
                        "workflow_id": workflow_id
                    }
                )
            else:
                return MultimodalOutput(
                    text=str(final_data),
                    json_data={"raw_output": final_data},
                    metadata={
                        "execution_time": execution_time,
                        "status": status,
                        "workflow_id": workflow_id
                    }
                )
        else:
            return MultimodalOutput(
                text=f"Error: {result['error']}",
                metadata={
                    "error": True,
                    "workflow_id": workflow_id,
                    "simulation_idx": simulation_idx
                }
            )
    
    return target_agent
