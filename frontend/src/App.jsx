import { useState } from "react"
import axios from "axios"

const API = "http://127.0.0.1:8000"

const steps = [
  { id: 1, label: "Trends", icon: "📡" },
  { id: 2, label: "Script", icon: "✍️" },
  { id: 3, label: "Captions", icon: "📝" },
  { id: 4, label: "Virality", icon: "🔮" },
  { id: 5, label: "Voiceover", icon: "🎙️" },
  { id: 6, label: "Thumbnail", icon: "🖼️" },
  { id: 7, label: "B-Roll", icon: "🎞️" },
  { id: 8, label: "Subtitles", icon: "💬" },
  { id: 9, label: "Video", icon: "🎬" },
]

export default function App() {
  const [topic, setTopic] = useState("")
  const [loading, setLoading] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [results, setResults] = useState(null)
  const [error, setError] = useState("")

  const runManual = async () => {
    if (!topic.trim()) return
    setLoading(true)
    setError("")
    setResults(null)
    setCurrentStep(0)

    try {
      setCurrentStep(1)
      const trendsRes = await axios.get(`${API}/trends/discover`)
      const trends = trendsRes.data.trends

      setCurrentStep(2)
      const scriptRes = await axios.post(`${API}/scripts/generate`, {
        topic,
        trend_score: trends[0]?.trend_score || 75,
        duration: 60,
      })
      const script = scriptRes.data

      setCurrentStep(3)
      const contentRes = await axios.post(`${API}/content/both`, {
        topic,
        hook: script.hook,
        key_insights: script.key_insights,
      })
      const content = contentRes.data

      setCurrentStep(4)
      const viralRes = await axios.post(`${API}/virality/predict`, {
        topic,
        hook: script.hook,
        story: script.story,
        key_insights: script.key_insights,
        cta: script.cta,
        word_count: script.word_count,
        trend_score: script.trend_score,
        linkedin_hashtags: content.linkedin?.hashtags || [],
        instagram_hashtags: content.instagram?.hashtags || [],
      })

      setCurrentStep(5)
      let voiceoverData = null
      try {
        const voiceRes = await axios.post(`${API}/voiceover/generate`, {
          script: script.full_script,
        })
        voiceoverData = voiceRes.data
      } catch (e) {
        console.log("Voiceover skipped:", e.message)
      }

      setCurrentStep(6)
      let thumbnailData = null
      try {
        const thumbRes = await axios.post(`${API}/thumbnail/generate`, {
          topic,
          hook: script.hook,
        })
        thumbnailData = thumbRes.data
      } catch (e) {
        console.log("Thumbnail skipped:", e.message)
      }

      setCurrentStep(7)
      let brollData = []
      try {
        const brollRes = await axios.post(`${API}/reel/broll`, {
          script,
          duration_sec: script.estimated_duration_sec || 60,
        })
        brollData = brollRes.data.scenes || []
      } catch (e) {
        console.log("B-Roll skipped:", e.message)
      }

      setCurrentStep(8)
      let subtitlesData = []
      let srtData = ""
      try {
        const subRes = await axios.post(`${API}/reel/subtitles`, {
          script,
          duration_sec: script.estimated_duration_sec || 60,
        })
        subtitlesData = subRes.data.subtitles || []
        srtData = subRes.data.srt_content || ""
      } catch (e) {
        console.log("Subtitles skipped:", e.message)
      }

      setCurrentStep(9)
      let videoData = null
      try {
        if (brollData.length > 0 && voiceoverData?.audio_base64) {
          const videoRes = await axios.post(`${API}/reel/video`, {
            broll: brollData,
            voiceover_b64: voiceoverData.audio_base64,
            subtitles: subtitlesData,
          }, { timeout: 120000 })
          videoData = videoRes.data
        }
      } catch (e) {
        console.log("Video skipped:", e.message)
      }

      setResults({
        trends: trends.slice(0, 5),
        script,
        linkedin: content.linkedin,
        instagram: content.instagram,
        virality: viralRes.data,
        voiceover: voiceoverData,
        thumbnail: thumbnailData,
        broll: brollData,
        subtitles: subtitlesData,
        srt: srtData,
        video: videoData,
        topic,
      })
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    } finally {
      setLoading(false)
      setCurrentStep(0)
    }
  }

  const runAuto = async () => {
    setLoading(true)
    setError("")
    setResults(null)
    setCurrentStep(1)
    try {
      const res = await axios.post(`${API}/pipeline/run`, {
        topic: "",
        auto_trend: true,
        duration: 60,
      }, { timeout: 300000 })
      setCurrentStep(9)
      setResults(res.data)
      setTopic(res.data.topic || "")
    } catch (e) {
      try {
        const cached = await axios.get(`${API}/pipeline/demo`)
        setResults(cached.data)
        setTopic(cached.data.topic || "")
      } catch {
        setError(e.response?.data?.detail || e.message)
      }
    } finally {
      setLoading(false)
      setCurrentStep(0)
    }
  }

  return (
    <div style={{ minHeight: "100vh", background: "#0f0f0f", color: "#f0f0f0", fontFamily: "Inter, sans-serif" }}>
      <div style={{ maxWidth: 940, margin: "0 auto", padding: "2rem 1rem" }}>

        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: "2.5rem" }}>
          <div style={{ fontSize: 44, marginBottom: 10 }}>🎬</div>
          <h1 style={{ fontSize: 34, fontWeight: 700, margin: 0, color: "#fff", letterSpacing: -0.5 }}>
            Viral Reel Agent
          </h1>
          <p style={{ color: "#555", marginTop: 8, fontSize: 15 }}>
            AI-powered content pipeline — trend to ready-to-post in seconds
          </p>
        </div>

        {/* Auto button */}
        <div style={{ textAlign: "center", marginBottom: "1rem" }}>
          <button
            onClick={runAuto}
            disabled={loading}
            style={{
              padding: "12px 36px", borderRadius: 10,
              border: "1px solid #4f46e5",
              background: loading ? "transparent" : "#1e1b4b",
              color: loading ? "#444" : "#a5b4fc",
              fontSize: 15, cursor: loading ? "not-allowed" : "pointer",
              fontWeight: 500, transition: "all 0.2s"
            }}
          >
            ⚡ Auto — pick today's top trend for me
          </button>
        </div>

        {/* Divider */}
        <div style={{ display: "flex", alignItems: "center", gap: 12, margin: "1rem 0" }}>
          <div style={{ flex: 1, height: 1, background: "#1f1f1f" }} />
          <span style={{ color: "#333", fontSize: 13 }}>or enter your own topic</span>
          <div style={{ flex: 1, height: 1, background: "#1f1f1f" }} />
        </div>

        {/* Manual input */}
        <div style={{ display: "flex", gap: 10, marginBottom: "2rem" }}>
          <input
            value={topic}
            onChange={e => setTopic(e.target.value)}
            onKeyDown={e => e.key === "Enter" && !loading && runManual()}
            placeholder="Enter a topic or paste a trending headline..."
            style={{
              flex: 1, padding: "12px 16px", borderRadius: 10,
              background: "#1a1a1a", border: "1px solid #2a2a2a",
              color: "#f0f0f0", fontSize: 15, outline: "none"
            }}
          />
          <button
            onClick={runManual}
            disabled={loading || !topic.trim()}
            style={{
              padding: "12px 28px", borderRadius: 10, border: "none",
              background: loading || !topic.trim() ? "#1a1a1a" : "#6366f1",
              color: loading || !topic.trim() ? "#444" : "#fff",
              fontWeight: 600, fontSize: 15,
              cursor: loading || !topic.trim() ? "not-allowed" : "pointer",
              transition: "all 0.2s"
            }}
          >
            {loading ? "Running..." : "Generate ✨"}
          </button>
        </div>

        {/* Pipeline steps */}
        <div style={{ display: "flex", gap: 4, marginBottom: "2rem" }}>
          {steps.map(s => (
            <div key={s.id} style={{
              flex: 1, padding: "8px 4px", borderRadius: 8, textAlign: "center",
              background: currentStep >= s.id ? "#1e1b4b" : "#111",
              border: `1px solid ${currentStep >= s.id ? "#4f46e5" : "#1f1f1f"}`,
              transition: "all 0.4s"
            }}>
              <div style={{ fontSize: 14 }}>{s.icon}</div>
              <div style={{ fontSize: 9, color: currentStep >= s.id ? "#a5b4fc" : "#333", marginTop: 3, lineHeight: 1.3 }}>
                {s.label}
              </div>
              {loading && currentStep === s.id && (
                <div style={{ fontSize: 8, color: "#818cf8", marginTop: 2 }}>...</div>
              )}
              {results && s.id <= 9 && (
                <div style={{ fontSize: 8, color: "#4ade80", marginTop: 2 }}>✓</div>
              )}
            </div>
          ))}
        </div>

        {/* Error */}
        {error && (
          <div style={{
            background: "#1a0a0a", border: "1px solid #7f1d1d",
            borderRadius: 10, padding: "12px 16px",
            color: "#fca5a5", marginBottom: "1.5rem", fontSize: 13
          }}>
            ⚠️ {error}
          </div>
        )}

        {/* Results */}
        {results && (
          <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>

            {/* Summary bar */}
            {results.summary && (
              <div style={{
                background: "#111", border: "1px solid #1f1f1f",
                borderRadius: 12, padding: "1rem 1.25rem",
                display: "flex", gap: 16, flexWrap: "wrap", alignItems: "center"
              }}>
                <SummaryPill label="Trend score" value={`${results.summary.trend_score}/100`} color="#a5b4fc" />
                <SummaryPill label="Virality" value={`${results.summary.virality_score}/100`} color="#4ade80" />
                <SummaryPill label="Script" value={`${results.summary.word_count}w`} color="#fbbf24" />
                <SummaryPill label="Duration" value={`~${results.summary.duration_sec}s`} color="#60a5fa" />
                <SummaryPill label="Voiceover" value={results.summary.voiceover_ready ? "✓" : "—"} color={results.summary.voiceover_ready ? "#4ade80" : "#444"} />
                <SummaryPill label="Thumbnail" value={results.summary.thumbnail_ready ? "✓" : "—"} color={results.summary.thumbnail_ready ? "#4ade80" : "#444"} />
                <SummaryPill label="B-Roll" value={`${results.summary.broll_scenes || 0} scenes`} color="#f472b6" />
                <SummaryPill label="Subtitles" value={`${results.summary.subtitle_lines || 0} lines`} color="#34d399" />
                <SummaryPill label="Video" value={results.summary.video_ready ? "✓ MP4" : "—"} color={results.summary.video_ready ? "#4ade80" : "#444"} />
              </div>
            )}

            {/* Video player — show at top if ready */}
            {results.video?.video_base64 && (
              <div style={{ background: "#1a1a1a", border: "1px solid #2a2a2a", borderRadius: 12, padding: "1.5rem" }}>
                <h2 style={{ margin: "0 0 16px", fontSize: 18, color: "#fff" }}>🎬 Generated Reel</h2>
                <div style={{ display: "flex", gap: 20, alignItems: "flex-start", flexWrap: "wrap" }}>
                  <video
                    controls
                    style={{
                      width: 280, borderRadius: 10,
                      border: "1px solid #2a2a2a", background: "#000"
                    }}
                    src={`data:video/mp4;base64,${results.video.video_base64}`}
                  />
                  <div style={{ flex: 1, minWidth: 200 }}>
                    <div style={{ fontSize: 13, color: "#888", marginBottom: 8 }}>
                      Duration: <span style={{ color: "#ddd" }}>{results.video.duration_sec}s</span>
                    </div>
                    <div style={{ fontSize: 13, color: "#888", marginBottom: 16 }}>
                      Scenes: <span style={{ color: "#ddd" }}>{results.video.scenes_used}</span>
                    </div>
                    
                     <a href={`data:video/mp4;base64,${results.video.video_base64}`}
                      download="reel.mp4"
                      style={{
                        display: "inline-block", fontSize: 13, fontWeight: 600,
                        color: "#fff", background: "#6366f1",
                        textDecoration: "none", padding: "8px 20px",
                        borderRadius: 8
                      }}
                    >
                      Download MP4
                    </a>
                  </div>
                </div>
              </div>
            )}

            {/* Virality Score */}
            <div style={{ background: "#1a1a1a", border: "1px solid #2a2a2a", borderRadius: 12, padding: "1.5rem" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
                <h2 style={{ margin: 0, fontSize: 18, color: "#fff" }}>🔮 Virality prediction</h2>
                <div style={{
                  fontSize: 40, fontWeight: 700,
                  color: results.virality.virality_score >= 70 ? "#4ade80"
                    : results.virality.virality_score >= 50 ? "#fbbf24" : "#f87171"
                }}>
                  {results.virality.virality_score}
                  <span style={{ fontSize: 16, color: "#333", fontWeight: 400 }}>/100</span>
                </div>
              </div>
              <p style={{ color: "#888", fontSize: 14, margin: "0 0 16px", lineHeight: 1.6 }}>
                {results.virality.verdict}
              </p>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10, marginBottom: 16 }}>
                <StatBox label="Instagram views" value={results.virality.instagram?.expected_views} />
                <StatBox label="Instagram likes" value={results.virality.instagram?.expected_likes} />
                <StatBox label="LinkedIn views" value={results.virality.linkedin?.expected_views} />
                <StatBox label="LinkedIn likes" value={results.virality.linkedin?.expected_likes} />
              </div>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 14 }}>
                {results.virality.strengths?.map((s, i) => (
                  <span key={i} style={{
                    background: "#052e16", color: "#4ade80", fontSize: 12,
                    padding: "3px 10px", borderRadius: 20, border: "1px solid #14532d"
                  }}>{s}</span>
                ))}
              </div>
              {results.virality.improvement_tips?.length > 0 && (
                <div style={{ marginBottom: 14 }}>
                  <div style={{ fontSize: 12, color: "#444", marginBottom: 8 }}>Tips to improve</div>
                  {results.virality.improvement_tips.map((tip, i) => (
                    <div key={i} style={{ fontSize: 13, color: "#999", marginBottom: 5 }}>
                      <span style={{ color: "#fbbf24" }}>→ </span>{tip}
                    </div>
                  ))}
                </div>
              )}
              <div style={{ fontSize: 12, color: "#444" }}>
                Best time — Instagram: <span style={{ color: "#818cf8" }}>{results.virality.best_time_to_post?.instagram}</span>
                &nbsp;&nbsp;|&nbsp;&nbsp;
                LinkedIn: <span style={{ color: "#818cf8" }}>{results.virality.best_time_to_post?.linkedin}</span>
              </div>
            </div>

            {/* Voiceover + Thumbnail */}
            <div style={{
              display: "grid",
              gridTemplateColumns: results.thumbnail?.image_base64 ? "1fr 1fr" : "1fr",
              gap: "1rem"
            }}>
              <AudioPlayer voiceover={results.voiceover} />
              <ThumbnailCard thumbnail={results.thumbnail} />
            </div>

            {/* B-Roll + Subtitles */}
            <BRollCard
              broll={results.broll}
              subtitles={results.subtitles}
              srt={results.srt}
            />

            {/* Script */}
            <div style={{ background: "#1a1a1a", border: "1px solid #2a2a2a", borderRadius: 12, padding: "1.5rem" }}>
              <h2 style={{ margin: "0 0 16px", fontSize: 18, color: "#fff" }}>✍️ Reel script</h2>
              <Section label="Hook" text={results.script.hook} color="#fbbf24" />
              <Section label="Story" text={results.script.story} color="#60a5fa" />
              <div style={{ marginBottom: 14 }}>
                <div style={{ fontSize: 11, color: "#818cf8", fontWeight: 600, marginBottom: 10, textTransform: "uppercase", letterSpacing: 1 }}>
                  Key insights
                </div>
                {results.script.key_insights?.map((ins, i) => (
                  <div key={i} style={{ display: "flex", gap: 10, marginBottom: 10, alignItems: "flex-start" }}>
                    <span style={{
                      color: "#fff", background: "#4f46e5", borderRadius: 5,
                      width: 22, height: 22, display: "flex", alignItems: "center",
                      justifyContent: "center", fontSize: 11, fontWeight: 700,
                      flexShrink: 0, marginTop: 1
                    }}>{i + 1}</span>
                    <span style={{ fontSize: 14, color: "#ddd", lineHeight: 1.6 }}>{ins}</span>
                  </div>
                ))}
              </div>
              <Section label="CTA" text={results.script.cta} color="#4ade80" />
              <div style={{ marginTop: 14, padding: "14px 16px", background: "#0f0f0f", borderRadius: 8, border: "1px solid #1f1f1f" }}>
                <div style={{ fontSize: 11, color: "#333", marginBottom: 8, textTransform: "uppercase", letterSpacing: 1 }}>Full script</div>
                <div style={{ fontSize: 13, color: "#bbb", lineHeight: 1.9 }}>{results.script.full_script}</div>
              </div>
              <div style={{ marginTop: 10, fontSize: 12, color: "#333" }}>
                {results.script.word_count} words · ~{results.script.estimated_duration_sec} seconds
              </div>
            </div>

            {/* LinkedIn + Instagram */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
              <CaptionCard title="LinkedIn post" icon="in" data={results.linkedin} textKey="post" color="#0a66c2" />
              <CaptionCard title="Instagram caption" icon="ig" data={results.instagram} textKey="caption" color="#e1306c" />
            </div>

            {/* Top trends */}
            <div style={{ background: "#1a1a1a", border: "1px solid #2a2a2a", borderRadius: 12, padding: "1.5rem" }}>
              <h2 style={{ margin: "0 0 16px", fontSize: 18, color: "#fff" }}>📡 Top trends discovered</h2>
              {results.trends?.map((t, i) => (
                <div key={i} style={{
                  display: "flex", alignItems: "center", gap: 12, padding: "10px 0",
                  borderBottom: i < results.trends.length - 1 ? "1px solid #1a1a1a" : "none"
                }}>
                  <div style={{
                    width: 38, height: 38, borderRadius: 8, background: "#1e1b4b",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: 13, fontWeight: 700, color: "#a5b4fc", flexShrink: 0
                  }}>
                    {t.trend_score}
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 13, color: "#ddd", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                      {t.title}
                    </div>
                    <div style={{ fontSize: 11, color: "#333", marginTop: 2 }}>{t.source}</div>
                  </div>
                  {t.ml_signals && (
                    <div style={{ display: "flex", gap: 6, flexShrink: 0 }}>
                      <MiniPill label="velocity" value={t.ml_signals.google_velocity} />
                      <MiniPill label="llm" value={t.ml_signals.llm_score} />
                    </div>
                  )}
                  {t.reason && !t.ml_signals && (
                    <div style={{ fontSize: 11, color: "#444", maxWidth: 160, textAlign: "right", flexShrink: 0, lineHeight: 1.4 }}>
                      {t.reason}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Start over */}
            <div style={{ textAlign: "center", paddingBottom: "2rem" }}>
              <button
                onClick={() => { setResults(null); setTopic(""); setCurrentStep(0) }}
                style={{
                  background: "none", border: "1px solid #2a2a2a",
                  color: "#444", padding: "10px 28px",
                  borderRadius: 10, fontSize: 14, cursor: "pointer"
                }}
              >
                Start over
              </button>
            </div>

          </div>
        )}
      </div>
    </div>
  )
}

function SummaryPill({ label, value, color }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
      <div style={{ fontSize: 10, color: "#333" }}>{label}</div>
      <div style={{ fontSize: 13, fontWeight: 600, color }}>{value}</div>
    </div>
  )
}

function MiniPill({ label, value }) {
  return (
    <div style={{ background: "#1e1b4b", borderRadius: 6, padding: "2px 7px", textAlign: "center" }}>
      <div style={{ fontSize: 9, color: "#555" }}>{label}</div>
      <div style={{ fontSize: 11, color: "#818cf8", fontWeight: 600 }}>{value}</div>
    </div>
  )
}

function StatBox({ label, value }) {
  return (
    <div style={{ background: "#111", borderRadius: 8, padding: "10px 12px" }}>
      <div style={{ fontSize: 11, color: "#333", marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 13, fontWeight: 600, color: "#ddd" }}>{value || "—"}</div>
    </div>
  )
}

function Section({ label, text, color }) {
  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ fontSize: 11, color, fontWeight: 600, marginBottom: 5, textTransform: "uppercase", letterSpacing: 1 }}>
        {label}
      </div>
      <div style={{ fontSize: 14, color: "#ddd", lineHeight: 1.7 }}>{text}</div>
    </div>
  )
}

function CaptionCard({ title, icon, data, textKey, color }) {
  const [copied, setCopied] = useState(false)
  const text = data?.[textKey] || ""
  const hashtags = data?.hashtags || []

  const copy = () => {
    navigator.clipboard.writeText(`${text}\n\n${hashtags.join(" ")}`)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div style={{ background: "#1a1a1a", border: "1px solid #2a2a2a", borderRadius: 12, padding: "1.25rem" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{
            width: 28, height: 28, borderRadius: 6, background: color,
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 11, fontWeight: 700, color: "#fff"
          }}>{icon}</div>
          <span style={{ fontSize: 14, fontWeight: 600, color: "#fff" }}>{title}</span>
        </div>
        <button onClick={copy} style={{
          background: "none",
          border: `1px solid ${copied ? "#4ade80" : "#2a2a2a"}`,
          color: copied ? "#4ade80" : "#555",
          borderRadius: 6, padding: "4px 10px",
          fontSize: 12, cursor: "pointer", transition: "all 0.2s"
        }}>
          {copied ? "✓ Copied!" : "Copy"}
        </button>
      </div>
      <div style={{
        fontSize: 13, color: "#bbb", lineHeight: 1.7, marginBottom: 10,
        whiteSpace: "pre-wrap", maxHeight: 180, overflowY: "auto"
      }}>
        {text}
      </div>
      {data?.engagement_hook && (
        <div style={{ fontSize: 12, color: "#fbbf24", marginBottom: 10, fontStyle: "italic" }}>
          "{data.engagement_hook}"
        </div>
      )}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
        {hashtags.slice(0, 8).map((h, i) => (
          <span key={i} style={{
            fontSize: 11, color: "#818cf8", background: "#1e1b4b",
            padding: "2px 8px", borderRadius: 20
          }}>{h}</span>
        ))}
      </div>
    </div>
  )
}

function AudioPlayer({ voiceover }) {
  if (!voiceover) return null
  const src = `data:audio/mp3;base64,${voiceover.audio_base64}`
  return (
    <div style={{ background: "#1a1a1a", border: "1px solid #2a2a2a", borderRadius: 12, padding: "1.25rem" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
        <div style={{
          width: 28, height: 28, borderRadius: 6, background: "#4f46e5",
          display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14
        }}>🎙️</div>
        <span style={{ fontSize: 14, fontWeight: 600, color: "#fff" }}>AI voiceover</span>
        <span style={{ fontSize: 11, color: "#333", marginLeft: "auto" }}>
          {voiceover.char_count} chars · {voiceover.voice}
        </span>
      </div>
      <audio controls style={{ width: "100%", accentColor: "#6366f1" }} src={src} />
      <a href={src} download="voiceover.mp3" style={{
        display: "inline-block", marginTop: 10, fontSize: 12,
        color: "#818cf8", textDecoration: "none",
        border: "1px solid #3730a3", padding: "4px 12px", borderRadius: 6
      }}>
        Download MP3
      </a>
    </div>
  )
}

function ThumbnailCard({ thumbnail }) {
  if (!thumbnail || !thumbnail.image_base64) return null
  const src = `data:image/jpeg;base64,${thumbnail.image_base64}`
  return (
    <div style={{ background: "#1a1a1a", border: "1px solid #2a2a2a", borderRadius: 12, padding: "1.25rem" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
        <div style={{
          width: 28, height: 28, borderRadius: 6, background: "#7c3aed",
          display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14
        }}>🖼️</div>
        <span style={{ fontSize: 14, fontWeight: 600, color: "#fff" }}>AI thumbnail</span>
      </div>
      <div style={{ display: "flex", gap: 14, alignItems: "flex-start" }}>
        <img src={src} alt="Generated thumbnail" style={{
          width: 110, borderRadius: 8, border: "1px solid #2a2a2a", flexShrink: 0
        }} />
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 11, color: "#333", marginBottom: 6 }}>Prompt used</div>
          <div style={{ fontSize: 12, color: "#777", lineHeight: 1.6 }}>{thumbnail.prompt_used}</div>
          <a href={src} download="thumbnail.jpg" style={{
            display: "inline-block", marginTop: 12, fontSize: 12,
            color: "#a78bfa", textDecoration: "none",
            border: "1px solid #5b21b6", padding: "4px 12px", borderRadius: 6
          }}>
            Download
          </a>
        </div>
      </div>
    </div>
  )
}

function BRollCard({ broll, subtitles, srt }) {
  const [showSrt, setShowSrt] = useState(false)

  const downloadSrt = () => {
    const blob = new Blob([srt], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "subtitles.srt"
    a.click()
    URL.revokeObjectURL(url)
  }

  if (!broll?.length && !subtitles?.length) return null

  return (
    <div style={{ background: "#1a1a1a", border: "1px solid #2a2a2a", borderRadius: 12, padding: "1.5rem" }}>
      <h2 style={{ margin: "0 0 16px", fontSize: 18, color: "#fff" }}>🎞️ B-Roll + Subtitles</h2>

      {broll?.length > 0 && (
        <div style={{ marginBottom: 20 }}>
          <div style={{ fontSize: 11, color: "#444", marginBottom: 10, textTransform: "uppercase", letterSpacing: 1 }}>
            B-Roll scenes ({broll.length})
          </div>
          <div style={{ display: "flex", gap: 10, overflowX: "auto", paddingBottom: 8 }}>
            {broll.map((scene, i) => (
              <div key={i} style={{ flexShrink: 0, textAlign: "center" }}>
                <img
                  src={`data:image/jpeg;base64,${scene.image_base64}`}
                  alt={`Scene ${scene.scene}`}
                  style={{
                    width: 85, height: 150, objectFit: "cover",
                    borderRadius: 8, border: "1px solid #2a2a2a", display: "block"
                  }}
                />
                <div style={{ fontSize: 10, color: "#444", marginTop: 5 }}>Scene {scene.scene}</div>
                <div style={{ fontSize: 10, color: "#333" }}>{scene.duration_sec}s</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {subtitles?.length > 0 && (
        <div>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
            <div style={{ fontSize: 11, color: "#444", textTransform: "uppercase", letterSpacing: 1 }}>
              Subtitles ({subtitles.length} lines)
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <button
                onClick={() => setShowSrt(!showSrt)}
                style={{
                  background: "none", border: "1px solid #2a2a2a",
                  color: "#555", borderRadius: 6, padding: "4px 10px",
                  fontSize: 11, cursor: "pointer"
                }}
              >
                {showSrt ? "Hide SRT" : "View SRT"}
              </button>
              <button
                onClick={downloadSrt}
                style={{
                  background: "none", border: "1px solid #3730a3",
                  color: "#818cf8", borderRadius: 6, padding: "4px 10px",
                  fontSize: 11, cursor: "pointer"
                }}
              >
                Download .srt
              </button>
            </div>
          </div>

          {showSrt ? (
            <pre style={{
              background: "#0f0f0f", borderRadius: 8, padding: "12px 14px",
              fontSize: 11, color: "#666", lineHeight: 1.8,
              maxHeight: 220, overflowY: "auto",
              fontFamily: "monospace", whiteSpace: "pre-wrap"
            }}>
              {srt}
            </pre>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 5, maxHeight: 180, overflowY: "auto" }}>
              {subtitles.slice(0, 8).map((s, i) => (
                <div key={i} style={{ display: "flex", gap: 12, fontSize: 12, alignItems: "flex-start" }}>
                  <span style={{ color: "#333", flexShrink: 0, fontFamily: "monospace", marginTop: 1 }}>
                    {s.start_fmt?.split(",")[0]}
                  </span>
                  <span style={{ color: "#bbb", lineHeight: 1.5 }}>{s.text}</span>
                </div>
              ))}
              {subtitles.length > 8 && (
                <div style={{ fontSize: 11, color: "#333", paddingTop: 4 }}>
                  +{subtitles.length - 8} more lines
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}