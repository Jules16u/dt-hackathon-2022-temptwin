using System;

namespace Assets.NestAPI.Scripts
{
    [Serializable]
    public class ErrorResponse
    {
        public Error error;
    }

    [Serializable]
    public class Error
    {
        public string code;
        public string message;
        public string status;
    }
}


//{
//"error": {
//    "code": 404,
//    "message": "Device enterprises/project-id/devices/device-id not found.",
//    "status": "NOT_FOUND"
//  }
//}