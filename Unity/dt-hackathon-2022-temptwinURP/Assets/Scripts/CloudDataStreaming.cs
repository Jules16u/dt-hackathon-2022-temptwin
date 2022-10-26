using System.Linq;
using System.Threading.Tasks;
using Unity.DigitalTwins.DataStreaming.Runtime;
using Unity.DigitalTwins.Identity;
using Unity.DigitalTwins.Identity.Runtime;
using Unity.DigitalTwins.Storage;
using UnityEngine;
using Unity.DigitalTwins.Common;
using Unity.DigitalTwins.Common.Runtime;

[RequireComponent(typeof(DataStreamingBehaviour))]
public class CloudDataStreaming : MonoBehaviour
{
    public string DefaultScene = "TempTwinHackweek2022";

    CloudConfiguration m_CloudConfiguration;
    UnityHttpClient m_HttpClient;
    CompositeAuthenticator m_Authenticator;
    ServiceHttpClient m_Service;

    async Task Start()
    {
        // Authenticate
        m_CloudConfiguration = UnityCloudConfigurationFactory.Create();
        m_HttpClient = new UnityHttpClient();

        m_Authenticator = new CompositeAuthenticator(m_HttpClient, DigitalTwinsPlayerSettings.Instance, DigitalTwinsPlayerSettings.Instance);
        await m_Authenticator.InitializeAsync();
        if (m_Authenticator.AuthenticationState == AuthenticationState.LoggedOut)
            await m_Authenticator.LoginAsync();

        // We will get our data from this service.
        m_Service = new ServiceHttpClient(m_HttpClient, m_Authenticator, DigitalTwinsPlayerSettings.Instance);

        LoadScene(DefaultScene);
    }

    void OnDestroy()
    {
        m_Authenticator?.Dispose();
    }

    public async void LoadScene(string name) {

        // Retrieving our uploaded scene through the available Scenes.
        var sceneProvider = new SceneProvider(m_Service, m_CloudConfiguration);
        var sceneList = await sceneProvider.ListScenesAsync();
        var scene = sceneList.First(each => each.Name == name);

        var dataStreaming = gameObject.GetComponent<DataStreamingBehaviour>();
        dataStreaming.OpenScene(scene, m_Service, m_CloudConfiguration);
    }
}