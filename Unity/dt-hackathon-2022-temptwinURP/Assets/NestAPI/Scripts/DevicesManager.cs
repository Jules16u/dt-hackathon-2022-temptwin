using Proyecto26;
using System;
using System.Collections;
using TMPro;
using UnityEditor;
using UnityEngine;

namespace Assets.NestAPI.Scripts
{
    public class DevicesManager : MonoBehaviour
    {
        TMP_Text TextMesh;
        public static string projectId = "7541be0c-7ef7-4667-b76a-5c01b5429f09";

        //private void Awake()
        //{
        //    TextMesh = GetComponent<TMP_Text>();
        //    StartCoroutine(UpdateText());
        //}

        public IEnumerator UpdateText()
        {
            GoogleAuthManager googleAuthManager = new GoogleAuthManager();
            yield return StartCoroutine(googleAuthManager.IsRefreshed());
            GetDevices();
        }

        private void LogMessage(string title, string message)
        {
#if UNITY_EDITOR
            EditorUtility.DisplayDialog(title, message, "Ok");
#else
		Debug.Log(message);
#endif
        }

        public void GetDevices()
        {
            // Create a new request to refresh the token
            var getDevicesRequest = new RequestHelper
            {
                Uri = GoogleUrls.Enterprise + $"/{projectId}/devices",
                EnableDebug = true
            };

            RestClient.Get<DevicesResponse>(getDevicesRequest)
                .Then(res =>
                {
                    TextMesh.text = JsonUtility.ToJson(res);
                })
                .Catch(err => 
                LogMessage("Error", err.Message));
        }
    }

    [Serializable]
    public class DevicesResponse
    {
        public Device[] devices;
    }

    [Serializable]
    public class Device
    {
        public string name;
        public string type;
        public string assignee;
        public Trait[] traits;
        public ParentRelation[] parentRelations;
    }

    [Serializable]
    public class ParentRelation
    {
        public string parent;
        public string displayName;
    }


    [Serializable]
    public class Trait
    {

    }
}
