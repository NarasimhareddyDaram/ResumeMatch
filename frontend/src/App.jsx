import { useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

function App() {
  const [resume, setResume] = useState("");
  const [job, setJob] = useState("");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [search, setSearch] = useState("");
  const [showHistory, setShowHistory] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function uploadResumePdf(e) {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Please select a PDF file.");
      e.target.value = "";
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    setError("");

    try {
      const response = await fetch(`${API}/upload-pdf`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "PDF upload failed.");
      }

      setResume(data.resume_text);
      setError("");
    } catch (err) {
      setError(err.message || "Could not upload PDF.");
    } finally {
      e.target.value = "";
    }
  }

  async function analyzeResume(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resume_text: resume,
          job_description: job,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Analysis failed. Please check your inputs."
        );
      }

      setResult(data);

      if (showHistory) {
        await loadHistory();
      }
    } catch (err) {
      setError(err.message || "Could not analyze. Check that FastAPI is running.");
    } finally {
      setLoading(false);
    }
  }

  async function loadHistory(term = search) {
    setError("");

    try {
      const response = await fetch(
        `${API}/analyses?search=${encodeURIComponent(term)}`
      );

      if (!response.ok) {
        throw new Error("History request failed.");
      }

      setHistory(await response.json());
      setShowHistory(true);
    } catch {
      setError("Could not load history. Check the backend.");
    }
  }


async function viewAnalysisDetails(id) {
  setError("");
  console.log("View Details clicked. Analysis ID:", id);

  try {
    const response = await fetch(`${API}/analyses/${id}`);
    console.log("API response status:", response.status);

    const data = await response.json();
    console.log("Analysis details received:", data);

    if (!response.ok) {
      throw new Error(
        data.detail || "Could not load analysis details."
      );
    }

    if (!data.resume_text || !data.job_description) {
      throw new Error("Resume or job description is missing.");
    }

    setSelectedAnalysis(data);
    console.log("Selected analysis updated:", data.id);
  } catch (err) {
    console.error("View Details error:", err);
    setError(err.message || "Could not load analysis details.");
  }
}


  function downloadAnalysis(item) {
    const report = `
ResumeMatch AI - Analysis Report
================================

Analysis ID: ${item.id}
Match Score: ${item.match_score}%

Matched Skills:
${item.matched_skills.join(", ") || "None"}

Missing Skills:
${item.missing_skills.join(", ") || "None"}

Recommendations:
${(item.recommendations || [])
  .map((recommendation, index) => `${index + 1}. ${recommendation}`)
  .join("\n") || "None"}
`;

    const blob = new Blob([report], {
      type: "text/plain;charset=utf-8",
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = `resumematch-analysis-${item.id}.txt`;

    document.body.appendChild(link);
    link.click();
    link.remove();

    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  async function deleteAnalysis(id) {
    if (!window.confirm(`Delete analysis ${id}?`)) return;

    try {
      const response = await fetch(`${API}/analyses/${id}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Delete failed.");
      }

      if (selectedAnalysis?.id === id) {
        setSelectedAnalysis(null);
      }

      await loadHistory();
    } catch {
      setError("Could not delete this analysis.");
    }
  }

  return (
    <main className="container">
     <header>
        <h1>ResumeMatch</h1>
        <p>Resume Analyzer & Job Matcher</p>
        <p>Analyze your resume against your target job description.</p>
     </header>

      <form onSubmit={analyzeResume}>
        <label>Upload Resume PDF</label>
        <input
          type="file"
          accept=".pdf,application/pdf"
          onChange={uploadResumePdf}
        />

        <p>Or paste your resume text below.</p>

        <label>Resume Text</label>
        <textarea
          value={resume}
          onChange={(e) => setResume(e.target.value)}
          placeholder="Paste your resume text here..."
          required
        />

        <label>Job Description</label>
        <textarea
          value={job}
          onChange={(e) => setJob(e.target.value)}
          placeholder="Paste the job description here..."
          required
        />

        <button type="submit" disabled={loading}>
          {loading ? "Analyzing..." : "Analyze Resume"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <section className="results">
          <h2>Match Score: {result.match_score}%</h2>

          <p>
            <strong>Matched Skills:</strong>{" "}
            {result.matched_skills.join(", ") || "None"}
          </p>

          <p>
            <strong>Missing Skills:</strong>{" "}
            {result.missing_skills.join(", ") || "None"}
          </p>

          <h3>Recommendations</h3>
          <ul>
            {result.recommendations?.map((item, index) => (
              <li key={index} style={{ marginBottom: "12px" }}>
                {item}
              </li>
            ))}
          </ul>

          <p>{result.message}</p>
        </section>
      )}

      <section className="results">
        <h2>Analysis History</h2>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            loadHistory(search);
          }}
        >
          <label>Search saved analyses</label>
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search resume or job text..."
          />

          <button type="submit">Search History</button>
        </form>

        <button type="button" onClick={() => loadHistory("")}>
          View All History
        </button>

        {showHistory && history.length === 0 && (
          <p>No analyses found.</p>
        )}

        {history.map((item) => (
          <article key={item.id} className="history-item">
            <h3>Analysis #{item.id}</h3>

            <p>
              <strong>Score:</strong> {item.match_score}%
            </p>

            <p>
              <strong>Matched:</strong>{" "}
              {item.matched_skills.join(", ") || "None"}
            </p>

            <p>
              <strong>Missing:</strong>{" "}
              {item.missing_skills.join(", ") || "None"}
            </p>

            <p><strong>Recommendations:</strong></p>
            <ul>
              {item.recommendations?.map((recommendation, index) => (
                <li key={index} style={{ marginBottom: "8px" }}>
                  {recommendation}
                </li>
              ))}
            </ul>

                      <button
                type="button"
                onClick={() => viewAnalysisDetails(item.id)}
              >
                View Details
              </button>
            <button
              type="button"
              onClick={() => downloadAnalysis(item)}
            >
              Download Report
            </button>

            <button
              type="button"
              onClick={() => deleteAnalysis(item.id)}
            >
              Delete Analysis
            </button>
          </article>
        ))}

        {selectedAnalysis && (
          <article className="history-item">
            <h2>Analysis Details #{selectedAnalysis.id}</h2>

            <h3>Original Resume</h3>
            <pre
              style={{
                whiteSpace: "pre-wrap",
                overflowWrap: "anywhere",
              }}
            >
              {selectedAnalysis.resume_text}
            </pre>

            <h3>Original Job Description</h3>
            <pre
              style={{
                whiteSpace: "pre-wrap",
                overflowWrap: "anywhere",
              }}
            >
              {selectedAnalysis.job_description}
            </pre>

            <button
              type="button"
              onClick={() => setSelectedAnalysis(null)}
            >
              Close Details
            </button>
          </article>
        )}
      </section>
    </main>
  );
}

export default App;
