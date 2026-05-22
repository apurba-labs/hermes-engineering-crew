"use client";

import axios from "axios";
import { useState } from "react";
import {
  Shield,
  Boxes,
  ClipboardList,
  Github,
} from "lucide-react";

export default function Home() {

  const [repoUrl, setRepoUrl] = useState("");

  const [loading, setLoading] = useState(false);

  const [report, setReport] = useState<any>(null);

  const analyzeRepository = async () => {

    if (!repoUrl) return;

    setLoading(true);

    try {

      const response = await axios.post(
        "http://127.0.0.1:8000/analyze-repo",
        {
          repo_url: repoUrl,
        }
      );

      setReport(response.data);

    } catch (error) {

      console.error(error);

    } finally {

      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-black text-white p-8">

      <div className="max-w-6xl mx-auto">

        <div className="text-center mb-12">

          <h1 className="text-5xl font-bold mb-4">
            Hermes Engineering Crew
          </h1>

          <p className="text-zinc-400 text-lg">
            Multi-agent AI engineering analysis powered by Gemma
          </p>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 mb-10">

          <div className="flex gap-4">

            <input
              type="text"
              placeholder="Enter GitHub repository URL..."
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              className="flex-1 bg-zinc-950 border border-zinc-700 rounded-xl px-4 py-3 outline-none"
            />

            <button
              onClick={analyzeRepository}
              disabled={loading}
              className="bg-white text-black px-6 py-3 rounded-xl font-semibold"
            >
              {loading ? "Analyzing..." : "Analyze"}
            </button>

          </div>
        </div>

        {loading && (

          <div className="grid md:grid-cols-3 gap-6 mb-10">

            <AgentCard
              icon={<Shield />}
              title="Security Agent"
              status="Running..."
            />

            <AgentCard
              icon={<Boxes />}
              title="Architecture Agent"
              status="Running..."
            />

            <AgentCard
              icon={<ClipboardList />}
              title="Planning Agent"
              status="Synthesizing..."
            />

          </div>
        )}

        {report && (

          <div className="grid md:grid-cols-3 gap-6">

            <ReportCard
              title="Security Report"
              content={report.security_report.summary}
            />

            <ReportCard
              title="Architecture Report"
              content={report.architecture_report.summary}
            />

            <ReportCard
              title="Planning Report"
              content={
                report.planning_report.issues[0].description
              }
            />

          </div>
        )}
      </div>
    </main>
  );
}

function AgentCard({
  icon,
  title,
  status,
}: any) {

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6">

      <div className="flex items-center gap-3 mb-4">

        <div className="text-green-400">
          {icon}
        </div>

        <h2 className="font-semibold text-lg">
          {title}
        </h2>
      </div>

      <p className="text-zinc-400 animate-pulse">
        {status}
      </p>
    </div>
  );
}

function ReportCard({
  title,
  content,
}: any) {

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6">

      <h2 className="text-xl font-semibold mb-4">
        {title}
      </h2>

      <p className="text-zinc-300 whitespace-pre-wrap text-sm leading-6">
        {content}
      </p>
    </div>
  );
}