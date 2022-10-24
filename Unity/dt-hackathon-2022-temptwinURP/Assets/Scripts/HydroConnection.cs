using System;
using System.Collections;
using System.Collections.Generic;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using UnityEngine;

public class HydroConnection : MonoBehaviour {

    private Uri u = new Uri("ws://localhost:8080");
    private ClientWebSocket cws = null;
    private ArraySegment<byte> buf = new ArraySegment<byte>(new byte[1024]);

    void Start() {
        Connect();
    }

    private void OnDestroy() {
        cws.CloseAsync(WebSocketCloseStatus.NormalClosure, string.Empty, CancellationToken.None);
    }

    async void Connect() {
        cws = new ClientWebSocket();
        try {
            await cws.ConnectAsync(u, CancellationToken.None);
            if (cws.State == WebSocketState.Open) Debug.Log("connected");
            TestMessage();
            GetNextMessage();
        }
        catch (Exception e) { Debug.Log("woe " + e.Message); }
    }

    async void TestMessage() {
        ArraySegment<byte> b = new ArraySegment<byte>(Encoding.UTF8.GetBytes("TestMessage"));
        await cws.SendAsync(b, WebSocketMessageType.Text, true, CancellationToken.None);
    }

    async void GetNextMessage() {
        WebSocketReceiveResult r = await cws.ReceiveAsync(buf, CancellationToken.None);

        if (r.MessageType == WebSocketMessageType.Close) {
            Console.WriteLine("Close loop complete");
            return;
        }

        string msg = Encoding.UTF8.GetString(buf.Array, 0, r.Count);
        Debug.Log(msg);
        /*int split_index = msg.IndexOf(':');
        if (split_index > 0) {
            string username = msg.Substring(0, split_index);
            Debug.Log(msg[split_index + 1]);
            if (msg[split_index + 1] == '!') {
                string command = msg.Substring(split_index + 1);
                Debug.Log("username: " + username + ", msg: " + command);


            }
        }*/
        GetNextMessage();
    }
}