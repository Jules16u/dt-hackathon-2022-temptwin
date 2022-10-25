using Models;
using Proyecto26;
using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace Assets.NestAPI.Scripts
{
    public class GoogleAuthManager : MonoBehaviour
    {
        private readonly string refreshToken = "1//0dT2eD0PdJDa6CgYIARAAGA0SNwF-L9Ir04FVsPdbZ6J9pjXfAalVMCYj8X4f8KkF_AEGiohkNU9PkJA_Io73zmNJPnGvIEhxKsg";
        private readonly string clientId = "1045536050186-d10bka0efn0btvk9v5ri4t8aoq5kbqj3.apps.googleusercontent.com";
        private readonly string clientSecret = "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";
        private float expiryTime = 0f;

        private void LogMessage(string title, string message)
        {
#if UNITY_EDITOR
            EditorUtility.DisplayDialog(title, message, "Ok");
#else
		Debug.Log(message);
#endif
        }

        public IEnumerator IsRefreshed()
        {
            RefreshAccessToken();
            yield return new WaitUntil(() => RestClient.DefaultRequestHeaders.Count > 0);
        }

        private void Update()
        {
            if (expiryTime > expiryTime / 2f)
            {
                expiryTime -= Time.deltaTime;
            }
            else
            {
                RefreshAccessToken();
            }
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
            RestClient.DefaultRequestHeaders["Authorization"] = $"Bearer {res.access_token}";
            RestClient.DefaultRequestHeaders["Content-Type"] = "application/json";
            expiryTime = res.expires_in;
        })
        .Catch(err => LogMessage("Error", err.Message));
        }
    }

    [Serializable]
    public class RefreshTokenResponse
    {
        public string access_token;

        public int expires_in;

        public string scope;

        public string token_type;

        public override string ToString()
        {
            return JsonUtility.ToJson(this, true);
        }
    }
}
