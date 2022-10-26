using Newtonsoft.Json;
using Proyecto26;
using System;
using System.Collections;
using TMPro;
using UnityEditor;
using UnityEngine;

namespace Assets.NestAPI.Scripts
{
    public class Thermostat : MonoBehaviour
    {
        //public string test;
        [SerializeField]
        TMP_Text Information;

        [SerializeField]
        TMP_Text Humidity;

        [SerializeField]
        TMP_Text Temperature;

        public static string projectId = "7541be0c-7ef7-4667-b76a-5c01b5429f09";
        public static string deviceId = "AVPHwEvrbIwSsnElHCEZ1YP4sTY58NdiZCNs-4a3wUhq1K1YnlEC5kSfzrDOaAvct9rZKU9P3wwFCuy4ph-qGQjpid0MZg";
        ThermostatTraits traits = new ThermostatTraits();

        private void Awake()
        {
           // TextMesh = GetComponent<TMP_Text>();
            StartCoroutine(UpdateTextWithTemperature());
        }

        public IEnumerator UpdateTextWithTemperature()
        {
            GoogleAuthManager googleAuthManager = new GoogleAuthManager();
            yield return StartCoroutine(googleAuthManager.IsRefreshed());
            GetThermostatInfo();
        }

        private void LogMessage(string title, string message)
        {
#if UNITY_EDITOR
            EditorUtility.DisplayDialog(title, message, "Ok");
#else
		Debug.Log(message);
#endif
        }

        public void SetHeating()
        {
            // Create a new request to set thermostat mode
            var setThermostatToHeating = new RequestHelper
            {
                Uri = GoogleUrls.Enterprise + $"/{projectId}/devices/{deviceId}:executeCommand",
                EnableDebug = true,
                Body = "{\"command\":\"sdm.devices.commands.ThermostatMode.SetMode\",\"params\":{\"mode\":\"HEAT\"}}"
            };
            RestClient.Post(setThermostatToHeating)
        .Then(res =>
        {
            LogMessage("Success", JsonUtility.ToJson($"Set thermostat mode to HEAT", true));
        })
        .Catch(err => LogMessage("Error", err.Message));
        }

        public void SetCooling()
        {
            // Create a new request to set thermostat mode
            var setThermostatToCooling = new RequestHelper
            {
                Uri = GoogleUrls.Enterprise + $"/{projectId}/devices/{deviceId}:executeCommand",
                EnableDebug = true,
                Body = "{\"command\":\"sdm.devices.commands.ThermostatMode.SetMode\",\"params\":{\"mode\":\"COOL\"}}"
            };
            RestClient.Post(setThermostatToCooling)
        .Then(res =>
        {
            LogMessage("Success", JsonUtility.ToJson($"Set thermostat mode to COOL", true));
        })
        .Catch(err => LogMessage("Error", err.Message));
        }

        public void Off()
        {
            // Create a new request to set thermostat mode
            var turnOffThermostat = new RequestHelper
            {
                Uri = GoogleUrls.Enterprise + $"/{projectId}/devices/{deviceId}:executeCommand",
                EnableDebug = true,
                BodyString = "{\"command\":\"sdm.devices.commands.ThermostatMode.SetMode\",\"params\":{\"mode\":\"OFF\"}}"
            };
            RestClient.Post(turnOffThermostat)
        .Then(res =>
        {
            LogMessage("Success", JsonUtility.ToJson($"Set thermostat mode to OFF", true));
        })
        .Catch(err => LogMessage("Error", err.Message));
        }

        public void GetThermostatInfo()
        {
            var getThermostatInfoRequest = new RequestHelper
            {
                Uri = GoogleUrls.Enterprise + $"/{projectId}/devices/{deviceId}",
                EnableDebug = true
            };

            RestClient.Get(getThermostatInfoRequest).Then(res => 
            {
                ParseTraits(res.Text);
                Information.text = traits.Info;
                Humidity.text = traits.Humidity;
                Temperature.text= traits.Temperature;

            }).Catch(err => LogMessage("Error", err.Message));
        }


        private void ParseTraits(string input)
        {
            traits = new ThermostatTraits();

            // Get Info
            var infoIndex = input.IndexOf("customName");
            var startIndex = input.IndexOf(':', infoIndex);
            var endIndex = input.IndexOf('}', infoIndex);
            var info = input.Substring(startIndex + 1, endIndex - startIndex).Replace(" ", "").Replace("\"", "").Replace("}", "");
            traits.Info = info;

            // Get Humidity
            var humidityIndex = input.IndexOf("ambientHumidityPercent");
            startIndex = input.IndexOf(':', humidityIndex);
            endIndex = input.IndexOf('}', humidityIndex);
            var humidity = input.Substring(startIndex + 1, endIndex - startIndex).Replace(" ", "").Replace("\"", "").Replace("}", "");
            traits.Humidity = humidity;

            // Get Connectivity
            var connectivitySectionIndex = input.IndexOf("sdm.devices.traits.Connectivity");
            var connectivityIndex = input.IndexOf("status", connectivitySectionIndex);
            startIndex = input.IndexOf(':', connectivityIndex);
            endIndex = input.IndexOf('}', connectivityIndex);
            var connectivity = input.Substring(startIndex + 1, endIndex - startIndex).Replace(" ", "").Replace("\"", "").Replace("}", "");
            traits.Connectivity = connectivity;

            // Get ThermostatMode
            var thermostatModeSectionIndex = input.IndexOf("sdm.devices.traits.ThermostatMode");
            var thermostatModeIndex = input.IndexOf("mode", thermostatModeSectionIndex);
            startIndex = input.IndexOf(':', thermostatModeIndex);
            endIndex = input.IndexOf('}', thermostatModeIndex);
            var thermostatMode = input.Substring(startIndex + 1, endIndex - startIndex).Replace(" ", "").Replace("\"", "").Replace("}", "");
            traits.Connectivity = thermostatMode;

            // Get ThermostatHvac
            var hvacSectionIndex = input.IndexOf("sdm.devices.traits.ThermostatHvac");
            var hvacIndex = input.IndexOf("status", hvacSectionIndex);
            startIndex = input.IndexOf(':', hvacIndex);
            endIndex = input.IndexOf('}', hvacIndex);
            var hvac= input.Substring(startIndex + 1, endIndex - startIndex).Replace(" ", "").Replace("\"", "").Replace("}", "");
            traits.ThermostatHvac = hvac;

            // Get Temperature
            var tempIndex = input.IndexOf("ambientTemperatureCelsius");
            startIndex = input.IndexOf(':', tempIndex);
            endIndex = input.IndexOf('}', tempIndex);
            var temp = input.Substring(startIndex + 1, endIndex - startIndex).Replace(" ", "").Replace("\"", "").Replace("}", "");
            traits.Temperature = temp;       
        }

        public class ThermostatTraits
        {
            public string Info;
            public string Humidity;
            public string Connectivity;
            public string Fan;
            public string ThermostatMode;
            public string ThermostatEco;
            public string ThermostatHvac;
            public string Settings;
            public string TemperatureSetpoint;
            public string Temperature;
        }

        [Serializable]
        public class ThermostatResponse
        {
            public string name;
            public string type;
            public string assignee;
            public ParentRelations[] parentRelations;
            public override string ToString()
            {
                return JsonUtility.ToJson(this, true);
            }

            [Serializable]
            public class ParentRelations
            {
                public string parent;
                public string displayName;
            }
        }
    }
}
