import requests
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger

from app.enums.project_enum import ProjectEnum

application = FastAPI()

# 挂载静态资源
application.mount("/static", StaticFiles(directory="static"), name="static")


@application.get("/", response_class=HTMLResponse)
async def root():
    return FileResponse("static/index.html")


@application.get("/api/projects")
async def get_projects():
    return ProjectEnum.get_all_projects()


@application.get("/api/tags")
async def get_tags(repo: str = Query(...)):
    if "/" not in repo:
        raise HTTPException(status_code=400, detail="格式应为 owner/repo")
    url = f"https://api.github.com/repos/{repo}/tags"
    logger.info(f"开始获取{repo}的Tag,url {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        tags = response.json()
        # 只返回前30个tag
        return tags[:30]
    except Exception as e:
        logger.error(f"获取tags失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取tags失败: {str(e)}")


@application.get("/api/branches")
async def get_branches(repo: str = Query(...)):
    if "/" not in repo:
        raise HTTPException(status_code=400, detail="格式应为 owner/repo")
    url = f"https://api.github.com/repos/{repo}/branches"
    logger.info(f"开始获取{repo}的Branches,url {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        branches = response.json()
        # 只返回前30个分支
        return branches[:30]
    except Exception as e:
        logger.error(f"获取branches失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取branches失败: {str(e)}")

# 首页
