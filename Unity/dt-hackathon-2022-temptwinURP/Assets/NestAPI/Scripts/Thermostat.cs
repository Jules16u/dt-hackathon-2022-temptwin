using Proyecto26;
using System;
using UnityEditor;
using UnityEngine;
using static Assets.NestAPI.Scripts.Thermostat.SetThermostatModeRequest;

namespace Assets.NestAPI.Scripts
{
    public class Thermostat : MonoBehaviour
    {
        private void LogMessage(string title, string message)
        {
#if UNITY_EDITOR
            EditorUtility.DisplayDialog(title, message, "Ok");
#else
		Debug.Log(message);
#endif
        }

        public void SetMode(string projectId, string deviceId, ThermostatMode mode)
        {
            // Create a new request to set thermostat mode
            var setThermostat = new RequestHelper
            {
                Uri = GoogleUrls.Enterprise + $"/{projectId}/devices/{deviceId}:executeCommand",
                EnableDebug = true,
                Body = new SetThermostatModeRequest
                {
                    command = "sdm.devices.commands.ThermostatMode.SetMode",
                    modeParams = new Params { mode = mode.ToString() }
                }
            };
            RestClient.Post(setThermostat)
        .Then(res =>
        {
            LogMessage("Success", JsonUtility.ToJson($"Set thermostat mode to {mode.ToString()}", true));
        })
        .Catch(err =>
        // If it's token issue, refresh the token and try again
        LogMessage("Error", err.Message));
        }

        public void GetMode(string projectId, string deviceId)
        {
            // Create a new request to refresh the token
            var getThermostatMode = new RequestHelper
            {
                Uri = GoogleUrls.Enterprise + $"/{projectId}/devices/{deviceId}",
                EnableDebug = true
            };

            RestClient.Get(getThermostatMode)
                .Then(res =>
                {
                    // Set the access token on default request header
                    LogMessage("Success", JsonUtility.ToJson("Refreshed access token", true));
                })
                .Catch(err =>
                    // If it's token issue, refresh the token and try again
                    LogMessage("Error", err.Message)
                );
        }

        public enum ThermostatMode { HEAT, COOL, HEATCOOL, OFF };

        public class SetThermostatModeRequest
        {
            public string command;
            public Params modeParams;
            public override string ToString()
            {
                return JsonUtility.ToJson(this, true);
            }

            public class Params
            {
                public string mode;
            }
        }

        [Serializable]
        public class ThermostatModeResponse
        {
            public string name;
            public Traits traits;

            [Serializable]
            public class Traits
            {
                public ThermostatMode thermostatMode;
            }

            [Serializable]
            public class ThermostatMode
            {
                public string availableModes;
                public string mode;
            }
            public override string ToString()
            {
                return JsonUtility.ToJson(this, true);
            }
        }
    }
}
