using TMPro;
using UnityEngine;

public class timestamp : MonoBehaviour
{
    TMP_Text m_Timestamp;
    
    void Awake()
    {
        m_Timestamp = GetComponent<TMP_Text>();
    }

    // Update is called once per frame
    void Update()
    {
        m_Timestamp.text = System.DateTime.Now.ToString("MMM dd, yyyy HH:mm:ss");
    }
}
