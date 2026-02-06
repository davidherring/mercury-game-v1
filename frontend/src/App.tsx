import React from "react";
import { Navigate, Route, Routes, useParams } from "react-router-dom";
import { useAuth } from "./contexts/AuthContext";
import { useConfirmedRole } from "./contexts/RoleContext";
import { LoginPage } from "./pages/LoginPage";
import { SetPasswordPage } from "./pages/SetPasswordPage";
import { GameViewPage } from "./pages/GameViewPage";
import { RoleSelectPage } from "./pages/RoleSelectPage";

export const App: React.FC = () => {
  const { user, isLoadingAuth, authEvent } = useAuth();
  const needsPasswordSetup = user && (authEvent === "PASSWORD_RECOVERY" || hasInviteParams());

  if (isLoadingAuth) {
    return (
      <main className="page">
        <div className="container">Loading session...</div>
      </main>
    );
  }

  if (!user) {
    return <LoginPage />;
  }

  if (needsPasswordSetup) {
    return <SetPasswordPage />;
  }

  return (
    <Routes>
      <Route path="/" element={<Navigate to="/role-select" replace />} />
      <Route path="/role-select" element={<RoleSelectPage />} />
      <Route path="/game/:gameId" element={<GameRoute />} />
    </Routes>
  );
};

function hasInviteParams(): boolean {
  if (typeof window === "undefined") return false;
  const hashParams = new URLSearchParams(window.location.hash.replace(/^#/, ""));
  const searchParams = new URLSearchParams(window.location.search);
  const type = hashParams.get("type") || searchParams.get("type");
  const hasTokens =
    hashParams.has("access_token") ||
    hashParams.has("refresh_token") ||
    hashParams.has("code") ||
    searchParams.has("access_token") ||
    searchParams.has("refresh_token") ||
    searchParams.has("code");

  return Boolean(hasTokens && (type === "invite" || type === "recovery" || searchParams.has("code")));
}

const GameRoute: React.FC = () => {
  const { gameId } = useParams<{ gameId: string }>();
  const { confirmedRoleId } = useConfirmedRole();

  if (!gameId || !confirmedRoleId) {
    return <Navigate to="/role-select" replace />;
  }

  return <GameViewPage gameId={gameId} confirmedRoleId={confirmedRoleId} />;
};
