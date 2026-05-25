"use client";

import axios from "axios";
import { useState } from "react";
import {
  Shield,
  Boxes,
  ClipboardList,
  GitBranch,
} from "lucide-react";


export default function Home() {
  
  const [repoUrl, setRepoUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<any>(null);
  const [githubToken, setGithubToken] = useState("");
  const [telemetryLogs, setTelemetryLogs] = useState<string[]>([]);

  const analyzeRepository = async () => {
  if (!repoUrl) return;

  setLoading(true);
  
  // Initialize logs instantly
  setTelemetryLogs([
    "[SYSTEM] Initializing Hermes Engineering Crew...",
    "[TELEMETRY] Connecting to GitHub repository...",
  ]);

  // Set up parallel simulated steps on separate staggered interval tracks
  const simulationTimers = [
    setTimeout(() => setTelemetryLogs(prev => [...prev, "[TELEMETRY] GitHubLoader indexed repository structure."]), 800),
    setTimeout(() => setTelemetryLogs(prev => [...prev, "[TELEMETRY] Stage 1: SecurityAgent + ArchitectureAgent launched."]), 1800),
    setTimeout(() => setTelemetryLogs(prev => [...prev, "[TELEMETRY] asyncio.gather synchronization complete."]), 2800),
    setTimeout(() => setTelemetryLogs(prev => [...prev, "[TELEMETRY] PlanningAgent roadmap synthesis initialized."]), 3800),
  ];

  try {
    // Fire the API call concurrently with the running animations
    const response = await axios.post(
      `${process.env.NEXT_PUBLIC_API_URL}/analyze-repo`,
      { 
        repo_url: repoUrl, 
        github_token: githubToken, 
      }
    );

    // Clean up any remaining animation timers if the API completes incredibly fast
    simulationTimers.forEach(clearTimeout);

    // Append final real success status logs instantly alongside the data payload
    setTelemetryLogs(prev => [
      ...prev,
      "[TELEMETRY] Hermes executive synthesis layer completed.",
      "[SYSTEM] Analysis report compiled successfully."
    ]);
    setReport(response.data);

  } catch (error) {
    console.error(error);
    simulationTimers.forEach(clearTimeout);
    setTelemetryLogs(prev => [...prev, "[ERROR] Analysis pipeline halted unexpectedly."]);
  } finally {
    setLoading(false);
  }
};


  return (
    <main className="min-h-screen bg-gradient-to-b from-black via-zinc-950 to-zinc-900 text-white p-8">

      <div className="max-w-6xl mx-auto">

        <div className="text-center mb-12">

          <h1 className="text-5xl md:text-6xl font-extrabold mb-4 tracking-tight bg-gradient-to-r from-white to-zinc-500 bg-clip-text text-transparent">
            Hermes Engineering Crew
          </h1>
          <p className="text-zinc-400 text-lg">
            Hermes-inspired AI agents collaborating to analyze and improve software repositories
          </p>
          <a
            href="https://github.com/apurba-labs/gotihub-hermes-crew"
            target="_blank"
            rel="noopener noreferrer"
            className="
              inline-flex items-center gap-2
              mt-6
              bg-zinc-900 border border-zinc-800
              px-5 py-3 rounded-xl
              hover:bg-zinc-800 transition-all
            "
          >
            ⭐
            <span>
              Star the repository on GitHub
            </span>

            <GitBranch className="text-zinc-400" size={18} />
          </a>
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
            <div className="mt-4">
              <input
                type="password"
                placeholder="Optional GitHub Access Token"
                value={githubToken}
                onChange={(e) => setGithubToken(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-700 rounded-xl px-4 py-3 outline-none text-sm"
                autoComplete="off"
              />
              <p className="text-xs text-zinc-500 mt-2">
                Optional — improves GitHub API rate limits and private repository access.
              </p>
            </div>

            <button
              onClick={analyzeRepository}
              disabled={loading}
              className="bg-white hover:bg-zinc-200 hover:scale-105 transition-all duration-200 text-black px-6 py-3 rounded-xl font-semibold shadow-lg shadow-white/10"
            >
              {loading ? "Analyzing..." : "Analyze"}
            </button>

          </div>
        </div>

        {loading && (

          <div className="mb-10">

            <div className="grid md:grid-cols-3 gap-6 mb-6">

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

            <div className="bg-black border border-zinc-800 rounded-2xl p-6 max-h-[260px] overflow-y-auto">

              <div className="flex items-center justify-between mb-4">

                <h2 className="text-lg font-semibold">
                  System Telemetry
                </h2>

                <div className="h-2 w-2 rounded-full bg-green-400 animate-pulse" />

              </div>

              <div className="space-y-2 font-mono text-sm text-green-400">

                {telemetryLogs.map((log, index) => (

                  <p
                    key={index}
                    className={
                      index === telemetryLogs.length - 1
                        ? "animate-pulse"
                        : ""
                    }
                  >
                    {log}
                  </p>

                ))}

              </div>
            </div>

          </div>
        )}

        {report && (


          <div className="grid md:grid-cols-3 gap-6">
            <div className="mb-6">
              <h2 className="text-2xl font-bold">
                Engineering Analysis Report
              </h2>

              <p className="text-zinc-500 mt-1">
                Multi-agent repository analysis generated by Hermes Engineering Crew
              </p>
            </div>

            <ReportCard
              title="Security Report"
              content={report.security_report.summary}
              score={report.security_report.score}
            />

            <ReportCard
              title="Architecture Report"
              content={report.architecture_report.summary}
              score={report.architecture_report.score}
            />

            <ReportCard
              title="Planning Report"
              content={report.planning_report.issues[0].description}
              score={report.planning_report.score}
            />

          </div>
        )}
      </div>
      <footer className="mt-20 text-center text-zinc-600 text-sm">
        Hermes Engineering Crew • Local AI Orchestration with Gemma + Ollama
      </footer>
    </main>
  );
}

function AgentCard({
  icon,
  title,
  status,
}: any) {

  return (
    <div className="bg-zinc-900/80 backdrop-blur border border-zinc-800 rounded-2xl p-6 hover:border-zinc-700 transition-all duration-300">

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
  score,
}: {
  title: string;
  content: string;
  score?: number;
}) {

  return (
    <div className="bg-zinc-900/80 backdrop-blur border border-zinc-800 rounded-2xl p-6 hover:border-zinc-700 transition-all duration-300">

      <div className="inline-flex items-center px-3 py-1 rounded-full bg-zinc-800 text-xs text-zinc-300 mb-4">
        AI Confidence Score: {score ?? 90}
      </div>

      <h2 className="text-xl font-semibold mb-4">
        {title}
      </h2>

      <p className="text-zinc-300 whitespace-pre-wrap text-sm leading-6">
        {content}
      </p>
    </div>
  );
}