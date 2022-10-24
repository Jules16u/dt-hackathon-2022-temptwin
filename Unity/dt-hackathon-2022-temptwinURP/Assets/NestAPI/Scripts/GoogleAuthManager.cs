using Models;
using Proyecto26;
using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace Assets.NestAPI.Scripts
{
    public class GoogleAuthManager
    {
        private readonly string refreshToken = "1//0dT2eD0PdJDa6CgYIARAAGA0SNwF-L9Ir04FVsPdbZ6J9pjXfAalVMCYj8X4f8KkF_AEGiohkNU9PkJA_Io73zmNJPnGvIEhxKsg";
        private readonly string clientId = "7541be0c-7ef7-4667-b76a-5c01b5429f09";
        private readonly string clientSecret = "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";

        private void LogMessage(string title, string message)
        {
#if UNITY_EDITOR
            EditorUtility.DisplayDialog(title, message, "Ok");
#else
		Debug.Log(message);
#endif
        }

        public void RefreshAccessToken()
        {
            // Clear previously set accessToken
            RestClient.ClearDefaultParams();

            // Create a new request to refresh the token
            var refreshTokenRequest = new RequestHelper
            {
                Uri = GoogleUrls.RefreshToken,
                Params = new Dictionary<string, string> {
                    { "client_id", clientId },
                    { "client_secret", clientSecret },
                    { "refresh_token", refreshToken},
                    {"grant_type", "refresh_token" }
                },
                EnableDebug = true
            };
            RestClient.Post<RefreshTokenResponse>(refreshTokenRequest)
        .Then(res =>
        {
            // Set the access token on default request header
            LogMessage("Success", JsonUtility.ToJson("Refreshed access token", true));
            RestClient.DefaultRequestHeaders["Authorization"] = $"Bearer {res.access_token}";
            RestClient.DefaultRequestHeaders["Content-Type"] = "application/json";
        })
        .Catch(err => LogMessage("Error", err.Message));
        }
    }

    [Serializable]
    public class RefreshTokenResponse
    {
        public string access_token;

        public string expires_in;

        public string scope;

        public string token_type;

        public override string ToString()
        {
            return JsonUtility.ToJson(this, true);
        }
    }
}
