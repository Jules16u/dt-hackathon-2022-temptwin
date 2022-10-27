using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CharacterColliderManager : MonoBehaviour
{
    [SerializeField]
    Transform m_FireOrigin;
    // Update is called once per frame
    void Update()
    {
        if (Input.GetKeyDown(KeyCode.F))
        {
            Debug.Log($"Key press");
            OnCollisionHit();
        }
    }

    void OnCollisionHit()
    {
        RaycastHit hit;
        Ray ray = new Ray(m_FireOrigin.position, m_FireOrigin.forward * 2f);

        if (Physics.Raycast(ray, out hit))
        {
            Debug.Log($"hit object{hit.transform.name}");
            Destroy(hit.transform.gameObject.GetComponent<MeshCollider>());
        }
    }
}
