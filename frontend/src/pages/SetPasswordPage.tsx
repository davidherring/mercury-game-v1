import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { getSupabaseClient } from "../api/supabaseClient";

export const SetPasswordPage: React.FC = () => {
  const navigate = useNavigate();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!password || !confirmPassword) return;
    if (password !== confirmPassword) {
      setErrorMessage("Passwords do not match.");
      return;
    }
    setErrorMessage(null);
    setIsSubmitting(true);
    try {
      const supabase = getSupabaseClient();
      if (!supabase) {
        throw new Error("Supabase client not initialized.");
      }
      const { error } = await supabase.auth.updateUser({ password });
      if (error) {
        throw error;
      }
      if (typeof window !== "undefined") {
        window.history.replaceState({}, document.title, window.location.pathname);
      }
      navigate("/role-select", { replace: true });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      setErrorMessage(message || "Could not set password.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="page">
      <div className="container">
        <div className="card login-card">
          <h1 className="page-title login-title">Set your password</h1>
          <p className="text-muted">Finish setting up your account to continue.</p>
          <form className="action-stack" onSubmit={handleSubmit}>
            <label className="field">
              New password
              <input
                type="password"
                autoComplete="new-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input"
              />
            </label>
            <label className="field">
              Confirm password
              <input
                type="password"
                autoComplete="new-password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="input"
              />
            </label>
            <button type="submit" className="btn btn-primary" disabled={!password || !confirmPassword || isSubmitting}>
              {isSubmitting ? "Saving..." : "Set password"}
            </button>
            {errorMessage && <div className="text-small text-error">{errorMessage}</div>}
          </form>
        </div>
      </div>
    </main>
  );
};
