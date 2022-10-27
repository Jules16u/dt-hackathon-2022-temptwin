using System;
using StarterAssets;
using UnityEngine;

public class CinemachineSwitcher : MonoBehaviour
{
    [SerializeField]
    Animator m_CinemachineAnimator;
    [SerializeField]
    bool m_IsPlayerCamera = false;
    [SerializeField]
    StarterAssetsInputs m_StarterAssetsInputs;

    void Awake()
    {
        m_CinemachineAnimator.GetComponent<Animator>();
    }
    
    void SwitchCamera()
    {
        m_CinemachineAnimator.Play(m_IsPlayerCamera ? "ThermostatCamera" : "PlayerCamera");
        m_StarterAssetsInputs.cursorLocked = !m_IsPlayerCamera;
        m_StarterAssetsInputs.cursorInputForLook = !m_IsPlayerCamera;
        m_IsPlayerCamera = !m_IsPlayerCamera;
    }

    // Update is called once per frame
    void Update()
    {
        if (Input.GetKeyDown(KeyCode.C))
        {
            SwitchCamera();
        }
    }
}
