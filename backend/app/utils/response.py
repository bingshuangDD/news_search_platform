from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

def success_response(message:str="success",data= None):
  content = {"code":200,"message":message,"data":data}
  #要把任何fastapi，pandatic,orm返回的数据都转换成标准文档中的格式。
  
  return JSONResponse(content=jsonable_encoder(content))