import subprocess
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import analysis, dataflow, diff, embed, flowchart, graph, llm, repo, roles, search

app = FastAPI(title="RepoLens")
STATIC = Path(__file__).resolve().parent.parent / "static"
_cache: dict = {}


class RepoReq(BaseModel):
    url: str
    refresh: bool = False


class FileReq(BaseModel):
    url: str
    path: str


class SearchReq(BaseModel):
    url: str
    query: str


class FlowReq(BaseModel):
    url: str
    path: str
    function: str


class TraceReq(BaseModel):
    url: str
    target: str
    start: Optional[str] = None


class DiffReq(BaseModel):
    url: str
    pr_url: Optional[str] = None
    diff: Optional[str] = None
