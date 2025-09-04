"""
from_pickle.py
A backwards-compatability script to migrate pickle file loading to new Postgres database.
"""

import pickle
from utils.schema import Tool
from utils.models import Base, GalaxyTool
from utils.embedding import generate_tool_documentation_embedding
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from argparse import ArgumentParser
from tqdm import tqdm
from openai import OpenAI
from typing import Dict

parser = ArgumentParser("Migrate pickle file to Postgres")
parser.add_argument("pickle_file", default="tools_dict.pkl")
parser.add_argument("--host", help="Hostname of Postgres instance", default="localhost")
parser.add_argument("--port", help="Port of Postgres instance", default="5432")
parser.add_argument(
    "--embedding-url",
    help="URL to OpenAI-compatable embedding API",
    default="http://localhost:8000/v1",
)
parser.add_argument("--api-key", help="API key for OpenAI endpoint", default="abc123")
parser.add_argument(
    "--model", help="Embedding model to utilize", default="Qwen/Qwen3-Embedding-0.6B"
)
args = parser.parse_args()

DATABASE_URL = f"postgresql://postgres:postgres@{args.host}:{args.port}/rhea"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

client = OpenAI(base_url=args.embedding_url, api_key=args.api_key)


if __name__ == "__main__":
    with open(args.pickle_file, "rb") as f:
        tools: Dict[str, Tool] = pickle.load(f)

    session = SessionLocal()

    inserted_count = 0
    updated_count = 0

    for tool_id, tool in tqdm(tools.items(), desc="Processing tools"):
        try:
            # Check if the tool already exists
            existing_tool = session.query(GalaxyTool).filter_by(id=tool_id).first()

            if existing_tool:
                # Update existing tool
                existing_tool.name = tool.name or ""  # type: ignore
                existing_tool.user_provided_name = tool.user_provided_name  # type: ignore
                existing_tool.description = tool.description  # type: ignore
                existing_tool.long_description = tool.long_description  # type: ignore
                existing_tool.documentation = tool.documentation  # type: ignore
                existing_tool.embedding = generate_tool_documentation_embedding(  # type: ignore
                    tool, client, args.model
                )
                existing_tool.definition = tool
                updated_count += 1
                tqdm.write(f"Updated tool {tool_id}")
            else:
                # Insert new tool
                galaxy_tool = GalaxyTool(
                    id=tool_id,
                    name=tool.name or "",
                    user_provided_name=tool.user_provided_name,
                    description=tool.description,
                    long_description=tool.long_description,
                    documentation=tool.documentation,
                    embedding=generate_tool_documentation_embedding(
                        tool, client, args.model
                    ),
                )
                galaxy_tool.definition = tool
                session.add(galaxy_tool)
                inserted_count += 1
                tqdm.write(f"Inserted new tool {tool_id}")

            session.commit()

        except Exception as e:
            session.rollback()
            tqdm.write(f"Failed to process tool {tool_id}: {str(e)}")

    print(
        f"Inserted {inserted_count} new tools and updated {updated_count} existing tools in the database."
    )
    session.close()
