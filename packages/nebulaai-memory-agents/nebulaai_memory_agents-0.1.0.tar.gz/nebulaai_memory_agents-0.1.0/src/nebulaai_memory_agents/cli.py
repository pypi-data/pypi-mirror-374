import click
import asyncio
from .sdk import MemoryAgentsSDK

@click.group()
def main():
    """CLI for NebulaAI Memory Agents"""
    pass

@main.command()
@click.argument("agent_id")
@click.argument("message")
def chat(agent_id, message):
    sdk = MemoryAgentsSDK({"apiKey": "dummy", "model": "gpt-4o-mini"})
    res = asyncio.run(sdk.chat(agent_id, message))
    click.echo(res["reply"])

@main.command()
@click.argument("agent_id")
@click.option("--add", "-a", help="Add a memory")
@click.option("--search", "-s", help="Search memories")
def memory(agent_id, add, search):
    sdk = MemoryAgentsSDK({"apiKey": "dummy", "model": "gpt-4o-mini"})
    if add:
        asyncio.run(sdk.save_memory(agent_id, add))
    elif search:
        click.echo(asyncio.run(sdk.search_memories(agent_id, search)))
    else:
        click.echo(asyncio.run(sdk.get_memories(agent_id)))

@main.command()
@click.argument("agent_id")
def agent(agent_id):
    click.echo(f"Agent info for {agent_id} (stub)")