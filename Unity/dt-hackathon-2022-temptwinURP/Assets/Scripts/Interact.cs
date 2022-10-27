using UnityEngine;
using UnityEngine.Events;

[RequireComponent(typeof(Collider))] //A collider is needed to receive clicks
public class Interact : MonoBehaviour
{
    public UnityEvent interactEvent;

    void OnMouseDown()
    {
        interactEvent.Invoke();
    }
}
