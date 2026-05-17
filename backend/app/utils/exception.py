
import traceback
from fastapi import FastAPI, Request,HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from starlette import status

DEBUG_MODE=True#教学项⽬保持开启
#开发模式：返回详细错误信息
#⽣产模式：返回简化错误信息


async def http_exception_handler(request:Request,exc:HTTPException):
  """
  处理HTTPException异常
  """ 
  #HTTPException通常是业务逻辑主动抛出的，data保持None
  return JSONResponse(
    status_code=exc.status_code,
    content={
    "code":exc.status_code,
    "message":exc.detail,
    "data":None
    }
  )

async def integrity_error_handler(request:Request,exc:IntegrityError):
  """
  处理IntegrityError异常
  """
  error_msg=str(exc.orig)
  
  if "username_UNIQUE" in error_msg or  "Duplicate entry" in error_msg:
    detail="用户名已存在"
  elif "FOREIGN KEY" in error_msg:
    detail="关联外键数据不存在"
  else:
    detail="数据约束重突,请检查输入"
    
  error_data = None
  if DEBUG_MODE:  #开发模式下返回错误信息
    error_data = {
      "error_type":"IntegrityError",
      "error_detail":error_msg,
      "path":str(request.url)
    }
  return JSONResponse(
    status_code=status.HTTP_400_BAD_REQUEST,
    content={
    "code": 400,
    "message": detail,
    "data": error_data
    }
  )
  

async def sqlalchemy_error_handler(request:Request,exc:SQLAlchemyError):
  """
  处理SQLAlchemyError异常
  """
  error_msg=str(exc)
  detail="数据操作异常,请检查输入"
  error_data = None
  if DEBUG_MODE:  #开发模式下返回错误信息
    error_data = {
      "error_type":type(exc).__name__,
      "error_detail":str(exc),
      "traceback":traceback.format_exc(),
      "path":str(request.url)
    }
  return JSONResponse(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    content={
    "code": 500,
    "message": detail,
    "data": error_data
    }
  )
  
async def general_exception_handler(request:Request,exc:Exception):
  """
  处理未定义的异常
  """
  error_msg=str(exc)
  detail="服务器内部错误"
  error_data = None
  if DEBUG_MODE:  #开发模式下返回错误信息
    error_data = {
      "error_type":type(exc).__name__,
      "error_detail":str(exc),
      "traceback":traceback.format_exc(),
      "path":str(request.url)
    }
  return JSONResponse(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    content={
      "code": 500,
      "message": detail,
      "data": error_data
}
  )