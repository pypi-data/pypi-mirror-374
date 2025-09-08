"""
UI层次结构API路由
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional

router = APIRouter()

def get_ui_analyzer():
    """依赖注入：获取UI分析器"""
    from ..core import ui_analyzer
    return ui_analyzer

@router.get("/ui-hierarchy")
async def get_ui_hierarchy(
    device: str = Query(..., description="设备ID"),
    analyzer=Depends(get_ui_analyzer)
):
    """获取当前UI层次结构"""
    try:
        device_manager = analyzer.device_manager.get_device(device)
        if not device_manager:
            raise HTTPException(status_code=404, detail=f"设备 {device} 不存在")
        
        if not device_manager.is_connected:
            device_manager.connect()
        
        hierarchy = await analyzer._get_ui_hierarchy(device_manager)
        
        return {
            "success": True,
            "hierarchy": hierarchy,
            "device_id": device
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取UI层次结构失败: {str(e)}"
        )

@router.post("/ui-dump")
async def refresh_ui_hierarchy(
    device: str = Query(..., description="设备ID"),
    analyzer=Depends(get_ui_analyzer)
):
    """强制刷新UI层次结构"""
    try:
        device_manager = analyzer.device_manager.get_device(device)
        if not device_manager:
            raise HTTPException(status_code=404, detail=f"设备 {device} 不存在")
        
        if not device_manager.is_connected:
            device_manager.connect()
        
        # 强制重新获取
        hierarchy = await analyzer._get_ui_hierarchy(device_manager)
        
        return {
            "success": True,
            "hierarchy": hierarchy,
            "device_id": device,
            "refreshed": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"刷新UI层次结构失败: {str(e)}"
        )