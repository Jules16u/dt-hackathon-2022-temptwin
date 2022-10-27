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
        [SerializeField]
        TMP_Text Mode;

        [SerializeField]
        TMP_Text Humidity;

        [SerializeField]
        TMP_Text Temperature;

        [SerializeField]
        TMP_Text SetTemperaturePoint;

        public static string projectId = "7541be0c-7ef7-4667-b76a-5c01b5429f09";
        public static string deviceId = "AVPHwEvrbIwSsnElHCEZ1YP4sTY58NdiZCNs-4a3wUhq1K1YnlEC5kSfzrDOaAvct9rZKU9P3wwFCuy4ph-qGQjpid0MZg";
        ThermostatTraits traits = new ThermostatTraits();
        public float timer = 60f;
        public bool setHeat = false;
        public float setHeatTimer = 8f;
        public bool setMode = false;
        public float setModeTimer = 5f;

        private void Update()
        {
            if (timer > 0)
            {
                timer -= Time.deltaTime;
            }
            else
            {
                GetThermostatInfo();
                timer = 60f;
            }

            if (setHeat && setHeatTimer < 0)
            {
                var setTempUp = new RequestHelper
                {
                    Uri = GoogleUrls.Enterprise + $"/{projectId}/devices/{deviceId}:executeCommand",
                    EnableDebug = true,
                    BodyString = "{\"command\":\"sdm.devices.commands.ThermostatTemperatureSetpoint.SetHeat\",\"params\":{\"heatCelsius\":" + traits.TemperatureSetpoint + "}}"
                };
                RestClient.Post(setTempUp)
                    .Then(res => { })
                    .Catch(err => LogMessage("Error", err.Message));
                setHeatTimer = 8f;
                setHeat = false;

            }
            else setHeatTimer -= Time.deltaTime;

            if (setMode && setModeTimer < 0)
            {
                // Create a new request to set thermostat mode
                var setThermostatToHeating = new RequestHelper
                {
                    Uri = GoogleUrls.Enterprise + $"/{projectId}/devices/{deviceId}:executeCommand",
                    EnableDebug = true,
                    BodyString = "{\"command\":\"sdm.devices.commands.ThermostatMode.SetMode\",\"params\":{\"mode\":\"" + traits.ThermostatMode + "\"}}"
                };
                RestClient.Post(setThermostatToHeating)
                    .Then(res =>
                    {

                    })
                    .Catch(err => LogMessage("Error", err.Message));
                setModeTimer = 5f;
                setMode = false;
            }
            else setModeTimer -= Time.deltaTime;
        }

        private void Awake()
        {
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

        public void SetTempUp()
        {
            var newTemp = float.Parse(traits.TemperatureSetpoint) + 1;
            traits.TemperatureSetpoint = newTemp.ToString("F2");
            SetTemperaturePoint.text = traits.TemperatureSetpoint;
            setHeat = true;
        }

        public void SetTempDown()
        {
            var newTemp = float.Parse(traits.TemperatureSetpoint) - 1;
            traits.TemperatureSetpoint = newTemp.ToString("F2");
            SetTemperaturePoint.text = traits.TemperatureSetpoint;
            setHeat = true;
        }

        public void SetHeating()
        {
            traits.ThermostatMode = "HEAT";
            Mode.text = traits.ThermostatMode;
            setMode = true;
        }

        public void Off()
        {
            traits.ThermostatMode = "OFF";
            Mode.text = traits.ThermostatMode;
            setMode = true;
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
                Mode.text = traits.ThermostatMode;
                Humidity.text = traits.Humidity;
                Temperature.text = float.Parse(traits.Temperature).ToString("F2");
                if(traits.TemperatureSetpoint != null) SetTemperaturePoint.text = float.Parse(traits.TemperatureSetpoint).ToString("F2");

            }).Catch(err => LogMessage("Error", err.Message));
        }

        private void ParseTraits(string input)
        {
            traits = new ThermostatTraits();

            // Get Info
            var infoIndex = input.IndexOf("customName");
            var startIndex = input.IndexOf(':', infoIndex);
            var endIndex = input.IndexOf('}', infoIndex);
            var info = input.Substring(startIndex + 1, endIndex - startIndex).Replace(" ", "").Replace("\"", "").Replace("}", "").Replace("\r\n", "");
            traits.Info = info;

            // Get Humidity
            var humidityIndex = input.IndexOf("ambientHumidityPercent");
            startIndex = input.IndexOf(':', humidityIndex);
            endIndex = input.IndexOf('}', humidityIndex);
            var humidity = input.Substring(startIndex + 1, endIndex - startIndex).Replace(" ", "").Replace("\"", "").Replace("}", "").Replace("\r\n", "");
            traits.Humidity = humidity;

            // Get Connectivity
            var connectivitySectionIndex = input.IndexOf("sdm.devices.traits.Connectivity");
            var connectivityIndex = input.IndexOf("status", connectivitySectionIndex);
            startIndex = input.IndexOf(':', connectivityIndex);
            endIndex = input.IndexOf('}', connectivityIndex);
            var connectivity = input.Substring(startIndex + 1, endIndex - startIndex).Replace(" ", "").Replace("\"", "").Replace("}", "").Replace(",", "");
            traits.Connectivity = connectivity;

            // Get ThermostatMode
            var thermostatModeSectionIndex = input.IndexOf("sdm.devices.traits.ThermostatMode");
            var thermostatModeIndex = input.IndexOf("mode", thermostatModeSectionIndex);
            startIndex = input.IndexOf(':', thermostatModeIndex);
            endIndex = input.IndexOf(',', thermostatModeIndex);
            var thermostatMode = input.Substring(startIndex + 1, endIndex - startIndex).Replace(" ", "").Replace("\"", "").Replace("}", "").Replace(",", "");
            traits.ThermostatMode = thermostatMode;

            // Get ThermostatHvac
            var hvacSectionIndex = input.IndexOf("sdm.devices.traits.ThermostatHvac");
            var hvacIndex = input.IndexOf("status", hvacSectionIndex);
            startIndex = input.IndexOf(':', hvacIndex);
            endIndex = input.IndexOf('}', hvacIndex);
            var hvac = input.Substring(startIndex + 1, endIndex - startIndex).Replace(" ", "").Replace("\"", "").Replace("}", "").Replace(",", "");
            traits.ThermostatHvac = hvac;

            // Get ThermostatTemperatureSetpoint
            if (traits.ThermostatMode != "OFF")
            {
                var temperatureSetpointSectionIndex = input.IndexOf("sdm.devices.traits.ThermostatTemperatureSetpoint");
                var temperatureSetpointIndex = input.IndexOf("heatCelsius", temperatureSetpointSectionIndex);
                startIndex = input.IndexOf(':', temperatureSetpointIndex);
                endIndex = input.IndexOf(',', temperatureSetpointIndex);
                var temperatureSetpoint = input.Substring(startIndex + 1, endIndex - startIndex).Replace(" ", "").Replace("\"", "").Replace("}", "").Replace(",", "");
                traits.TemperatureSetpoint = temperatureSetpoint;
            }

            // Get Temperature
            var tempIndex = input.IndexOf("ambientTemperatureCelsius");
            startIndex = input.IndexOf(':', tempIndex);
            endIndex = input.IndexOf('}', tempIndex);
            var temp = input.Substring(startIndex + 1, endIndex - startIndex).Replace(" ", "").Replace("\"", "").Replace("}", "").Replace(",", "");
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
