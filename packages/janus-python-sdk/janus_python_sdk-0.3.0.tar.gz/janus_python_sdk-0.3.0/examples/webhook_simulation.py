"""
Example: Webhook Simulation with Janus SDK
"""
import asyncio
from janus_sdk import run_simulations, create_webhook_target_agent

async def main():
    # Configuration
    n8n_config = {
        "base_url": "https://your-n8n-instance.com",
        "api_key": "your_api_key_here",
        "workflow_id": "your_workflow_id"
    }
    
    # Webhook payload
    webhook_payload = {
        "case_id": "CASE-12345",
        "client_name": "Example Corp",
        "submission_type": "Document Processing",
        "priority": "High"
    }
    
    # Create target agent
    target_agent = await create_webhook_target_agent(
        n8n_config["base_url"],
        n8n_config["api_key"],
        n8n_config["workflow_id"],
        webhook_payload
    )
    
    # Run simulation
    await run_simulations(
        num_simulations=1,
        max_turns=1,  # Single webhook trigger = 1 turn
        target_agent=target_agent,
        # All existing parameters work the same
        rules_violated=["Don't suggest specific drugs"],
        identity_backstory="Professional seeking quick solutions"
    )

if __name__ == "__main__":
    asyncio.run(main())
