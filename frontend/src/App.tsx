import React from "react";
import { Navigate, Route, Routes, useParams } from "react-router-dom";
import { useConfirmedRole } from "./contexts/RoleContext";
import { GameViewPage } from "./pages/GameViewPage";
import { RoleSelectPage } from "./pages/RoleSelectPage";

export const App: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/role-select" replace />} />
      <Route path="/role-select" element={<RoleSelectPage />} />
      <Route path="/game/:gameId" element={<GameRoute />} />
    </Routes>
  );
};

const GameRoute: React.FC = () => {
  const { gameId } = useParams<{ gameId: string }>();
  const { confirmedRoleId } = useConfirmedRole();

  if (!gameId || !confirmedRoleId) {
    return <Navigate to="/role-select" replace />;
  }

  return <GameViewPage gameId={gameId} confirmedRoleId={confirmedRoleId} />;
};
