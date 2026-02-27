from fastapi import HTTPException
class ResponseHandler: 
    @staticmethod
    def success(message , payload , status): 
        return { 
            "message": message,
            "payload": payload,
            "status" : status
        }
    @staticmethod
    def error(error , status): 
        raise HTTPException(status_code=status, detail=error)