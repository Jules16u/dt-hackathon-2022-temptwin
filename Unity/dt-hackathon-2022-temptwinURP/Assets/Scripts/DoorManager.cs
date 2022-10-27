using System;
using UnityEngine;

public class DoorManager : MonoBehaviour
{
    void OnCollisionEnter(Collision collision)
    {
        Destroy(collision.gameObject.GetComponent<MeshCollider>());
        gameObject.SetActive(false);
        Debug.Log("DoorOpen");
    }

    void OnTriggerEnter(Collider other)
    {
        Destroy(other.gameObject.GetComponent<MeshCollider>());
        gameObject.SetActive(false);
    }
}
