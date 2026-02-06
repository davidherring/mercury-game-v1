import React, { useState } from "react";
import { useAuth } from "../contexts/AuthContext";

export const LoginPage: React.FC = () => {
  const { signInWithPassword } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!email || !password) return;
    setErrorMessage(null);
    setIsSubmitting(true);
    try {
      await signInWithPassword(email, password);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      setErrorMessage(message || "Login failed.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="page">
      <div className="container">
        <div className="card login-card">
          <h1 className="page-title login-title">Sign in</h1>
          <p className="text-muted">Invite-only access. Use your provided credentials.</p>
          <form className="action-stack" onSubmit={handleSubmit}>
            <label className="field">
              Email
              <input
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input"
              />
            </label>
            <label className="field">
              Password
              <input
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input"
              />
            </label>
            <button type="submit" className="btn btn-primary" disabled={!email || !password || isSubmitting}>
              {isSubmitting ? "Signing in..." : "Sign in"}
            </button>
            {errorMessage && <div className="text-small text-error">{errorMessage}</div>}
          </form>
        </div>
      </div>
    </main>
  );
};
