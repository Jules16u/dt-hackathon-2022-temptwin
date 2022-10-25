using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class LoadSceneButton : MonoBehaviour
{
    public TMP_InputField m_SceneNameInput;
    public CloudDataStreaming m_CloudDataStreaming;

    // Start is called before the first frame update
    void Start()
    {
        GetComponent<Button>().onClick.AddListener(OnClick);
    }

    void OnClick() {
        m_CloudDataStreaming.LoadScene(m_SceneNameInput.text);
    }
}
