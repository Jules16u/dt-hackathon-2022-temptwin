using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;

public class TestCameraController : MonoBehaviour {
    private Vector3 Rotation;

    // Start is called before the first frame update
    void Start() {

    }

    // Update is called once per frame
    void Update() {
        Vector2 delta = Mouse.current.delta.ReadValue() * 0.5f;
        Rotation.y += delta.x;
        Rotation.x -= delta.y;
        Rotation.x = Mathf.Clamp(Rotation.x, -50f, 50f);
        transform.rotation = Quaternion.Euler(Rotation);

        float speed = Keyboard.current.shiftKey.isPressed ? 10f : 3f;

        if (Keyboard.current.wKey.isPressed)
            transform.position += transform.forward * Time.deltaTime * speed;
        if (Keyboard.current.sKey.isPressed)
            transform.position -= transform.forward * Time.deltaTime * speed;
        if (Keyboard.current.aKey.isPressed)
            transform.position -= transform.right * Time.deltaTime * speed;
        if (Keyboard.current.dKey.isPressed)
            transform.position += transform.right * Time.deltaTime * speed;
    }
}
