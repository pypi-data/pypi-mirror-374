"""
屏幕截图API路由
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class ScreenshotRequest(BaseModel):
    device_id: str
    package_filter: Optional[str] = None

class ScreenshotResponse(BaseModel):
    success: bool
    screenshot: Optional[str] = None
    hierarchy: Optional[dict] = None
    error: Optional[str] = None
    device_id: str

def get_ui_analyzer():
    """依赖注入：获取UI分析器"""
    from ..core import ui_analyzer
    return ui_analyzer

@router.post("/screenshot", response_model=ScreenshotResponse)
async def capture_screenshot(
    device: str = Query(..., description="设备ID"),
    package: Optional[str] = Query(None, description="应用包名过滤"),
    analyzer=Depends(get_ui_analyzer)
):
    """截图并获取UI层次结构"""
    try:
        print(f"[API] 截图调用: 设备ID={device}, 包名={package}")
        result = await analyzer.capture_with_hierarchy(device)
        print(f"[API] 截图结果: success={result.get('success')}")
        
        return ScreenshotResponse(
            success=result["success"],
            screenshot=result.get("screenshot"),
            hierarchy=result.get("hierarchy"),
            error=result.get("error"),
            device_id=device
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"截图失败: {str(e)}"
        )

@router.get("/screenshot/{screenshot_id}")
async def get_screenshot(screenshot_id: str):
    """获取指定ID的截图（占位符，未实现历史截图功能）"""
    raise HTTPException(
        status_code=501,
        detail="历史截图功能尚未实现"
    )