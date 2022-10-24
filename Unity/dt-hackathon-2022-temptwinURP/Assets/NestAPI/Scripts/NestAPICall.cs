using System.Collections;
using System.Collections.Generic;
using Proyecto26;
using UnityEditor;
using UnityEngine;

public class NestAPICall : MonoBehaviour
{
    string accessToken = "ya29.a0Aa4xrXNnm4zewbKOGMw63IJUl2VE-T9iD93V6WtZA1NIio1I5O0FPg2NRAnypPzazsrZ3oAXt0X6f1KhuB_5833vF6qCVtHMM2Q6lYgF3aR-edrH1XS8bI07urfxzcd4jIzy4AzLnnh0HCgwEMLz310zrL04aCgYKATASARASFQEjDvL91WOy-LiRYl_DJ87NE7E3JA0163";
    string projectId = "7541be0c-7ef7-4667-b76a-5c01b5429f09";
    string deviceID = "64166600607A40B9";
    string basePath;
    RequestHelper currentRequest;
    
    
    public void GetStructures()
    {
        basePath = $"https://smartdevicemanagement.googleapis.com/v1/enterprises/{projectId}/structures";
        // We can add default request headers for all requests
        RestClient.DefaultRequestHeaders["Authorization"] = $"Bearer {accessToken}";
        RestClient.DefaultRequestHeaders["Content-Type"] = "application/json";

        RequestHelper requestOptions = null;
        
        RestClient.Get(basePath).Then(res => {
            EditorUtility.DisplayDialog("Response", res.Text, "Ok");
            Debug.Log(res.Text);
        });
    }
}
