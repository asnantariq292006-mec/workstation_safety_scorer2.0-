import { useState, useEffect, useRef } from "react";

const COLORS = {
  bg: "#0B0F19",
  glass: "rgba(255,255,255,0.04)",
  glassBorder: "rgba(0,240,255,0.15)",
  cyan: "#00F0FF",
  cyanDim: "rgba(0,240,255,0.15)",
  cyanGlow: "rgba(0,240,255,0.4)",
  white: "#FFFFFF",
  silver: "#A0AEC0",
  navy: "#131829",
  navyLight: "#1A2240",
  green: "#00FF94",
  amber: "#FFB800",
  red: "#FF4D6D",
  purple: "#B48FFF",
};

const CATEGORIES = [
  { name: "Chair & Posture", icon: "🪑", score: 72, color: COLORS.cyan },
  { name: "Screen & Display", icon: "🖥️", score: 58, color: COLORS.purple },
  { name: "Keyboard & Mouse", icon: "⌨️", score: 85, color: COLORS.green },
  { name: "Lighting", icon: "💡", score: 45, color: COLORS.amber },
  { name: "Environment", icon: "🌡️", score: 63, color: "#FF6B9D" },
  { name: "Work Habits", icon: "⏱️", score: 70, color: "#7EB8FF" },
];

const HISTORY = [
  { month: "Jan", score: 42 },
  { month: "Feb", score: 48 },
  { month: "Mar", score: 51 },
  { month: "Apr", score: 55 },
  { month: "May", score: 60 },
  { month: "Jun", score: 65 },
  { month: "Jul", score: 60 },
];

const ASSESSMENT_QUESTIONS = [
  { id: 1, category: "Chair & Posture", question: "Is your chair height adjustable so feet rest flat?", weight: 15 },
  { id: 2, category: "Chair & Posture", question: "Does your lower back have lumbar support?", weight: 12 },
  { id: 3, category: "Screen & Display", question: "Is the monitor top at or slightly below eye level?", weight: 10 },
  { id: 4, category: "Screen & Display", question: "Is viewing distance 50–70 cm from eyes?", weight: 10 },
  { id: 5, category: "Keyboard & Mouse", question: "Are wrists neutral (not bent) while typing?", weight: 12 },
  { id: 6, category: "Keyboard & Mouse", question: "Is the mouse within easy reach without stretching?", weight: 8 },
  { id: 7, category: "Lighting", question: "Is there no glare or reflection on your screen?", weight: 10 },
  { id: 8, category: "Lighting", question: "Is ambient lighting sufficient without eye strain?", weight: 8 },
  { id: 9, category: "Environment", question: "Is room temperature comfortable (20–24°C)?", weight: 8 },
  { id: 10, category: "Work Habits", question: "Do you take regular breaks every 45–60 mins?", weight: 7 },
];

function useCountUp(target, duration = 1500, delay = 0) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    let timeout;
    let start;
    let animFrame;
    timeout = setTimeout(() => {
      start = performance.now();
      const tick = (now) => {
        const p = Math.min((now - start) / duration, 1);
        const ease = 1 - Math.pow(1 - p, 3);
        setCount(Math.round(ease * target));
        if (p < 1) animFrame = requestAnimationFrame(tick);
      };
      animFrame = requestAnimationFrame(tick);
    }, delay);
    return () => { clearTimeout(timeout); cancelAnimationFrame(animFrame); };
  }, [target, duration, delay]);
  return count;
}

function ParticleField() {
  const canvasRef = useRef(null);
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    const particles = Array.from({ length: 60 }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      r: Math.random() * 1.5 + 0.3,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      alpha: Math.random() * 0.5 + 0.1,
    }));
    let raf;
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      particles.forEach((p) => {
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0) p.x = canvas.width;
        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(0,240,255,${p.alpha})`;
        ctx.fill();
      });
      raf = requestAnimationFrame(draw);
    };
    draw();
    return () => cancelAnimationFrame(raf);
  }, []);
  return <canvas ref={canvasRef} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", pointerEvents: "none" }} />;
}

function RadarChart({ categories }) {
  const cx = 140, cy = 140, r = 100;
  const n = categories.length;
  const angles = categories.map((_, i) => (i * 2 * Math.PI) / n - Math.PI / 2);
  const toXY = (angle, radius) => ({
    x: cx + radius * Math.cos(angle),
    y: cy + radius * Math.sin(angle),
  });
  const gridLevels = [0.25, 0.5, 0.75, 1];
  const dataPoints = categories.map((cat, i) => toXY(angles[i], (cat.score / 100) * r));
  const dataPath = dataPoints.map((p, i) => `${i === 0 ? "M" : "L"}${p.x},${p.y}`).join(" ") + " Z";

  return (
    <svg width="280" height="280" viewBox="0 0 280 280">
      <defs>
        <radialGradient id="radarGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor={COLORS.cyan} stopOpacity="0.3" />
          <stop offset="100%" stopColor={COLORS.cyan} stopOpacity="0" />
        </radialGradient>
        <filter id="glow">
          <feGaussianBlur stdDeviation="3" result="blur" />
          <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>
      {gridLevels.map((lvl) => {
        const pts = angles.map((a) => toXY(a, lvl * r));
        const path = pts.map((p, i) => `${i === 0 ? "M" : "L"}${p.x},${p.y}`).join(" ") + " Z";
        return <path key={lvl} d={path} fill="none" stroke="rgba(0,240,255,0.12)" strokeWidth="1" />;
      })}
      {angles.map((angle, i) => {
        const end = toXY(angle, r);
        return <line key={i} x1={cx} y1={cy} x2={end.x} y2={end.y} stroke="rgba(0,240,255,0.1)" strokeWidth="1" />;
      })}
      <path d={dataPath} fill="rgba(0,240,255,0.12)" stroke={COLORS.cyan} strokeWidth="2" filter="url(#glow)" />
      {dataPoints.map((p, i) => (
        <g key={i}>
          <circle cx={p.x} cy={p.y} r="5" fill={categories[i].color} filter="url(#glow)" />
          <circle cx={p.x} cy={p.y} r="3" fill={COLORS.white} />
        </g>
      ))}
      {angles.map((angle, i) => {
        const pos = toXY(angle, r + 22);
        return (
          <text key={i} x={pos.x} y={pos.y} textAnchor="middle" dominantBaseline="middle"
            fontSize="9" fill={COLORS.silver} fontFamily="'Rajdhani', sans-serif">
            {categories[i].icon} {categories[i].name.split(" ")[0]}
          </text>
        );
      })}
    </svg>
  );
}

function SplineChart({ data }) {
  const w = 420, h = 140, pad = 30;
  const xs = data.map((_, i) => pad + (i / (data.length - 1)) * (w - pad * 2));
  const ys = data.map((d) => h - pad - ((d.score - 30) / 60) * (h - pad * 2));

  const pathD = xs.map((x, i) => {
    if (i === 0) return `M${x},${ys[i]}`;
    const px = xs[i - 1], py = ys[i - 1];
    const cp1x = px + (x - px) / 3, cp1y = py;
    const cp2x = x - (x - px) / 3, cp2y = ys[i];
    return `C${cp1x},${cp1y} ${cp2x},${cp2y} ${x},${ys[i]}`;
  }).join(" ");

  const fillPath = pathD + ` L${xs[xs.length - 1]},${h - pad} L${xs[0]},${h - pad} Z`;

  return (
    <svg width="100%" viewBox={`0 0 ${w} ${h}`} style={{ overflow: "visible" }}>
      <defs>
        <linearGradient id="splineGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={COLORS.cyan} stopOpacity="0.25" />
          <stop offset="100%" stopColor={COLORS.cyan} stopOpacity="0" />
        </linearGradient>
        <filter id="lineglow">
          <feGaussianBlur stdDeviation="2" result="blur" />
          <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>
      {[40, 55, 70].map((v) => {
        const y = h - pad - ((v - 30) / 60) * (h - pad * 2);
        return (
          <g key={v}>
            <line x1={pad} y1={y} x2={w - pad} y2={y} stroke="rgba(255,255,255,0.05)" strokeWidth="1" strokeDasharray="4,4" />
            <text x={pad - 8} y={y} textAnchor="end" dominantBaseline="middle" fontSize="8" fill={COLORS.silver} fontFamily="'Rajdhani',sans-serif">{v}%</text>
          </g>
        );
      })}
      <path d={fillPath} fill="url(#splineGrad)" />
      <path d={pathD} fill="none" stroke={COLORS.cyan} strokeWidth="2.5" filter="url(#lineglow)" />
      {xs.map((x, i) => (
        <g key={i}>
          {i === data.length - 2 && (
            <>
              <circle cx={x} cy={ys[i]} r="10" fill={COLORS.cyan} opacity="0.15">
                <animate attributeName="r" values="8;14;8" dur="2s" repeatCount="indefinite" />
                <animate attributeName="opacity" values="0.2;0.05;0.2" dur="2s" repeatCount="indefinite" />
              </circle>
              <circle cx={x} cy={ys[i]} r="5" fill={COLORS.cyan} filter="url(#lineglow)" />
              <circle cx={x} cy={ys[i]} r="3" fill={COLORS.white} />
            </>
          )}
          {i !== data.length - 2 && <circle cx={x} cy={ys[i]} r="3" fill={COLORS.cyan} opacity="0.6" />}
          <text x={x} y={h - pad + 12} textAnchor="middle" fontSize="8" fill={COLORS.silver} fontFamily="'Rajdhani',sans-serif">{data[i].month}</text>
        </g>
      ))}
    </svg>
  );
}

function GlassCard({ children, style = {}, glow = false }) {
  return (
    <div style={{
      background: "rgba(255,255,255,0.04)",
      border: `1px solid ${glow ? COLORS.cyanGlow : COLORS.glassBorder}`,
      borderRadius: 16,
      backdropFilter: "blur(20px)",
      boxShadow: glow
        ? `0 0 30px rgba(0,240,255,0.15), inset 0 1px 0 rgba(0,240,255,0.2)`
        : `0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.06)`,
      ...style,
    }}>
      {children}
    </div>
  );
}

function NavItem({ icon, label, active, onClick }) {
  return (
    <div onClick={onClick} style={{
      display: "flex", alignItems: "center", gap: 10, padding: "12px 16px",
      borderRadius: 12, cursor: "pointer", transition: "all 0.3s",
      background: active ? "rgba(0,240,255,0.1)" : "transparent",
      border: active ? `1px solid rgba(0,240,255,0.3)` : "1px solid transparent",
      color: active ? COLORS.cyan : COLORS.silver,
      position: "relative", overflow: "hidden",
    }}>
      {active && (
        <div style={{
          position: "absolute", left: 0, top: "50%", transform: "translateY(-50%)",
          width: 3, height: 24, background: COLORS.cyan,
          borderRadius: "0 4px 4px 0",
          boxShadow: `0 0 10px ${COLORS.cyan}`,
        }} />
      )}
      <span style={{ fontSize: 18 }}>{icon}</span>
      <span style={{ fontSize: 13, fontFamily: "'Rajdhani', sans-serif", fontWeight: 600, letterSpacing: 1 }}>{label}</span>
      {active && (
        <div style={{
          marginLeft: "auto", width: 6, height: 6, borderRadius: "50%",
          background: COLORS.cyan, boxShadow: `0 0 8px ${COLORS.cyan}`,
        }}>
          <div style={{
            width: 6, height: 6, borderRadius: "50%", background: COLORS.cyan,
            animation: "pulse 2s infinite",
          }} />
        </div>
      )}
    </div>
  );
}

function AssessmentView({ onBack }) {
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [score, setScore] = useState(0);

  const handleAnswer = (id, val) => setAnswers((a) => ({ ...a, [id]: val }));

  const handleSubmit = () => {
    let total = 0, maxTotal = 0;
    ASSESSMENT_QUESTIONS.forEach((q) => {
      maxTotal += q.weight;
      if (answers[q.id] !== undefined) total += (answers[q.id] / 4) * q.weight;
    });
    setScore(Math.round((total / maxTotal) * 100));
    setSubmitted(true);
  };

  const getRiskLabel = (s) => s >= 75 ? { label: "Low Risk", color: COLORS.green } :
    s >= 50 ? { label: "Moderate Risk", color: COLORS.amber } :
      { label: "High Risk", color: COLORS.red };

  if (submitted) {
    const risk = getRiskLabel(score);
    return (
      <div style={{ padding: 24 }}>
        <GlassCard glow style={{ padding: 32, textAlign: "center", maxWidth: 500, margin: "0 auto" }}>
          <div style={{ fontSize: 12, color: COLORS.silver, letterSpacing: 3, marginBottom: 16, fontFamily: "'Rajdhani',sans-serif" }}>ASSESSMENT COMPLETE</div>
          <div style={{ fontSize: 72, fontWeight: 900, color: COLORS.cyan, fontFamily: "'Orbitron',sans-serif", lineHeight: 1, textShadow: `0 0 30px ${COLORS.cyan}` }}>
            {score}%
          </div>
          <div style={{ color: risk.color, fontSize: 18, marginTop: 8, fontFamily: "'Rajdhani',sans-serif", fontWeight: 700, letterSpacing: 2 }}>
            ● {risk.label}
          </div>
          <div style={{ color: COLORS.silver, fontSize: 13, marginTop: 16, lineHeight: 1.8 }}>
            {score >= 75 ? "Excellent workstation setup. Maintain your current ergonomic practices." :
              score >= 50 ? "Several improvements needed. Review lighting and posture settings." :
                "Immediate ergonomic intervention recommended. Multiple risk factors detected."}
          </div>
          <button onClick={onBack} style={{
            marginTop: 24, padding: "12px 28px", background: "rgba(0,240,255,0.1)",
            border: `1px solid ${COLORS.cyan}`, borderRadius: 10, color: COLORS.cyan,
            fontFamily: "'Rajdhani',sans-serif", fontWeight: 700, fontSize: 13,
            letterSpacing: 2, cursor: "pointer",
          }}>← BACK TO DASHBOARD</button>
        </GlassCard>
      </div>
    );
  }

  return (
    <div style={{ padding: 24, maxHeight: "calc(100vh - 80px)", overflowY: "auto" }}>
      <div style={{ marginBottom: 20 }}>
        <div style={{ fontSize: 11, color: COLORS.silver, letterSpacing: 3, fontFamily: "'Rajdhani',sans-serif" }}>NEW ASSESSMENT</div>
        <div style={{ fontSize: 22, color: COLORS.white, fontFamily: "'Orbitron',sans-serif", marginTop: 4 }}>Ergonomic Evaluation</div>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {ASSESSMENT_QUESTIONS.map((q, idx) => (
          <GlassCard key={q.id} style={{ padding: "16px 20px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
              <div>
                <div style={{ fontSize: 10, color: COLORS.cyan, letterSpacing: 2, fontFamily: "'Rajdhani',sans-serif", marginBottom: 4 }}>{q.category.toUpperCase()}</div>
                <div style={{ fontSize: 13, color: COLORS.white, fontFamily: "'Rajdhani',sans-serif" }}>Q{idx + 1}. {q.question}</div>
              </div>
              <div style={{ fontSize: 10, color: COLORS.silver, minWidth: 50, textAlign: "right" }}>Weight: {q.weight}%</div>
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              {["Never", "Rarely", "Sometimes", "Often", "Always"].map((label, val) => (
                <button key={val} onClick={() => handleAnswer(q.id, val)} style={{
                  flex: 1, padding: "6px 4px", borderRadius: 8, fontSize: 10,
                  fontFamily: "'Rajdhani',sans-serif", fontWeight: 600, letterSpacing: 0.5, cursor: "pointer",
                  border: answers[q.id] === val ? `1px solid ${COLORS.cyan}` : "1px solid rgba(255,255,255,0.1)",
                  background: answers[q.id] === val ? "rgba(0,240,255,0.15)" : "rgba(255,255,255,0.03)",
                  color: answers[q.id] === val ? COLORS.cyan : COLORS.silver,
                  transition: "all 0.2s",
                }}>{label}</button>
              ))}
            </div>
          </GlassCard>
        ))}
      </div>
      <div style={{ marginTop: 20, textAlign: "center" }}>
        <button onClick={handleSubmit} style={{
          padding: "14px 40px", background: "linear-gradient(135deg, rgba(0,240,255,0.2), rgba(0,240,255,0.05))",
          border: `1px solid ${COLORS.cyan}`, borderRadius: 12, color: COLORS.cyan,
          fontFamily: "'Orbitron',sans-serif", fontWeight: 700, fontSize: 12,
          letterSpacing: 3, cursor: "pointer",
          boxShadow: `0 0 20px rgba(0,240,255,0.2)`,
        }}>CALCULATE SCORE →</button>
      </div>
    </div>
  );
}

export default function WorkstationSafetyScorer() {
  const [activeNav, setActiveNav] = useState("dashboard");
  const assessments = useCountUp(35, 1800, 300);
  const scoreAnim = useCountUp(60, 2000, 500);
  const risk = useCountUp(3, 1200, 700);

  const navItems = [
    { id: "dashboard", icon: "⬡", label: "DASHBOARD" },
    { id: "assessment", icon: "◈", label: "ASSESSMENT" },
    { id: "analytics", icon: "◉", label: "ANALYTICS" },
    { id: "reports", icon: "◫", label: "REPORTS" },
    { id: "settings", icon: "⚙", label: "SETTINGS" },
  ];

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;500;600;700&display=swap');
        @keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.4;transform:scale(1.5)} }
        @keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-6px)} }
        @keyframes scanline { 0%{transform:translateY(-100%)} 100%{transform:translateY(100vh)} }
        @keyframes borderGlow { 0%,100%{box-shadow:0 0 20px rgba(0,240,255,0.1)} 50%{box-shadow:0 0 40px rgba(0,240,255,0.3)} }
        * { box-sizing: border-box; margin: 0; padding: 0; scrollbar-width: thin; scrollbar-color: rgba(0,240,255,0.3) transparent; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: rgba(0,240,255,0.3); border-radius: 2px; }
      `}</style>
      <div style={{
        minHeight: "100vh", background: COLORS.bg, display: "flex",
        fontFamily: "'Rajdhani', sans-serif", position: "relative", overflow: "hidden",
      }}>
        <ParticleField />

        {/* Ambient glows */}
        <div style={{ position: "absolute", top: -200, left: -100, width: 500, height: 500, borderRadius: "50%", background: "radial-gradient(circle, rgba(0,240,255,0.06) 0%, transparent 70%)", pointerEvents: "none" }} />
        <div style={{ position: "absolute", bottom: -200, right: -100, width: 600, height: 600, borderRadius: "50%", background: "radial-gradient(circle, rgba(180,143,255,0.05) 0%, transparent 70%)", pointerEvents: "none" }} />

        {/* Left Nav */}
        <div style={{
          width: 200, minHeight: "100vh", background: "rgba(11,15,25,0.8)",
          borderRight: `1px solid rgba(0,240,255,0.1)`,
          backdropFilter: "blur(30px)", padding: "24px 12px", display: "flex", flexDirection: "column", gap: 4,
          position: "relative", zIndex: 10, flexShrink: 0,
        }}>
          {/* Logo */}
          <div style={{ padding: "8px 16px 24px" }}>
            <div style={{ fontSize: 16, fontFamily: "'Orbitron',sans-serif", fontWeight: 900, color: COLORS.cyan, letterSpacing: 1, textShadow: `0 0 20px ${COLORS.cyan}` }}>WSS</div>
            <div style={{ fontSize: 9, color: COLORS.silver, letterSpacing: 2, marginTop: 2 }}>ERGO·PLATFORM</div>
          </div>

          {navItems.map((item) => (
            <NavItem key={item.id} icon={item.icon} label={item.label} active={activeNav === item.id} onClick={() => setActiveNav(item.id)} />
          ))}

          <div style={{ marginTop: "auto", padding: "16px", borderTop: "1px solid rgba(0,240,255,0.08)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <div style={{ width: 36, height: 36, borderRadius: 10, background: "linear-gradient(135deg, rgba(0,240,255,0.3), rgba(180,143,255,0.2))", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16, border: `1px solid rgba(0,240,255,0.3)` }}>A</div>
              <div>
                <div style={{ fontSize: 12, color: COLORS.white, fontWeight: 700 }}>Asnan</div>
                <div style={{ fontSize: 10, color: COLORS.silver }}>UET Taxila</div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div style={{ flex: 1, overflow: "hidden", display: "flex", flexDirection: "column" }}>
          {/* Top Bar */}
          <div style={{
            padding: "16px 28px", borderBottom: `1px solid rgba(0,240,255,0.08)`,
            background: "rgba(11,15,25,0.5)", backdropFilter: "blur(20px)",
            display: "flex", alignItems: "center", justifyContent: "space-between",
          }}>
            <div>
              <div style={{ fontSize: 22, fontFamily: "'Orbitron',sans-serif", fontWeight: 900, color: COLORS.white, letterSpacing: 1 }}>
                Welcome, <span style={{ color: COLORS.cyan, textShadow: `0 0 20px ${COLORS.cyan}` }}>Asnan</span> 👋
              </div>
              <div style={{ fontSize: 11, color: COLORS.silver, marginTop: 2, letterSpacing: 2 }}>ICT IN HEALTH AND ERGONOMICS: WORKSTATION SAFETY SCORER • ENGINEERING</div>
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              {["●", "●", "●"].map((dot, i) => (
                <div key={i} style={{ width: 8, height: 8, borderRadius: "50%", background: i === 0 ? COLORS.green : i === 1 ? COLORS.amber : COLORS.red, boxShadow: `0 0 8px ${i === 0 ? COLORS.green : i === 1 ? COLORS.amber : COLORS.red}` }} />
              ))}
            </div>
          </div>

          {/* Content */}
          {activeNav === "assessment" ? (
            <div style={{ overflowY: "auto", flex: 1 }}>
              <AssessmentView onBack={() => setActiveNav("dashboard")} />
            </div>
          ) : activeNav === "analytics" ? (
            <div style={{ flex: 1, overflowY: "auto", padding: 24, display: "flex", flexDirection: "column", gap: 20 }}>
              <GlassCard style={{ padding: 24 }}>
                <div style={{ fontSize: 11, color: COLORS.cyan, letterSpacing: 3, marginBottom: 16, fontFamily: "'Rajdhani',sans-serif" }}>CATEGORY BREAKDOWN</div>
                <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                  {CATEGORIES.map((cat) => (
                    <div key={cat.name}>
                      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                        <span style={{ fontSize: 13, color: COLORS.silver }}>{cat.icon} {cat.name}</span>
                        <span style={{ fontSize: 13, color: cat.color, fontFamily: "'Orbitron',sans-serif" }}>{cat.score}%</span>
                      </div>
                      <div style={{ height: 6, background: "rgba(255,255,255,0.06)", borderRadius: 3, overflow: "hidden" }}>
                        <div style={{ height: "100%", width: `${cat.score}%`, background: `linear-gradient(90deg, ${cat.color}, ${cat.color}88)`, borderRadius: 3, boxShadow: `0 0 8px ${cat.color}`, transition: "width 1s" }} />
                      </div>
                    </div>
                  ))}
                </div>
              </GlassCard>
            </div>
          ) : activeNav === "reports" ? (
            <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <GlassCard style={{ padding: 40, textAlign: "center" }}>
                <div style={{ fontSize: 40, marginBottom: 16 }}>📊</div>
                <div style={{ fontSize: 16, color: COLORS.white, fontFamily: "'Orbitron',sans-serif" }}>Reports Module</div>
                <div style={{ fontSize: 13, color: COLORS.silver, marginTop: 8 }}>PDF export available after assessment</div>
              </GlassCard>
            </div>
          ) : activeNav === "settings" ? (
            <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <GlassCard style={{ padding: 40, textAlign: "center" }}>
                <div style={{ fontSize: 40, marginBottom: 16 }}>⚙️</div>
                <div style={{ fontSize: 16, color: COLORS.white, fontFamily: "'Orbitron',sans-serif" }}>Settings</div>
                <div style={{ fontSize: 13, color: COLORS.silver, marginTop: 8 }}>Configuration panel coming soon</div>
              </GlassCard>
            </div>
          ) : (
            <div style={{ flex: 1, overflowY: "auto", padding: "20px 24px", display: "flex", flexDirection: "column", gap: 20 }}>
              {/* Summary Cards */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16 }}>
                {[
                  { label: "Total Assessments", value: assessments, unit: "", icon: "◈", color: COLORS.cyan, desc: "All time records" },
                  { label: "Average Score", value: scoreAnim, unit: "%", icon: "◉", color: COLORS.purple, desc: "Current period" },
                  { label: "Risk Factors", value: risk, unit: " detected", icon: "⚠", color: COLORS.amber, desc: "Needs attention" },
                ].map((card, i) => (
                  <GlassCard key={i} glow={i === 1} style={{ padding: "20px 24px", animation: "borderGlow 4s infinite", animationDelay: `${i * 0.5}s` }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                      <div>
                        <div style={{ fontSize: 10, color: COLORS.silver, letterSpacing: 3, marginBottom: 8 }}>{card.label.toUpperCase()}</div>
                        <div style={{ fontSize: 36, fontFamily: "'Orbitron',sans-serif", fontWeight: 900, color: card.color, lineHeight: 1, textShadow: `0 0 20px ${card.color}88` }}>
                          {card.value}{card.unit}
                        </div>
                        <div style={{ fontSize: 11, color: COLORS.silver, marginTop: 6 }}>{card.desc}</div>
                      </div>
                      <div style={{ fontSize: 28, color: card.color, opacity: 0.6 }}>{card.icon}</div>
                    </div>
                  </GlassCard>
                ))}
              </div>

              {/* Main Charts Row */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1.4fr", gap: 16 }}>
                {/* Radar */}
                <GlassCard style={{ padding: 20 }}>
                  <div style={{ fontSize: 10, color: COLORS.cyan, letterSpacing: 3, marginBottom: 12 }}>ERGONOMIC RADAR</div>
                  <div style={{ display: "flex", justifyContent: "center" }}>
                    <RadarChart categories={CATEGORIES} />
                  </div>
                </GlassCard>

                {/* Score History */}
                <GlassCard style={{ padding: 20 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                    <div style={{ fontSize: 10, color: COLORS.cyan, letterSpacing: 3 }}>SCORE HISTORY</div>
                    <div style={{ fontSize: 10, color: COLORS.green, letterSpacing: 1 }}>▲ +18% this quarter</div>
                  </div>
                  <SplineChart data={HISTORY} />
                  <div style={{ display: "flex", gap: 16, marginTop: 16 }}>
                    {[{ label: "Peak", val: "65%", color: COLORS.cyan }, { label: "Avg", val: "54%", color: COLORS.purple }, { label: "Min", val: "42%", color: COLORS.amber }].map((s) => (
                      <div key={s.label} style={{ flex: 1, textAlign: "center" }}>
                        <div style={{ fontSize: 18, fontFamily: "'Orbitron',sans-serif", color: s.color, fontWeight: 700 }}>{s.val}</div>
                        <div style={{ fontSize: 10, color: COLORS.silver, letterSpacing: 1 }}>{s.label}</div>
                      </div>
                    ))}
                  </div>
                </GlassCard>
              </div>

              {/* Category Bars */}
              <GlassCard style={{ padding: 20 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                  <div style={{ fontSize: 10, color: COLORS.cyan, letterSpacing: 3 }}>RISK CATEGORY OVERVIEW</div>
                  <button onClick={() => setActiveNav("assessment")} style={{
                    padding: "8px 16px", background: "rgba(0,240,255,0.1)", border: `1px solid rgba(0,240,255,0.4)`,
                    borderRadius: 8, color: COLORS.cyan, fontSize: 10, letterSpacing: 2,
                    fontFamily: "'Rajdhani',sans-serif", fontWeight: 700, cursor: "pointer",
                  }}>NEW ASSESSMENT →</button>
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
                  {CATEGORIES.map((cat) => {
                    const riskLevel = cat.score >= 75 ? "Low" : cat.score >= 50 ? "Moderate" : "High";
                    const riskColor = cat.score >= 75 ? COLORS.green : cat.score >= 50 ? COLORS.amber : COLORS.red;
                    return (
                      <div key={cat.name} style={{ padding: "12px 16px", background: "rgba(255,255,255,0.03)", borderRadius: 10, border: `1px solid rgba(255,255,255,0.06)` }}>
                        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                          <span style={{ fontSize: 16 }}>{cat.icon}</span>
                          <span style={{ fontSize: 10, color: riskColor, fontWeight: 700 }}>{riskLevel}</span>
                        </div>
                        <div style={{ fontSize: 12, color: COLORS.white, marginBottom: 6, fontWeight: 600 }}>{cat.name}</div>
                        <div style={{ height: 4, background: "rgba(255,255,255,0.06)", borderRadius: 2 }}>
                          <div style={{ height: "100%", width: `${cat.score}%`, background: `linear-gradient(90deg, ${cat.color}, ${cat.color}66)`, borderRadius: 2, boxShadow: `0 0 6px ${cat.color}` }} />
                        </div>
                        <div style={{ fontSize: 18, fontFamily: "'Orbitron',sans-serif", color: cat.color, marginTop: 8, fontWeight: 700 }}>{cat.score}<span style={{ fontSize: 10 }}>%</span></div>
                      </div>
                    );
                  })}
                </div>
              </GlassCard>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
