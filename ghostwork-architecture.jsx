import { useState } from "react";

const agents = [
  {
    id: 0,
    name: "Command Center",
    emoji: "🎯",
    subtitle: "Agent 0 — Morning Briefing",
    tech: "Cowork + Chrome + Dashboard",
    schedule: "On-demand (when you wake up)",
    color: "#F59E0B",
    borderColor: "#D97706",
    description: "Your 15-minute morning interface. Pulls overnight activity from all agents, shows what needs approval, and lets you command the system.",
    inputs: ["Backend API briefing endpoint", "Email notifications", "Fiverr/Upwork messages via Chrome"],
    outputs: ["Approve/reject decisions", "Priority overrides", "New instructions to other agents"],
    status: "interactive"
  },
  {
    id: 1,
    name: "Lead Prospector",
    emoji: "🔍",
    subtitle: "Agent 1 — Finds Restaurants",
    tech: "FastAPI + Google Places + Groq",
    schedule: "Every night at 2 AM IST",
    color: "#3B82F6",
    borderColor: "#2563EB",
    description: "Searches target cities for restaurants with bad reviews, no social presence, or unresponded feedback. Scores and ranks leads by pain level.",
    inputs: ["Target city list", "Scoring criteria", "Google Places API"],
    outputs: ["Scored leads → database", "Pain point analysis per lead", "Free samples auto-generated"],
    status: "autonomous"
  },
  {
    id: 2,
    name: "The Closer",
    emoji: "📬",
    subtitle: "Agent 2 — Outreach & Follow-up",
    tech: "FastAPI + Resend + Groq",
    schedule: "Every morning at 8 AM IST",
    color: "#8B5CF6",
    borderColor: "#7C3AED",
    description: "Sends personalized cold emails to leads with free sample attached. Auto-follows up on Day 3 and Day 7. Flags interested responses for your approval.",
    inputs: ["Approved leads from Agent 1", "Email templates", "Groq personalization"],
    outputs: ["Sent emails logged", "Responses flagged", "Proposals drafted for approval"],
    status: "semi-autonomous"
  },
  {
    id: 3,
    name: "The Factory",
    emoji: "🏭",
    subtitle: "Agent 3 — Builds Deliverables",
    tech: "FastAPI + Groq + Templates",
    schedule: "On-demand + pre-generates samples",
    color: "#10B981",
    borderColor: "#059669",
    description: "The revenue engine. Generates review responses, social media content packs, menu rewrites. Also pre-generates free samples for outreach leads.",
    inputs: ["Client orders", "Restaurant reviews/menus", "New leads (for free samples)"],
    outputs: ["Review response packs", "30-day content calendars", "Menu rewrites", "Free samples for outreach"],
    status: "autonomous"
  },
  {
    id: 4,
    name: "The Reporter",
    emoji: "📊",
    subtitle: "Agent 4 — Analytics & Optimization",
    tech: "FastAPI + Neon + Groq insights",
    schedule: "Continuous logging, weekly report Sundays",
    color: "#EF4444",
    borderColor: "#DC2626",
    description: "Tracks funnel metrics, identifies what's working, and recommends strategic changes. You make one decision per week based on this data.",
    inputs: ["All agent logs", "Outreach metrics", "Revenue data"],
    outputs: ["Weekly strategy report", "Template performance ranking", "Revenue projections"],
    status: "autonomous"
  }
];

const infraStack = [
  { name: "FastAPI", role: "Backend engine (24/7)", icon: "⚡" },
  { name: "Neon PostgreSQL", role: "Database (Mumbai)", icon: "🗄️" },
  { name: "Render", role: "Hosting (free tier)", icon: "☁️" },
  { name: "Groq", role: "AI inference (free)", icon: "🧠" },
  { name: "Resend", role: "Email (100/day free)", icon: "✉️" },
  { name: "cron-job.org", role: "Scheduled triggers", icon: "⏰" },
  { name: "Vercel", role: "Dashboard frontend", icon: "🌐" },
  { name: "Cowork", role: "Your command UI", icon: "🖥️" },
];

const phases = [
  { num: 1, name: "Foundation", weeks: "1-2", desc: "FastAPI + DB + Deploy", done: false },
  { num: 2, name: "Factory", weeks: "2-3", desc: "Product generators", done: false },
  { num: 3, name: "Prospector", weeks: "3-4", desc: "Lead finding engine", done: false },
  { num: 4, name: "Outreach", weeks: "4-5", desc: "Auto cold email", done: false },
  { num: 5, name: "Command", weeks: "5-6", desc: "Dashboard + Cowork", done: false },
  { num: 6, name: "Analytics", weeks: "6-7", desc: "Reports + optimization", done: false },
  { num: 7, name: "Scale", weeks: "7+", desc: "Fiverr, payments, expand", done: false },
];

const statusColors = {
  autonomous: { bg: "#065F46", text: "#6EE7B7", label: "Fully Autonomous" },
  "semi-autonomous": { bg: "#5B21B6", text: "#C4B5FD", label: "Semi-Autonomous" },
  interactive: { bg: "#92400E", text: "#FCD34D", label: "You Control" },
};

export default function GhostWorkArch() {
  const [selected, setSelected] = useState(null);
  const [view, setView] = useState("agents");

  return (
    <div style={{
      minHeight: "100vh",
      background: "#0A0A0B",
      color: "#E5E5E5",
      fontFamily: "'JetBrains Mono', 'SF Mono', 'Fira Code', monospace",
      padding: "24px 16px",
    }}>
      {/* Header */}
      <div style={{ textAlign: "center", marginBottom: 32 }}>
        <div style={{
          fontSize: 11,
          letterSpacing: 6,
          color: "#6B7280",
          textTransform: "uppercase",
          marginBottom: 8,
        }}>Architecture Blueprint v1.0</div>
        <h1 style={{
          fontSize: 28,
          fontWeight: 700,
          background: "linear-gradient(135deg, #F59E0B, #EF4444, #8B5CF6)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
          margin: 0,
          letterSpacing: -0.5,
        }}>GHOSTWORK</h1>
        <div style={{ fontSize: 13, color: "#9CA3AF", marginTop: 4 }}>
          Autonomous Business OS for Restaurant AI Services
        </div>
      </div>

      {/* View Tabs */}
      <div style={{ display: "flex", gap: 8, justifyContent: "center", marginBottom: 24 }}>
        {[
          { key: "agents", label: "Agents" },
          { key: "infra", label: "Infrastructure" },
          { key: "flow", label: "Daily Flow" },
          { key: "phases", label: "Build Phases" },
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => { setView(tab.key); setSelected(null); }}
            style={{
              padding: "8px 16px",
              borderRadius: 8,
              border: "1px solid",
              borderColor: view === tab.key ? "#F59E0B" : "#2D2D30",
              background: view === tab.key ? "#F59E0B15" : "#1A1A1D",
              color: view === tab.key ? "#F59E0B" : "#9CA3AF",
              fontSize: 12,
              fontWeight: 600,
              cursor: "pointer",
              fontFamily: "inherit",
              transition: "all 0.2s",
            }}
          >{tab.label}</button>
        ))}
      </div>

      {/* Agents View */}
      {view === "agents" && (
        <div>
          {/* You Node */}
          <div style={{
            textAlign: "center",
            marginBottom: 16,
          }}>
            <div style={{
              display: "inline-block",
              background: "#1A1A1D",
              border: "2px solid #F59E0B",
              borderRadius: 12,
              padding: "12px 24px",
              boxShadow: "0 0 20px #F59E0B20",
            }}>
              <div style={{ fontSize: 20 }}>👤</div>
              <div style={{ fontSize: 13, fontWeight: 700, color: "#F59E0B" }}>YOU</div>
              <div style={{ fontSize: 10, color: "#9CA3AF" }}>15 min/day</div>
            </div>
            <div style={{ color: "#4B5563", fontSize: 18, margin: "8px 0" }}>↕</div>
          </div>

          {/* Agent Cards */}
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {agents.map(agent => {
              const isSelected = selected === agent.id;
              const status = statusColors[agent.status];
              return (
                <div
                  key={agent.id}
                  onClick={() => setSelected(isSelected ? null : agent.id)}
                  style={{
                    background: isSelected ? "#1A1A1D" : "#111113",
                    border: `1.5px solid ${isSelected ? agent.color : "#2D2D30"}`,
                    borderRadius: 12,
                    padding: 16,
                    cursor: "pointer",
                    transition: "all 0.25s ease",
                    boxShadow: isSelected ? `0 0 24px ${agent.color}15` : "none",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                    <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
                      <div style={{
                        width: 40, height: 40,
                        borderRadius: 10,
                        background: `${agent.color}15`,
                        border: `1px solid ${agent.color}40`,
                        display: "flex", alignItems: "center", justifyContent: "center",
                        fontSize: 20,
                      }}>{agent.emoji}</div>
                      <div>
                        <div style={{ fontSize: 14, fontWeight: 700, color: agent.color }}>{agent.name}</div>
                        <div style={{ fontSize: 11, color: "#6B7280" }}>{agent.subtitle}</div>
                      </div>
                    </div>
                    <span style={{
                      fontSize: 9,
                      padding: "3px 8px",
                      borderRadius: 20,
                      background: status.bg,
                      color: status.text,
                      fontWeight: 600,
                      letterSpacing: 0.3,
                    }}>{status.label}</span>
                  </div>

                  {isSelected && (
                    <div style={{ marginTop: 16, paddingTop: 16, borderTop: "1px solid #2D2D30" }}>
                      <div style={{ fontSize: 12, color: "#D1D5DB", lineHeight: 1.6, marginBottom: 12 }}>
                        {agent.description}
                      </div>

                      <div style={{ display: "flex", gap: 8, marginBottom: 10, flexWrap: "wrap" }}>
                        <span style={{ fontSize: 10, color: "#9CA3AF", background: "#1F1F23", padding: "3px 8px", borderRadius: 6 }}>
                          🔧 {agent.tech}
                        </span>
                        <span style={{ fontSize: 10, color: "#9CA3AF", background: "#1F1F23", padding: "3px 8px", borderRadius: 6 }}>
                          ⏰ {agent.schedule}
                        </span>
                      </div>

                      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                        <div>
                          <div style={{ fontSize: 10, fontWeight: 700, color: "#6B7280", marginBottom: 6, letterSpacing: 1 }}>INPUTS</div>
                          {agent.inputs.map((inp, i) => (
                            <div key={i} style={{ fontSize: 11, color: "#9CA3AF", marginBottom: 3 }}>
                              <span style={{ color: "#3B82F6" }}>→</span> {inp}
                            </div>
                          ))}
                        </div>
                        <div>
                          <div style={{ fontSize: 10, fontWeight: 700, color: "#6B7280", marginBottom: 6, letterSpacing: 1 }}>OUTPUTS</div>
                          {agent.outputs.map((out, i) => (
                            <div key={i} style={{ fontSize: 11, color: "#9CA3AF", marginBottom: 3 }}>
                              <span style={{ color: "#10B981" }}>←</span> {out}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Infrastructure View */}
      {view === "infra" && (
        <div>
          <div style={{
            background: "#111113",
            border: "1px solid #2D2D30",
            borderRadius: 12,
            padding: 16,
            marginBottom: 16,
          }}>
            <div style={{ fontSize: 12, fontWeight: 700, color: "#F59E0B", marginBottom: 4 }}>TOTAL MONTHLY COST</div>
            <div style={{ fontSize: 32, fontWeight: 700, color: "#10B981" }}>₹0</div>
            <div style={{ fontSize: 11, color: "#6B7280" }}>Everything runs on free tiers until scale demands upgrades</div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {infraStack.map((item, i) => (
              <div key={i} style={{
                display: "flex",
                alignItems: "center",
                gap: 12,
                background: "#111113",
                border: "1px solid #2D2D30",
                borderRadius: 10,
                padding: "12px 16px",
              }}>
                <div style={{ fontSize: 22, width: 36, textAlign: "center" }}>{item.icon}</div>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: "#E5E5E5" }}>{item.name}</div>
                  <div style={{ fontSize: 11, color: "#6B7280" }}>{item.role}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Daily Flow View */}
      {view === "flow" && (
        <div style={{ display: "flex", flexDirection: "column", gap: 0 }}>
          {[
            { time: "2:00 AM", agent: "Agent 1", action: "Scrapes leads, scores, generates free samples", color: "#3B82F6", auto: true },
            { time: "6:00 AM", agent: "Agent 3", action: "Pre-generates deliverables for active orders", color: "#10B981", auto: true },
            { time: "8:00 AM", agent: "Agent 2", action: "Sends outreach emails + follow-ups", color: "#8B5CF6", auto: true },
            { time: "9:00 AM", agent: "YOU", action: "Open Cowork → review briefing → approve/reject (15 min)", color: "#F59E0B", auto: false },
            { time: "9:15 AM", agent: "Agent 2", action: "Sends approved proposals to interested leads", color: "#8B5CF6", auto: true },
            { time: "9:15 AM", agent: "Agent 3", action: "Delivers approved work to clients", color: "#10B981", auto: true },
            { time: "All Day", agent: "Agent 4", action: "Logs metrics, tracks opens/replies", color: "#EF4444", auto: true },
            { time: "9:00 PM", agent: "YOU", action: "Quick 15-min check if anything was flagged", color: "#F59E0B", auto: false },
            { time: "Sunday", agent: "Agent 4", action: "Weekly report + strategy recommendations", color: "#EF4444", auto: true },
          ].map((step, i) => (
            <div key={i} style={{ display: "flex", gap: 16, minHeight: 64 }}>
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: 50 }}>
                <div style={{
                  width: 10, height: 10,
                  borderRadius: "50%",
                  background: step.auto ? step.color : "#F59E0B",
                  border: step.auto ? "none" : "2px solid #F59E0B",
                  flexShrink: 0,
                  marginTop: 4,
                }}/>
                {i < 8 && <div style={{ width: 1, flex: 1, background: "#2D2D30" }}/>}
              </div>
              <div style={{ paddingBottom: 16, flex: 1 }}>
                <div style={{ display: "flex", gap: 8, alignItems: "baseline", flexWrap: "wrap" }}>
                  <span style={{ fontSize: 11, color: "#6B7280", fontWeight: 600, minWidth: 60 }}>{step.time}</span>
                  <span style={{
                    fontSize: 10,
                    padding: "2px 6px",
                    borderRadius: 4,
                    background: step.auto ? "#1A1A1D" : "#92400E",
                    color: step.auto ? step.color : "#FCD34D",
                    fontWeight: 600,
                  }}>{step.agent}</span>
                </div>
                <div style={{ fontSize: 12, color: "#D1D5DB", marginTop: 4, lineHeight: 1.5 }}>{step.action}</div>
              </div>
            </div>
          ))}

          <div style={{
            background: "#111113",
            border: "1px solid #F59E0B40",
            borderRadius: 10,
            padding: 14,
            marginTop: 12,
            textAlign: "center",
          }}>
            <div style={{ fontSize: 24, fontWeight: 700, color: "#F59E0B" }}>30 min</div>
            <div style={{ fontSize: 12, color: "#9CA3AF" }}>Your total daily involvement</div>
          </div>
        </div>
      )}

      {/* Build Phases View */}
      {view === "phases" && (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {phases.map((phase, i) => (
            <div key={i} style={{
              background: "#111113",
              border: "1px solid #2D2D30",
              borderRadius: 10,
              padding: 14,
              display: "flex",
              alignItems: "center",
              gap: 14,
            }}>
              <div style={{
                width: 36, height: 36,
                borderRadius: 8,
                background: i === 0 ? "#F59E0B20" : "#1A1A1D",
                border: `1.5px solid ${i === 0 ? "#F59E0B" : "#3D3D42"}`,
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 14, fontWeight: 800,
                color: i === 0 ? "#F59E0B" : "#6B7280",
                flexShrink: 0,
              }}>{phase.num}</div>
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                  <span style={{ fontSize: 13, fontWeight: 700, color: i === 0 ? "#F59E0B" : "#E5E5E5" }}>{phase.name}</span>
                  <span style={{ fontSize: 10, color: "#6B7280" }}>Week {phase.weeks}</span>
                </div>
                <div style={{ fontSize: 11, color: "#9CA3AF", marginTop: 2 }}>{phase.desc}</div>
              </div>
            </div>
          ))}

          <div style={{
            background: "#111113",
            border: "1px dashed #3D3D42",
            borderRadius: 10,
            padding: 14,
            marginTop: 8,
            textAlign: "center",
          }}>
            <div style={{ fontSize: 12, color: "#6B7280" }}>Target: system fully operational in</div>
            <div style={{ fontSize: 22, fontWeight: 700, color: "#10B981", marginTop: 4 }}>7 weeks</div>
            <div style={{ fontSize: 11, color: "#6B7280", marginTop: 2 }}>Adjusted to your marathon pace</div>
          </div>
        </div>
      )}
    </div>
  );
}
