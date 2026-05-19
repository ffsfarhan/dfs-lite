import { useEffect, useState } from "react";

const API = "http://127.0.0.1:8000";

/* ---------------- BADGE ---------------- */

function Badge({ status }) {
  let style =
    "px-3 py-1 text-xs font-semibold rounded-full border";

  if (status === "HEALTHY") {
    style += " bg-green-500/20 text-green-400 border-green-500";
  } else if (status === "DEAD") {
    style += " bg-red-500/20 text-red-400 border-red-500";
  } else if (status === "DEGRADED") {
    style += " bg-yellow-400/20 text-yellow-300 border-yellow-400";
  } else if (status === "CRITICAL") {
    style += " bg-red-600/30 text-red-400 border-red-600";
  } else {
    style += " bg-gray-600/20 text-gray-300 border-gray-600";
  }

  return <span className={style}>{status}</span>;
}

/* ---------------- MAIN ---------------- */

export default function App() {
  const [files, setFiles] = useState([]);
  const [nodes, setNodes] = useState([]);
  const [cluster, setCluster] = useState(null);
  const [owner, setOwner] = useState("");
  const [file, setFile] = useState(null);

  const loadAll = async () => {
    const f = await fetch(`${API}/files`).then((r) => r.json());
    const n = await fetch(`${API}/nodes`).then((r) => r.json());
    const c = await fetch(`${API}/cluster/health`).then((r) => r.json());

    setFiles(f);
    setNodes(n);
    setCluster(c);
  };

  useEffect(() => {
    loadAll();
    const interval = setInterval(loadAll, 5000);
    return () => clearInterval(interval);
  }, []);

  const uploadFile = async () => {
    if (!file || !owner) return alert("Owner + file required");

    const form = new FormData();
    form.append("uploaded_file", file);

    await fetch(`${API}/upload?owner=${owner}`, {
      method: "POST",
      body: form,
    });

    setOwner("");
    setFile(null);
    loadAll();
  };

  const deleteFile = async (id) => {
    if (!window.confirm("Delete permanently?")) return;

    await fetch(`${API}/files/${id}`, {
      method: "DELETE",
    });

    loadAll();
  };

  const toggleNode = async (name) => {
    await fetch(`${API}/nodes/${name}/toggle`, {
      method: "POST",
    });
    loadAll();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0f172a] via-[#1e1b4b] to-[#020617] text-white">

      {/* ================= HEADER ================= */}

      <div className="py-20 text-center border-b border-gray-800">

        <h1 className="text-6xl md:text-7xl font-extrabold tracking-tight bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent drop-shadow-2xl">
          DFS Lite Control Panel
        </h1>

        <p className="text-5xl mt-6 font-extrabold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-500 bg-clip-text text-transparent">
          Distributed Storage Monitoring
        </p>

      </div>

      <div className="max-w-7xl mx-auto p-10 space-y-16">

        {/* ================= CLUSTER ================= */}

        {cluster && (
          <div className="grid md:grid-cols-3 gap-8">

            <Card>
              <p className="text-gray-400 mb-4">Cluster Status</p>
              <Badge status={cluster.cluster_status} />
            </Card>

            <Card>
              <p className="text-gray-400 mb-4">Online Nodes</p>
              <p className="text-4xl font-bold text-green-400">
                {cluster.nodes.online} / {cluster.nodes.total}
              </p>
            </Card>

            <Card>
              <p className="text-gray-400 mb-4">Total Files</p>
              <p className="text-4xl font-bold text-purple-400">
                {cluster.files.total}
              </p>
            </Card>

          </div>
        )}

        {/* ================= UPLOAD ================= */}

        <Section title="Upload File" color="text-purple-400">
          <div className="flex gap-4 flex-wrap items-center">

            <input
              value={owner}
              onChange={(e) => setOwner(e.target.value)}
              placeholder="Owner name"
              className="bg-slate-900 px-4 py-3 rounded-lg border border-gray-600 focus:border-cyan-400 outline-none transition"
            />

            <input
              type="file"
              onChange={(e) => setFile(e.target.files[0])}
            />

            <button
              onClick={uploadFile}
              className="px-6 py-2 rounded-lg font-semibold bg-gradient-to-r from-cyan-500 to-purple-500 hover:scale-105 transition"
            >
              Upload
            </button>

          </div>
        </Section>

        {/* ================= FILES ================= */}

        <Section title="Stored Files" color="text-cyan-400">
          <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-8">

            {files.map((f) => (
              <Card key={f.file_id}>

                <div className="flex justify-between items-center">
                  <p className="font-semibold truncate">
                    {f.filename}
                  </p>
                  <Badge status={f.status} />
                </div>

                <p className="text-gray-400 text-sm">
                  Owner: {f.owner}
                </p>

                <div className="flex gap-5 pt-4">

                  <button
                    onClick={() =>
                      window.open(`${API}/download/${f.file_id}`, "_blank")
                    }
                    className="px-4 py-2 rounded-lg font-semibold bg-blue-600 hover:bg-blue-500 transition"
                  >
                    Download
                  </button>

                  <button
                    onClick={() => deleteFile(f.file_id)}
                    className="px-4 py-2 rounded-lg font-semibold bg-pink-600 hover:bg-pink-500 transition"
                  >
                    Delete
                  </button>

                </div>

              </Card>
            ))}

          </div>
        </Section>

        {/* ================= NODES ================= */}

        <Section title="Storage Nodes" color="text-orange-400">
          <div className="grid md:grid-cols-3 gap-8">

            {nodes.map((node) => (
              <Card key={node.name}>

                <div className="flex justify-between items-center">
                  <p className="font-bold">{node.name}</p>
                  <Badge status={node.is_online ? "HEALTHY" : "DEAD"} />
                </div>

                {node.is_online ? (
                  <button
                    onClick={() => toggleNode(node.name)}
                    className="px-5 py-2 rounded-lg font-semibold bg-green-600 hover:bg-green-500 transition"
                  >
                    Toggle Online / Offline
                  </button>
                ) : (
                  <button
                    onClick={() => toggleNode(node.name)}
                    className="px-5 py-2 rounded-lg font-semibold bg-red-600 hover:bg-red-500 transition"
                  >
                    Toggle Online / Offline
                  </button>
                )}

              </Card>
            ))}

          </div>
        </Section>

      </div>
    </div>
  );
}

/* ---------------- CARD ---------------- */

function Card({ children }) {
  return (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-xl space-y-4">
      {children}
    </div>
  );
}

/* ---------------- SECTION ---------------- */

function Section({ title, color, children }) {
  return (
    <div>
      <h2 className={`text-3xl font-bold mb-8 ${color}`}>
        {title}
      </h2>
      {children}
    </div>
  );
}

