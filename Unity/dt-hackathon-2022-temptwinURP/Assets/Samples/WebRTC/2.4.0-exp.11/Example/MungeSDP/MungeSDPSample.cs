using System.Collections;
using System.Collections.Generic;
using Unity.WebRTC;
using Unity.WebRTC.Samples;
using UnityEngine;
using UnityEngine.UI;

class MungeSDPSample : MonoBehaviour
{
#pragma warning disable 0649
    [SerializeField] private Button startButton;
    [SerializeField] private Button callButton;
    [SerializeField] private Button createOfferButton;
    [SerializeField] private Button setOfferButton;
    [SerializeField] private Button createAnswerButton;
    [SerializeField] private Button setAnswerButton;
    [SerializeField] private Button hangUpButton;
    [SerializeField] private Camera cam;
    [SerializeField] private RawImage sourceImage;
    [SerializeField] private RawImage receiveImage;
    [SerializeField] private InputField offerSdpInput;
    [SerializeField] private InputField answerSdpInput;
    [SerializeField] private Transform rotateObject;
#pragma warning restore 0649

    private RTCConfiguration configuration = new RTCConfiguration
    {
        
        iceServers = new[] {new RTCIceServer {urls = new[] { "stun:stun.l.google.com:19302" } }}
    };

    private RTCPeerConnection pcLocal, pcRemote;
    private MediaStream sourceVideoStream, receiveVideoStream;
    private Coroutine updateCoroutine;

    private void Awake()
    {
        WebRTC.Initialize(WebRTCSettings.LimitTextureSize);
    }

    private void OnDestroy()
    {
        WebRTC.Dispose();
    }

    private void Start()
    {
        startButton.onClick.AddListener(Setup);
        callButton.onClick.AddListener(Call);
        createOfferButton.onClick.AddListener(() => StartCoroutine(CreateOffer()));
        setOfferButton.onClick.AddListener(() => StartCoroutine(SetOffer()));
        createAnswerButton.onClick.AddListener(() => StartCoroutine(CreateAnswer()));
        setAnswerButton.onClick.AddListener(() => StartCoroutine(SetAnswer()));
        hangUpButton.onClick.AddListener(HangUp);


        startButton.interactable = true;
        callButton.interactable = false;
        hangUpButton.interactable = false;
    }

    private void Update()
    {
        if (rotateObject != null)
        {
            rotateObject.Rotate(1, 2, 3);
        }
    }

    private void Setup()
    {
        Debug.Log("Set up source/receive streams");

        sourceVideoStream = cam.CaptureStream(WebRTCSettings.StreamSize.x, WebRTCSettings.StreamSize.y);
        sourceImage.texture = cam.targetTexture;
        updateCoroutine = StartCoroutine(WebRTC.Update());

        receiveVideoStream = new MediaStream();
        receiveVideoStream.OnAddTrack = e =>
        {
            if (e.Track is VideoStreamTrack track)
            {
                track.OnVideoReceived += tex =>
                {
                    receiveImage.texture = tex;
                };
            }
        };

        startButton.interactable = false;
        callButton.interactable = true;
    }

    private void Call()
    {
        Debug.Log("Starting calls");

        pcLocal = new RTCPeerConnection(ref configuration);
        pcRemote = new RTCPeerConnection(ref configuration);
        pcRemote.OnTrack = e => receiveVideoStream.AddTrack(e.Track);
        pcLocal.OnIceCandidate = candidate => pcRemote.AddIceCandidate(candidate);
        pcRemote.OnIceCandidate = candidate => pcLocal.AddIceCandidate(candidate);
        Debug.Log("pc1: created local and remote peer connection object");

        var senders = new List<RTCRtpSender>();
        foreach (var track in sourceVideoStream.GetTracks())
        {
            senders.Add(pcLocal.AddTrack(track, sourceVideoStream));
        }

        if (WebRTCSettings.UseVideoCodec != null)
        {
            var codecs = new[] {WebRTCSettings.UseVideoCodec};
            foreach (var transceiver in pcLocal.GetTransceivers())
            {
                if (senders.Contains(transceiver.Sender))
                {
                    transceiver.SetCodecPreferences(codecs);
                }
            }
        }

        Debug.Log("Adding local stream to pcLocal");

        callButton.interactable = false;
        createOfferButton.interactable = true;
        createAnswerButton.interactable = true;
        setOfferButton.interactable = true;
        setAnswerButton.interactable = true;
        hangUpButton.interactable = true;
    }

    private IEnumerator CreateOffer()
    {
        var op = pcLocal.CreateOffer();
        yield return op;

        if (op.IsError)
        {
            OnCreateSessionDescriptionError(op.Error);
            yield break;
        }

        offerSdpInput.text = op.Desc.sdp;
        offerSdpInput.interactable = true;
    }

    private IEnumerator SetOffer()
    {
        var offer = new RTCSessionDescription {type = RTCSdpType.Offer, sdp = offerSdpInput.text};
        Debug.Log($"Modified Offer from LocalPeerConnection\n{offer.sdp}");

        var opLocal = pcLocal.SetLocalDescription(ref offer);
        yield return opLocal;

        if (opLocal.IsError)
        {
            OnSetSessionDescriptionError(opLocal.Error);
            yield break;
        }

        Debug.Log("Set Local session description success on LocalPeerConnection");

        var opRemote = pcRemote.SetRemoteDescription(ref offer);
        yield return opRemote;

        if (opRemote.IsError)
        {
            OnSetSessionDescriptionError(opRemote.Error);
            yield break;
        }

        Debug.Log("Set Remote session description success on RemotePeerConnection");
    }

    private IEnumerator CreateAnswer()
    {
        var op = pcRemote.CreateAnswer();
        yield return op;

        if (op.IsError)
        {
            OnCreateSessionDescriptionError(op.Error);
            yield break;
        }

        answerSdpInput.text = @"v=0\r\no=- 0 2 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\na=group:BUNDLE 0 2 1\r\na=msid-semantic: WMS 5156208097417639292/2559814816 virtual-6666\r\na=ice-lite\r\nm=audio 19305 UDP/TLS/RTP/SAVPF 111\r\nc=IN IP4 142.250.112.127\r\na=rtcp:9 IN IP4 0.0.0.0\r\na=candidate: 1 udp 2113939711 2607:f8b0:4023:1402::7f 19305 typ host generation 0\r\na=candidate: 1 tcp 2113939710 2607:f8b0:4023:1402::7f 19305 typ host tcptype passive generation 0\r\na=candidate: 1 ssltcp 2113939709 2607:f8b0:4023:1402::7f 443 typ host generation 0\r\na=candidate: 1 udp 2113932031 142.250.112.127 19305 typ host generation 0\r\na=candidate: 1 tcp 2113932030 142.250.112.127 19305 typ host tcptype passive generation 0\r\na=candidate: 1 ssltcp 2113932029 142.250.112.127 443 typ host generation 0\r\na=ice-ufrag:LNBHWNP2CN2F7QHW\r\na=ice-pwd:P18C2XRFUDSZHKLWUKBWBW7H\r\na=fingerprint:sha-256 6D:71:73:61:28:78:B1:72:F4:1E:C8:A5:32:F3:09:1C:AA:46:F3:AB:DD:DC:FC:B5:D4:E2:77:D1:35:39:8C:FE\r\na=setup:passive\r\na=mid:0\r\na=extmap:1 urn:ietf:params:rtp-hdrext:ssrc-audio-level\r\na=extmap:3 http://www.ietf.org/id/draft-holmer-rmcat-transport-wide-cc-extensions-01\r\na=sendrecv\r\na=msid:virtual-6666 virtual-6666\r\na=rtcp-mux\r\na=rtpmap:111 opus/48000/2\r\na=rtcp-fb:111 transport-cc\r\na=fmtp:111 minptime=10;useinbandfec=1\r\na=ssrc:6666 cname:6666\r\nm=video 9 UDP/TLS/RTP/SAVPF 98 99 125 107 96 97\r\nc=IN IP4 0.0.0.0\r\na=rtcp:9 IN IP4 0.0.0.0\r\na=ice-ufrag:LNBHWNP2CN2F7QHW\r\na=ice-pwd:P18C2XRFUDSZHKLWUKBWBW7H\r\na=fingerprint:sha-256 6D:71:73:61:28:78:B1:72:F4:1E:C8:A5:32:F3:09:1C:AA:46:F3:AB:DD:DC:FC:B5:D4:E2:77:D1:35:39:8C:FE\r\na=setup:passive\r\na=mid:1\r\na=extmap:2 http://www.webrtc.org/experiments/rtp-hdrext/abs-send-time\r\na=extmap:13 urn:3gpp:video-orientation\r\na=extmap:3 http://www.ietf.org/id/draft-holmer-rmcat-transport-wide-cc-extensions-01\r\na=sendrecv\r\na=msid:5156208097417639292/2559814816 5156208097417639292/2559814816\r\na=rtcp-mux\r\na=rtpmap:98 VP9/90000\r\na=rtcp-fb:98 transport-cc\r\na=rtcp-fb:98 ccm fir\r\na=rtcp-fb:98 nack\r\na=rtcp-fb:98 nack pli\r\na=rtcp-fb:98 goog-remb\r\na=fmtp:98 profile-id=0\r\na=rtpmap:99 rtx/90000\r\na=fmtp:99 apt=98\r\na=rtpmap:125 H264/90000\r\na=rtcp-fb:125 transport-cc\r\na=rtcp-fb:125 ccm fir\r\na=rtcp-fb:125 nack\r\na=rtcp-fb:125 nack pli\r\na=rtcp-fb:125 goog-remb\r\na=fmtp:125 level-asymmetry-allowed=1;packetization-mode=1;profile-level-id=42e01f\r\na=rtpmap:107 rtx/90000\r\na=fmtp:107 apt=125\r\na=rtpmap:96 VP8/90000\r\na=rtcp-fb:96 transport-cc\r\na=rtcp-fb:96 ccm fir\r\na=rtcp-fb:96 nack\r\na=rtcp-fb:96 nack pli\r\na=rtcp-fb:96 goog-remb\r\na=rtpmap:97 rtx/90000\r\na=fmtp:97 apt=96\r\na=ssrc-group:FID 2559814816 328484180\r\na=ssrc:2559814816 cname:2559814816\r\na=ssrc:328484180 cname:2559814816\r\nm=application 9 DTLS/SCTP 5000\r\nc=IN IP4 0.0.0.0\r\na=ice-ufrag:LNBHWNP2CN2F7QHW\r\na=ice-pwd:P18C2XRFUDSZHKLWUKBWBW7H\r\na=fingerprint:sha-256 6D:71:73:61:28:78:B1:72:F4:1E:C8:A5:32:F3:09:1C:AA:46:F3:AB:DD:DC:FC:B5:D4:E2:77:D1:35:39:8C:FE\r\na=setup:passive\r\na=mid:2\r\na=sctpmap:5000 webrtc-datachannel 1024\r\n";
        answerSdpInput.interactable = true;
    }

    private IEnumerator SetAnswer()
    {
        pcRemote = new RTCPeerConnection(ref configuration);
        answerSdpInput.text = @"v=0\r\no=- 0 2 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\na=group:BUNDLE 0 2 1\r\na=msid-semantic: WMS 5156208097417639292/2559814816 virtual-6666\r\na=ice-lite\r\nm=audio 19305 UDP/TLS/RTP/SAVPF 111\r\nc=IN IP4 142.250.112.127\r\na=rtcp:9 IN IP4 0.0.0.0\r\na=candidate: 1 udp 2113939711 2607:f8b0:4023:1402::7f 19305 typ host generation 0\r\na=candidate: 1 tcp 2113939710 2607:f8b0:4023:1402::7f 19305 typ host tcptype passive generation 0\r\na=candidate: 1 ssltcp 2113939709 2607:f8b0:4023:1402::7f 443 typ host generation 0\r\na=candidate: 1 udp 2113932031 142.250.112.127 19305 typ host generation 0\r\na=candidate: 1 tcp 2113932030 142.250.112.127 19305 typ host tcptype passive generation 0\r\na=candidate: 1 ssltcp 2113932029 142.250.112.127 443 typ host generation 0\r\na=ice-ufrag:LNBHWNP2CN2F7QHW\r\na=ice-pwd:P18C2XRFUDSZHKLWUKBWBW7H\r\na=fingerprint:sha-256 6D:71:73:61:28:78:B1:72:F4:1E:C8:A5:32:F3:09:1C:AA:46:F3:AB:DD:DC:FC:B5:D4:E2:77:D1:35:39:8C:FE\r\na=setup:passive\r\na=mid:0\r\na=extmap:1 urn:ietf:params:rtp-hdrext:ssrc-audio-level\r\na=extmap:3 http://www.ietf.org/id/draft-holmer-rmcat-transport-wide-cc-extensions-01\r\na=sendrecv\r\na=msid:virtual-6666 virtual-6666\r\na=rtcp-mux\r\na=rtpmap:111 opus/48000/2\r\na=rtcp-fb:111 transport-cc\r\na=fmtp:111 minptime=10;useinbandfec=1\r\na=ssrc:6666 cname:6666\r\nm=video 9 UDP/TLS/RTP/SAVPF 98 99 125 107 96 97\r\nc=IN IP4 0.0.0.0\r\na=rtcp:9 IN IP4 0.0.0.0\r\na=ice-ufrag:LNBHWNP2CN2F7QHW\r\na=ice-pwd:P18C2XRFUDSZHKLWUKBWBW7H\r\na=fingerprint:sha-256 6D:71:73:61:28:78:B1:72:F4:1E:C8:A5:32:F3:09:1C:AA:46:F3:AB:DD:DC:FC:B5:D4:E2:77:D1:35:39:8C:FE\r\na=setup:passive\r\na=mid:1\r\na=extmap:2 http://www.webrtc.org/experiments/rtp-hdrext/abs-send-time\r\na=extmap:13 urn:3gpp:video-orientation\r\na=extmap:3 http://www.ietf.org/id/draft-holmer-rmcat-transport-wide-cc-extensions-01\r\na=sendrecv\r\na=msid:5156208097417639292/2559814816 5156208097417639292/2559814816\r\na=rtcp-mux\r\na=rtpmap:98 VP9/90000\r\na=rtcp-fb:98 transport-cc\r\na=rtcp-fb:98 ccm fir\r\na=rtcp-fb:98 nack\r\na=rtcp-fb:98 nack pli\r\na=rtcp-fb:98 goog-remb\r\na=fmtp:98 profile-id=0\r\na=rtpmap:99 rtx/90000\r\na=fmtp:99 apt=98\r\na=rtpmap:125 H264/90000\r\na=rtcp-fb:125 transport-cc\r\na=rtcp-fb:125 ccm fir\r\na=rtcp-fb:125 nack\r\na=rtcp-fb:125 nack pli\r\na=rtcp-fb:125 goog-remb\r\na=fmtp:125 level-asymmetry-allowed=1;packetization-mode=1;profile-level-id=42e01f\r\na=rtpmap:107 rtx/90000\r\na=fmtp:107 apt=125\r\na=rtpmap:96 VP8/90000\r\na=rtcp-fb:96 transport-cc\r\na=rtcp-fb:96 ccm fir\r\na=rtcp-fb:96 nack\r\na=rtcp-fb:96 nack pli\r\na=rtcp-fb:96 goog-remb\r\na=rtpmap:97 rtx/90000\r\na=fmtp:97 apt=96\r\na=ssrc-group:FID 2559814816 328484180\r\na=ssrc:2559814816 cname:2559814816\r\na=ssrc:328484180 cname:2559814816\r\nm=application 9 DTLS/SCTP 5000\r\nc=IN IP4 0.0.0.0\r\na=ice-ufrag:LNBHWNP2CN2F7QHW\r\na=ice-pwd:P18C2XRFUDSZHKLWUKBWBW7H\r\na=fingerprint:sha-256 6D:71:73:61:28:78:B1:72:F4:1E:C8:A5:32:F3:09:1C:AA:46:F3:AB:DD:DC:FC:B5:D4:E2:77:D1:35:39:8C:FE\r\na=setup:passive\r\na=mid:2\r\na=sctpmap:5000 webrtc-datachannel 1024\r\n";
        var answer = new RTCSessionDescription {type = RTCSdpType.Answer, sdp = answerSdpInput.text};
        Debug.Log($"Modified Answer from RemotePeerConnection\n{answer.sdp}");

        var opLocal = pcRemote.SetLocalDescription(ref answer);
        yield return opLocal;

        if (opLocal.IsError)
        {
            OnSetSessionDescriptionError(opLocal.Error);
            yield break;
        }

        Debug.Log("Set Local session description success on RemotePeerConnection");

        var opRemote = pcLocal.SetRemoteDescription(ref answer);
        yield return opRemote;

        if (opRemote.IsError)
        {
            OnSetSessionDescriptionError(opRemote.Error);
            yield break;
        }

        Debug.Log("Set Remote session description success on LocalPeerConnection");
    }

    private void HangUp()
    {
        StopCoroutine(updateCoroutine);
        updateCoroutine = null;
        sourceVideoStream.Dispose();
        sourceVideoStream = null;
        sourceImage.texture = null;
        receiveVideoStream.Dispose();
        receiveVideoStream = null;
        receiveImage.texture = null;

        offerSdpInput.text = string.Empty;
        answerSdpInput.text = string.Empty;

        pcLocal.Close();
        pcRemote.Close();
        pcLocal.Dispose();
        pcRemote.Dispose();
        pcLocal = null;
        pcRemote = null;

        startButton.interactable = true;
        callButton.interactable = false;
        createOfferButton.interactable = false;
        createAnswerButton.interactable = false;
        setOfferButton.interactable = false;
        setAnswerButton.interactable = false;
        hangUpButton.interactable = false;
        offerSdpInput.interactable = false;
        answerSdpInput.interactable = false;
    }

    private static void OnCreateSessionDescriptionError(RTCError error)
    {
        Debug.LogError($"Failed to create session description: {error.message}");
    }

    private static void OnSetSessionDescriptionError(RTCError error)
    {
        Debug.LogError($"Failed to set session description: {error.message}");
    }
}
