using System;
using System.Collections.Generic;
using System.Linq;
using Unity.DigitalTwins.ActorFramework.Runtime;
using Unity.DigitalTwins.DataStreaming.Runtime;
using UnityEngine;
using Metadata = Unity.DigitalTwins.DataStreaming.Runtime.Metadata;

public class CollidersManagers : MonoBehaviour {
    [Header("References")]
    [SerializeField]
    ActorGraph m_ActorGraph;
    [SerializeField]
    GameObject m_Character;
    [SerializeField]
    GameObject m_HydroPrefab;
    bool m_hydroSpawned = false;
    GameObject m_hydroConn;

    float m_Distance = 5;

    Dictionary<GameObject, MeshCollider> m_MeshCollidersDictionary = new Dictionary<GameObject, MeshCollider>();

    void Awake()
    {
        if (!m_ActorGraph)
        {
            m_ActorGraph = GetComponent<ActorGraph>();
        }

        m_ActorGraph.GraphInstanceStarted += OnGraphStarted;
    }

    void OnGraphStarted(BridgeActor obj)
    {
        if (m_ActorGraph.TryGetActor(out ColliderActor actor))
        {
            actor.OnObjectCreated += OnObjectCreated;
            actor.OnObjectDestroyed += OnObjectDestroyed;
        }
    }
    
    void OnObjectDestroyed(GameObjectIdentifier obj)
    {
        m_MeshCollidersDictionary.Remove(obj.GameObject);
    }

    void OnObjectCreated(GameObjectIdentifier obj)
    {
        bool addCollider = true;
        Metadata md = obj.GameObject.GetComponent<Metadata>();
        if (md) 
        {
            /*foreach (var m in md.GetParameters()) {
                Debug.Log(m);
            }*/
            string val = null;
            if (md.TryGetValue("Materials and Finishes/Material", out val)) {
                if (val == "Glass") {
                    addCollider = false;
                }
            }
            if (md.TryGetValue("Identity Data/OmniClass Title", out val)) {
                if (val == "Doors") {
                    addCollider = false;
                }
            }
            if (md.TryGetValue("Other/Category", out val)) {
                if (val == "Doors") {
                    addCollider = false;
                }
            }
            if (!m_hydroSpawned && md.TryGetValue("Identity Data/Type Name", out val)) {
                if (val == "Main_Electrical_Panel_with_Meter_20852") {
                    Debug.Log("Found Hydro panel, spawning info panel");
                    m_hydroConn = Instantiate(m_HydroPrefab, obj.GameObject.transform);
                    m_hydroConn.transform.localPosition = new Vector3(0.0f, 1f, 0.5f); // small offset to prevent spawning in wall
                    m_hydroSpawned = true;
                }
            }
        }
        if (addCollider)
            AddColliders(obj.GameObject);
    }

    void Update()
    {
        m_hydroConn?.SetActive(Vector3.Distance(m_Character.transform.position, m_hydroConn.transform.position) < m_Distance);
    }

    void AddColliders()
    {
        var meshes = GetComponentsInChildren<MeshRenderer>(true);
        foreach (var mesh in meshes)
        {
            if (!m_MeshCollidersDictionary.ContainsKey(mesh.gameObject))
            {
                m_MeshCollidersDictionary.Add(mesh.gameObject, mesh.gameObject.AddComponent<MeshCollider>());
            }
        }
    }

    void AddColliders(GameObject go)
    {
        var meshes = go.GetComponent<MeshRenderer>();
        var goCollider = go.GetComponent<MeshCollider>();
        if (meshes != null)
        {
            if (!m_MeshCollidersDictionary.ContainsKey(go) && goCollider == null)
            {
                m_MeshCollidersDictionary.Add(go, go.AddComponent<MeshCollider>());
            }
        }
    }
}

[Actor(isBoundToMainThread: true)]
public class ColliderActor
{
    public event Action<GameObjectIdentifier> OnObjectCreated;
    public event Action<GameObjectIdentifier> OnObjectDestroyed;

    [Pipe]
    public ActorTask GameObjectCreating(GameObjectCreating data)
    {
        foreach (var gameObjectId in data.GameObjectIds.Where(gameObjectId => IsDoorOrWindow(gameObjectId.GameObjectInfo.Metadata)))
        {
            OnObjectCreated?.Invoke(gameObjectId);
        }

        return ActorTask.CompletedTask;
    }

    [Pipe]
    public ActorTask GameObjectDestroying(GameObjectDestroying data)
    {
        foreach (var gameObjectId in data.GameObjectIds)
        {
            OnObjectDestroyed?.Invoke(gameObjectId);
        }

        return ActorTask.CompletedTask;
    }

    static bool IsDoorOrWindow(Metadata metadata)
    {
        return !metadata.TryGetValue("Curtain Panels", out var value) && !metadata.TryGetValue("Doors", out var value2);
    }
}
