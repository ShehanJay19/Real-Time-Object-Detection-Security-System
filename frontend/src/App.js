import './App.css';
import { useCallback, useEffect, useMemo, useState } from 'react';

const REFRESH_MS = 4000;
const AUTH_TOKEN_KEY = 'securitySystemOwnerToken';

function formatTime(value) {
  if (!value) {
    return 'Unknown';
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return parsed.toLocaleString();
}

function normalizeObjects(value) {
  if (Array.isArray(value)) {
    return value.join(', ');
  }
  return String(value ?? 'unknown');
}

function App() {
  const [authToken, setAuthToken] = useState(() => localStorage.getItem(AUTH_TOKEN_KEY) || '');
  const [authLoading, setAuthLoading] = useState(true);
  const [loginForm, setLoginForm] = useState({ username: '', password: '' });
  const [loginSubmitting, setLoginSubmitting] = useState(false);
  const [loginError, setLoginError] = useState('');
  const [owner, setOwner] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [logs, setLogs] = useState([]);
  const [cameraStatus, setCameraStatus] = useState({ running: false, last_error: '', selected_camera_index: 0 });
  const [cameraOptions, setCameraOptions] = useState([]);
  const [selectedCamera, setSelectedCamera] = useState(0);
  const [loading, setLoading] = useState(true);
  const [startingCamera, setStartingCamera] = useState(false);
  const [switchingCamera, setSwitchingCamera] = useState(false);
  const [error, setError] = useState('');
  const [lastUpdated, setLastUpdated] = useState('');
  const [selectedObject, setSelectedObject] = useState('all');
  const [timeWindow, setTimeWindow] = useState('all');

  const objectOptions = useMemo(() => {
    const unique = new Set();
    [...alerts, ...logs].forEach((entry) => {
      const value = normalizeObjects(entry.objects ?? entry.object).trim().toLowerCase();
      if (value) {
        unique.add(value);
      }
    });
    return Array.from(unique).sort();
  }, [alerts, logs]);

  const topThreats = useMemo(() => {
    const counts = {};
    alerts.forEach((entry) => {
      const key = normalizeObjects(entry.objects ?? entry.object).toLowerCase();
      counts[key] = (counts[key] ?? 0) + 1;
    });

    return Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([name, count]) => ({ name, count }));
  }, [alerts]);

  const fetchJson = useCallback(async (path, options = {}) => {
    const headers = new Headers(options.headers || {});
    if (authToken) {
      headers.set('Authorization', `Bearer ${authToken}`);
    }

    const response = await fetch(path, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const message = await response.text();
      throw new Error(message || `${path} failed with ${response.status}`);
    }
    return response.json();
  }, [authToken]);

  const validateSession = useCallback(async () => {
    if (!authToken) {
      setOwner(null);
      setAuthLoading(false);
      return;
    }

    try {
      const session = await fetchJson('/auth/me');
      setOwner(session.owner || session.user || null);
      setAuthLoading(false);
    } catch {
      localStorage.removeItem(AUTH_TOKEN_KEY);
      setAuthToken('');
      setOwner(null);
      setAuthLoading(false);
    }
  }, [authToken, fetchJson]);

  async function handleLogin(event) {
    event.preventDefault();
    setLoginSubmitting(true);
    setLoginError('');

    try {
      const response = await fetch('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginForm),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Login failed');
      }

      localStorage.setItem(AUTH_TOKEN_KEY, data.access_token);
      setAuthToken(data.access_token);
      setOwner(data.owner || data.user || null);
      setLoginForm({ username: '', password: '' });
    } catch (loginFailure) {
      setLoginError(loginFailure.message);
    } finally {
      setLoginSubmitting(false);
    }
  }

  function handleLogout() {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    setAuthToken('');
    setOwner(null);
    setAlerts([]);
    setLogs([]);
    setCameraOptions([]);
    setCameraStatus({ running: false, last_error: '', selected_camera_index: 0 });
  }

  const refreshData = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (selectedObject !== 'all') {
        params.set('object_name', selectedObject);
      }
      if (timeWindow !== 'all') {
        params.set('minutes', timeWindow);
      }
      const query = params.toString();
      const querySuffix = query ? `?${query}` : '';

      const [alertsData, logsData, cameraData, camerasData] = await Promise.all([
        fetchJson(`/alerts${querySuffix}`),
        fetchJson(`/logs${querySuffix}`),
        fetchJson('/camera-status'),
        fetchJson('/cameras'),
      ]);
      setAlerts(Array.isArray(alertsData.alerts) ? alertsData.alerts : []);
      setLogs(Array.isArray(logsData.logs) ? logsData.logs : []);
      const normalizedCameraStatus = cameraData && typeof cameraData === 'object'
        ? cameraData
        : { running: false, last_error: '', selected_camera_index: 0 };
      setCameraStatus(normalizedCameraStatus);
      const cameras = Array.isArray(camerasData.cameras) ? camerasData.cameras : [];
      setCameraOptions(cameras);
      setSelectedCamera(normalizedCameraStatus.selected_camera_index ?? 0);
      setError('');
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (refreshError) {
      setError(refreshError.message);
    } finally {
      setLoading(false);
    }
  }, [fetchJson, selectedObject, timeWindow]);

  async function handleStartCamera() {
    setStartingCamera(true);
    try {
      await fetchJson('/start-camera');
      await refreshData();
      setError('');
    } catch (cameraError) {
      setError(cameraError.message);
    } finally {
      setStartingCamera(false);
    }
  }

  async function handleSelectCamera(event) {
    const nextIndex = Number(event.target.value);
    setSelectedCamera(nextIndex);
    setSwitchingCamera(true);
    try {
      const result = await fetchJson(`/select-camera?index=${nextIndex}`);
      if (result.ok === false) {
        throw new Error(result.message || 'Failed to switch camera');
      }
      await refreshData();
      setError('');
    } catch (cameraError) {
      setError(cameraError.message);
    } finally {
      setSwitchingCamera(false);
    }
  }

  async function handleRefreshCameras() {
    setSwitchingCamera(true);
    try {
      await fetchJson('/debug/cameras');
      await refreshData();
      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setSwitchingCamera(false);
    }
  }

  useEffect(() => {
    validateSession();
  }, [validateSession]);

  useEffect(() => {
    if (!authToken || authLoading) {
      return undefined;
    }

    refreshData();
    const timer = setInterval(refreshData, REFRESH_MS);
    return () => clearInterval(timer);
  }, [authToken, authLoading, refreshData]);

  if (authLoading) {
    return (
      <div className="app-shell login-shell">
        <div className="ambient ambient-a" />
        <div className="ambient ambient-b" />
        <main className="login-screen">
          <section className="panel login-panel">
            <p className="eyebrow">Real-Time Object Detection Security System</p>
            <h1>Loading secure access...</h1>
            <p className="intro">Verifying the owner session before opening the dashboard.</p>
          </section>
        </main>
      </div>
    );
  }

  if (!authToken || !owner) {
    return (
      <div className="app-shell login-shell">
        <div className="ambient ambient-a" />
        <div className="ambient ambient-b" />
        <main className="login-screen">
          <section className="panel login-panel reveal">
            <p className="eyebrow">Owner Access</p>
            <h1>Login to open the live security console</h1>
            <p className="intro">
              This system is protected. Use the owner credentials to access the camera and alert dashboard.
            </p>

            <form className="login-form" onSubmit={handleLogin}>
              <label className="control">
                <span>Owner username</span>
                <input
                  className="text-input"
                  type="text"
                  value={loginForm.username}
                  onChange={(event) => setLoginForm((current) => ({ ...current, username: event.target.value }))}
                  placeholder="owner"
                  autoComplete="username"
                  required
                />
              </label>

              <label className="control">
                <span>Password</span>
                <input
                  className="text-input"
                  type="password"
                  value={loginForm.password}
                  onChange={(event) => setLoginForm((current) => ({ ...current, password: event.target.value }))}
                  placeholder="Enter owner password"
                  autoComplete="current-password"
                  required
                />
              </label>

              {loginError && <p className="login-error">{loginError}</p>}

              <button className="primary-btn login-btn" type="submit" disabled={loginSubmitting}>
                {loginSubmitting ? 'Signing in...' : 'Open Secure Dashboard'}
              </button>
            </form>
          </section>
        </main>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <div className="ambient ambient-a" />
      <div className="ambient ambient-b" />
      <main className="dashboard">
        <header className="hero reveal">
          <div className="hero-copy">
            <p className="eyebrow">Real-Time Object Detection Security System</p>
            <h1>Live Threat Stream</h1>
            <p className="intro">
              Keep the camera feed front and center while alerts stay visible in a focused log.
            </p>
          </div>
          <div className="hero-badge panel">
            <span className="badge-copy">{owner?.username ? `Owner: ${owner.username}` : 'Owner signed in'}</span>
            <span className="badge-meta">Updated {lastUpdated || 'just now'}</span>
          </div>
        </header>

        {error && (
          <section className="panel error-panel reveal">
            <strong>Connection Error:</strong> {error}
          </section>
        )}

        <section className="stats-grid reveal stagger-1">
          <article className="panel stat-card">
            <p className="stat-label">Total Alerts</p>
            <p className="stat-value">{alerts.length}</p>
          </article>
          <article className="panel stat-card">
            <p className="stat-label">Event Logs</p>
            <p className="stat-value">{logs.length}</p>
          </article>
          <article className="panel stat-card">
            <p className="stat-label">Top Threat</p>
            <p className="stat-value small">
              {topThreats[0] ? `${topThreats[0].name} (${topThreats[0].count})` : 'N/A'}
            </p>
          </article>
          <article className="panel stat-card">
            <p className="stat-label">Camera</p>
            <p className={`stat-value small ${cameraStatus.running ? 'ok' : 'warn'}`}>
              {cameraStatus.running ? 'Running' : 'Idle'}
            </p>
          </article>
        </section>

        <section className="stream-layout reveal stagger-2">
          <article className="panel live-panel">
            <div className="panel-head live-head">
              <div>
                <p className="section-kicker">Primary View</p>
                <h2>Live Camera Stream</h2>
              </div>
              <span className="pill">MJPEG feed</span>
            </div>
            <div className="live-frame-wrap">
              {cameraStatus.running ? (
                <img
                  className="live-frame"
                  src={`/video-feed?camera=${selectedCamera}&token=${encodeURIComponent(authToken)}&t=${Date.now()}`}
                  alt="Live camera stream"
                />
              ) : (
                <div className="empty live-empty">
                  Select a camera below, then start live streaming.
                </div>
              )}
            </div>

            <section className="panel camera-panel">
              <div className="panel-head">
                <div>
                  <p className="section-kicker">Camera Control</p>
                  <h2>Select Source</h2>
                </div>
                <span className="pill">Below stream</span>
              </div>
              <div className="camera-controls">
                <label className="control camera-control">
                  <span>Camera Source</span>
                  <select
                    id="cameraSelect"
                    className="camera-select"
                    value={selectedCamera}
                    onChange={handleSelectCamera}
                    disabled={cameraStatus.running || switchingCamera || cameraOptions.length === 0}
                  >
                    {cameraOptions.length === 0 && <option value={0}>No camera detected</option>}
                    {cameraOptions.map((camera) => (
                      <option key={camera.index} value={camera.index}>
                        {camera.name}
                        {camera.index === selectedCamera ? ' (selected)' : ''}
                      </option>
                    ))}
                  </select>
                </label>

                <div className="camera-action-row">
                  <button
                    className="ghost-btn"
                    type="button"
                    onClick={handleRefreshCameras}
                    disabled={switchingCamera}
                  >
                    {switchingCamera ? 'Scanning cameras...' : 'Refresh Cameras'}
                  </button>

                  <button
                    className="primary-btn"
                    type="button"
                    onClick={handleStartCamera}
                    disabled={startingCamera || cameraStatus.running || cameraOptions.length === 0}
                  >
                    {cameraStatus.running
                      ? 'Camera Running'
                      : startingCamera
                        ? 'Starting camera...'
                        : 'Start Live Camera'}
                  </button>

                  <button className="ghost-btn" type="button" onClick={refreshData}>
                    Refresh Now
                  </button>
                  <button className="ghost-btn" type="button" onClick={handleLogout}>
                    Logout
                  </button>
                </div>

                {cameraOptions.length === 0 && (
                  <div className="camera-help">
                    <p>💡 Troubleshooting:</p>
                    <ul>
                      <li>Ensure GlideX app is open and camera is connected</li>
                      <li>Check that no other app is using the camera</li>
                      <li>Try clicking "Refresh Cameras" below</li>
                      <li>Check the backend console for detailed diagnostics</li>
                    </ul>
                  </div>
                )}

                {cameraStatus.last_error && (
                  <p className="camera-error">Camera error: {cameraStatus.last_error}</p>
                )}
              </div>
            </section>
          </article>

          <article className="panel alerts-panel">
            <div className="panel-head">
              <div>
                <p className="section-kicker">Alert Feed</p>
                <h2>Recent Alerts Only</h2>
              </div>
              <span className="pill danger">Critical feed</span>
            </div>
            <div className="filters-grid compact-filters">
              <label className="control">
                <span>Object Type</span>
                <select
                  value={selectedObject}
                  onChange={(event) => setSelectedObject(event.target.value)}
                >
                  <option value="all">All objects</option>
                  {objectOptions.map((name) => (
                    <option key={name} value={name}>
                      {name}
                    </option>
                  ))}
                </select>
              </label>

              <label className="control">
                <span>Time Window</span>
                <select
                  value={timeWindow}
                  onChange={(event) => setTimeWindow(event.target.value)}
                >
                  <option value="all">All time</option>
                  <option value="5">Last 5 minutes</option>
                  <option value="15">Last 15 minutes</option>
                  <option value="60">Last 1 hour</option>
                </select>
              </label>
            </div>

            <ul className="event-list alert-feed">
              {alerts.length === 0 && !loading && (
                <li className="empty">No alert events yet. The stream is quiet.</li>
              )}
              {alerts.slice(0, 8).map((alert) => (
                <li key={`alert-${alert.id}`} className="event-item">
                  <div>
                    <p className="event-title">
                      {normalizeObjects(alert.objects ?? alert.object)}
                    </p>
                    <p className="event-time">{formatTime(alert.timestamp)}</p>
                  </div>
                  <span className="confidence">
                    {typeof alert.confidence === 'number'
                      ? `${Math.round(alert.confidence * 100)}%`
                      : '-'}
                  </span>
                </li>
              ))}
            </ul>
          </article>
        </section>
      </main>
    </div>
  );
}

export default App;
