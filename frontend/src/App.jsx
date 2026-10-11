
import { useCallback, useEffect, useState } from "react";
import {
  ArrowDownRight,
  ArrowRight,
  Check,
  Clock3,
  Compass,
  Leaf,
  LoaderCircle,
  MapPin,
  NotebookPen,
  RefreshCw,
  Sparkles,
  Sprout,
  Wind,
} from "lucide-react";

import {
  generateQuest,
  getObservations,
  saveObservation,
} from "./api";

import "./App.css";

const initialPreferences = {
  environment: "Garden",
  minutes: 10,
  interest: "Biodiversity",
};

const environments = [
  "Garden",
  "College campus",
  "Park",
  "Neighbourhood",
];

const interests = [
  "Biodiversity",
  "Plants",
  "Sounds",
  "Observation and mindfulness",
];

function App() {
  const [preferences, setPreferences] = useState(initialPreferences);
  const [mission, setMission] = useState(null);
  const [source, setSource] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [observation, setObservation] = useState("");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [journal, setJournal] = useState([]);
  const [journalError, setJournalError] = useState("");

  const loadJournal = useCallback(async () => {
    try {
      const data = await getObservations();
      setJournal(data.observations);
      setJournalError("");
    } catch {
      setJournalError("Could not load your local journal.");
    }
  }, []);

  useEffect(() => {
    loadJournal();
  }, [loadJournal]);

  function updatePreference(key, value) {
    setPreferences((current) => ({
      ...current,
      [key]: value,
    }));
  }

  async function handleGenerate(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");
    setObservation("");

    try {
      const data = await generateQuest(preferences);
      setMission(data.mission);
      setSource(data.source);
    } catch (err) {
      setError(
        err.message ||
          "Couldn't reach OutsideIn. Check that the Python API is running."
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleSave(event) {
    event.preventDefault();

    if (!observation.trim() || !mission) return;

    setSaving(true);
    setMessage("");

    try {
      await saveObservation(mission.title, observation);
      setObservation("");
      setMessage("Observation saved to your local journal.");
      await loadJournal();
    } catch (err) {
      setMessage(err.message || "Could not save your observation.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#home" aria-label="OutsideIn home">
          <span className="brand-mark">
            <Sprout size={23} strokeWidth={1.8} />
          </span>
          <span>outside<span className="brand-light">in</span></span>
        </a>

        <nav className="navigation" aria-label="Main navigation">
          <a href="#discover">Discover</a>
          <a href="#journal">My journal</a>
        </nav>

        <a className="topbar-note" href="#discover">
          <span className="status-dot" />
          Your next little adventure
        </a>
      </header>

      <main id="home">
        <section className="hero">
          <div className="hero-copy">
            <div className="eyebrow">
              <span className="eyebrow-line" />
              A DIFFERENT KIND OF AI
            </div>

            <h1>
              The world is
              <br />
              <span>waiting for you.</span>
            </h1>

            <p className="hero-description">
              Small adventures. Real discoveries. Let a little AI inspiration
              take you somewhere beyond your screen.
            </p>

            <a className="hero-link" href="#discover">
              Find your next quest
              <ArrowDownRight size={18} />
            </a>

            <div className="hero-note">
              <Leaf size={16} />
              Made for curious minds and open skies.
            </div>
          </div>

          <div className="hero-visual">
            <div className="hero-image" role="img" aria-label="Sunlight falling on green leaves">
              <div className="image-label">
                <span className="image-label-icon">
                  <Wind size={16} />
                </span>
                <span>
                  <strong>Take a breath.</strong>
                  <small>Step into the moment.</small>
                </span>
              </div>
            </div>

            <div className="floating-note">
              <Sparkles size={17} />
              <span>A little wonder goes a long way.</span>
            </div>

            <div className="hero-number">01 / GO OUTSIDE</div>
          </div>
        </section>

        <section className="discover-section" id="discover">
          <div className="section-heading">
            <div>
              <div className="eyebrow">
                <span className="eyebrow-line" />
                YOUR MOMENT OUTSIDE
              </div>
              <h2>Find your kind of wonder.</h2>
              <p>Tell us what you have in mind. We'll help you get started.</p>
            </div>
            <div className="section-icon">
              <Compass size={27} strokeWidth={1.4} />
            </div>
          </div>

          <div className="workspace">
            <form className="preferences-card" onSubmit={handleGenerate}>
              <div className="card-overline">
                <span>01</span>
                BUILD YOUR QUEST
              </div>

              <label htmlFor="environment">
                <MapPin size={17} />
                Where are you exploring?
              </label>
              <select
                id="environment"
                value={preferences.environment}
                onChange={(event) =>
                  updatePreference("environment", event.target.value)
                }
              >
                {environments.map((environment) => (
                  <option key={environment} value={environment}>
                    {environment}
                  </option>
                ))}
              </select>

              <label htmlFor="minutes">
                <Clock3 size={17} />
                How much time do you have?
              </label>
              <div className="duration-options">
                {[5, 10, 15, 20].map((minutes) => (
                  <button
                    className={
                      preferences.minutes === minutes
                        ? "duration-option selected"
                        : "duration-option"
                    }
                    type="button"
                    key={minutes}
                    onClick={() => updatePreference("minutes", minutes)}
                    aria-pressed={preferences.minutes === minutes}
                  >
                    {minutes}
                    <span>min</span>
                  </button>
                ))}
              </div>

              <label htmlFor="interest">
                <Leaf size={17} />
                What catches your curiosity?
              </label>
              <select
                id="interest"
                value={preferences.interest}
                onChange={(event) =>
                  updatePreference("interest", event.target.value)
                }
              >
                {interests.map((interest) => (
                  <option key={interest} value={interest}>
                    {interest}
                  </option>
                ))}
              </select>

              <button
                className="primary-button generate-button"
                type="submit"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <LoaderCircle className="spin" size={19} />
                    Finding your quest...
                  </>
                ) : (
                  <>
                    <Sparkles size={18} />
                    Find my nature quest
                    <ArrowRight size={18} />
                  </>
                )}
              </button>

              <p className="privacy-note">
                <Leaf size={13} />
                Local AI. Personal discoveries. No account needed.
              </p>
            </form>

            <div className="mission-area" aria-live="polite">
              {!mission && !loading && (
                <div className="empty-state">
                  <div className="empty-icon">
                    <Sprout size={34} strokeWidth={1.3} />
                  </div>
                  <span className="empty-overline">A LITTLE SOMETHING AWAITS</span>
                  <h3>Your next discovery<br />starts here.</h3>
                  <p>
                    Choose your preferences and let OutsideIn create a small
                    mission for your time outdoors.
                  </p>
                  <div className="empty-footer">
                    <span>Curiosity is enough.</span>
                    <Leaf size={17} />
                  </div>
                </div>
              )}

              {loading && (
                <div className="empty-state loading-state">
                  <LoaderCircle className="spin" size={34} />
                  <h3>Finding your wonder...</h3>
                  <p>Your next little adventure is taking shape.</p>
                </div>
              )}

              {error && (
                <div className="alert error-alert" role="alert">
                  <strong>We couldn't generate your quest.</strong>
                  <p>{error}</p>
                  <button
                    className="text-button"
                    onClick={handleGenerate}
                    type="button"
                  >
                    <RefreshCw size={15} />
                    Try again
                  </button>
                </div>
              )}

              {mission && !loading && (
                <article className="mission-card">
                  <div className="mission-topline">
                    <span className="mission-badge">
                      <Sparkles size={14} />
                      YOUR QUEST
                    </span>
                    <span className="mission-duration">
                      <Clock3 size={14} />
                      {mission.duration_minutes} min
                    </span>
                  </div>

                  <div className="mission-title-wrap">
                    <span className="mission-kicker">A MOMENT OF DISCOVERY</span>
                    <h3>{mission.title}</h3>
                    <p>{mission.mission}</p>
                  </div>

                  <div className="mission-steps">
                    <h4>Your little plan</h4>
                    {mission.steps.map((step, index) => (
                      <div className="mission-step" key={`${index}-${step}`}>
                        <span className="step-number">
                          {String(index + 1).padStart(2, "0")}
                        </span>
                        <p>{step}</p>
                      </div>
                    ))}
                  </div>

                  <div className="reflection-card">
                    <span>WHEN YOU RETURN</span>
                    <p>{mission.reflection_question}</p>
                  </div>

                  <div className="safety-note">
                    <Leaf size={16} />
                    <p>{mission.safety_note}</p>
                  </div>

                  <div className="mission-footer">
                    <span className="source-label">
                      <span className="status-dot" />
                      {source}
                    </span>
                    <span className="mission-footer-note">
                      Time to step away.
                    </span>
                  </div>
                </article>
              )}
            </div>
          </div>
        </section>

        {mission && (
          <section className="observation-section">
            <div className="observation-intro">
              <span className="eyebrow">AFTER YOUR ADVENTURE</span>
              <h2>What did you notice?</h2>
              <p>
                Step outside first. When you return, save a detail worth
                remembering.
              </p>
            </div>

            <form className="observation-form" onSubmit={handleSave}>
              <label htmlFor="observation">Your field notes</label>
              <textarea
                id="observation"
                value={observation}
                onChange={(event) => setObservation(event.target.value)}
                placeholder="I noticed something interesting..."
                maxLength={2000}
                required
              />
              <div className="observation-form-footer">
                <span>{observation.length}/2000 characters</span>
                <button
                  className="primary-button"
                  type="submit"
                  disabled={saving || !observation.trim()}
                >
                  {saving ? (
                    <LoaderCircle className="spin" size={17} />
                  ) : (
                    <Check size={17} />
                  )}
                  {saving ? "Saving..." : "Save observation"}
                </button>
              </div>
              {message && (
                <p className="form-message" role="status">
                  {message}
                </p>
              )}
            </form>
          </section>
        )}

        <section className="journal-section" id="journal">
          <div className="journal-heading">
            <div>
              <div className="eyebrow">
                <span className="eyebrow-line" />
                YOUR LITTLE COLLECTION
              </div>
              <h2>The things you noticed.</h2>
              <p>A growing journal of moments from the world outside.</p>
            </div>
            <div className="journal-icon">
              <NotebookPen size={26} strokeWidth={1.4} />
            </div>
          </div>

          {journalError && (
            <div className="alert error-alert" role="alert">
              {journalError}
              <button className="text-button" onClick={loadJournal}>
                Retry
              </button>
            </div>
          )}

          {journal.length === 0 ? (
            <div className="journal-empty">
              <Leaf size={23} />
              <p>Your journal is waiting for its first discovery.</p>
            </div>
          ) : (
            <div className="journal-grid">
              {[...journal].reverse().map((entry, index) => (
                <article
                  className="journal-entry"
                  key={`${entry.completed_at}-${index}`}
                >
                  <div className="journal-entry-top">
                    <Leaf size={18} />
                    <span>
                      {entry.completed_at
                        ? new Date(entry.completed_at).toLocaleDateString(
                            undefined,
                            {
                              day: "numeric",
                              month: "short",
                              year: "numeric",
                            }
                          )
                        : "Nature notes"}
                    </span>
                  </div>
                  <h3>{entry.mission_title}</h3>
                  <p>{entry.observation}</p>
                </article>
              ))}
            </div>
          )}
        </section>
      </main>

      <footer className="site-footer">
        <a className="brand footer-brand" href="#home">
          <span className="brand-mark">
            <Sprout size={20} />
          </span>
          <span>outside<span className="brand-light">in</span></span>
        </a>
        <p>Built for the moments beyond the screen.</p>
        <a href="#home" className="back-to-top">
          Back to the beginning ↑
        </a>
      </footer>
    </div>
  );
}

export default App;
