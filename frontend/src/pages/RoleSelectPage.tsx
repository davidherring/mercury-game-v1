import React, { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { createApiClient } from "../api/client";
import { useConfirmedRole } from "../contexts/RoleContext";
import { CHAIR, COUNTRIES, NGOS, RoleId } from "../config/roles";
import { useApiBaseUrl } from "../hooks/useApiBaseUrl";

export const RoleSelectPage: React.FC = () => {
  const navigate = useNavigate();
  const { confirmedRoleId, setConfirmedRoleId } = useConfirmedRole();
  const { baseUrl } = useApiBaseUrl();
  const api = useMemo(() => createApiClient({ baseUrl }), [baseUrl]);
  const [selectedRoleId, setSelectedRoleId] = useState<RoleId | null>(
    confirmedRoleId as RoleId | null
  );
  const [gameId, setGameId] = useState("");
  const [createError, setCreateError] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const gameIdTrimmed = gameId.trim();
  const isGameIdValid = isUuid(gameIdTrimmed);

  const countryList = useMemo(() => [...COUNTRIES], []);
  const ngoList = useMemo(() => [...NGOS], []);

  const handleStartNewGame = async () => {
    if (!selectedRoleId || selectedRoleId === CHAIR) return;
    setCreateError(null);
    setIsCreating(true);
    try {
      const result = await api.createGame();
      const newGameId = (result as any)?.game_id || (result as any)?.gameId || (result as any)?.gameID;
      if (typeof newGameId !== "string") {
        setCreateError("Could not create game");
        return;
      }
      setConfirmedRoleId(selectedRoleId);
      navigate(`/game/${newGameId}`);
    } catch {
      setCreateError("Could not create game");
    } finally {
      setIsCreating(false);
    }
  };

  const handleJoinExisting = () => {
    if (!selectedRoleId || selectedRoleId === CHAIR) return;
    if (!isGameIdValid) return;
    setConfirmedRoleId(selectedRoleId);
    navigate(`/game/${gameIdTrimmed}`);
  };

  return (
    <main className="page">
      <div className="container">
        <h1 className="page-title">Role Selection</h1>

        <section className="section card">
          <div className="section-header">
            <h2 className="section-title">Countries</h2>
            <span className="badge">Vote required</span>
          </div>
          <div className="choice-grid">
            {countryList.map((roleId) => (
              <label key={roleId} className="choice">
                <input
                  type="radio"
                  name="role"
                  value={roleId}
                  checked={selectedRoleId === roleId}
                  onChange={() => setSelectedRoleId(roleId)}
                />
                <span>{roleId}</span>
              </label>
            ))}
          </div>
        </section>

        <section className="section card">
          <div className="section-header">
            <h2 className="section-title">NGOs</h2>
            <span className="badge">Observer</span>
          </div>
          <div className="choice-grid">
            {ngoList.map((roleId) => (
              <label key={roleId} className="choice">
                <input
                  type="radio"
                  name="role"
                  value={roleId}
                  checked={selectedRoleId === roleId}
                  onChange={() => setSelectedRoleId(roleId)}
                />
                <span>{roleId}</span>
              </label>
            ))}
          </div>
        </section>

        <section className="section card">
          <div className="section-header">
            <h2 className="section-title">Chair (not selectable)</h2>
          </div>
          <label className="choice">
            <input type="radio" name="role" value={CHAIR} disabled />
            <span>{CHAIR}</span>
          </label>
        </section>

        <section className="section card">
          <div className="action-row">
            <button
              type="button"
              onClick={() => void handleStartNewGame()}
              disabled={!selectedRoleId || selectedRoleId === CHAIR || isCreating}
              className="btn btn-primary"
              data-loading={isCreating}
            >
              {isCreating ? "Starting..." : "Start New Game"}
            </button>
            {createError && <div className="text-small text-error">{createError}</div>}
          </div>
        </section>

        <section className="section card">
          <div className="section-header">
            <h2 className="section-title">Join existing game (dev/test)</h2>
          </div>
          <label className="field">
            Existing game ID (UUID)
            <input
              type="text"
              value={gameId}
              onChange={(e) => setGameId(e.target.value)}
              placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
              className="input"
            />
          </label>
          {!isGameIdValid && gameIdTrimmed && (
            <div className="text-small text-error">
              Game ID must be a UUID (example: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
            </div>
          )}
          <div className="action-row stack-sm">
            <button
              type="button"
              onClick={handleJoinExisting}
              disabled={!selectedRoleId || selectedRoleId === CHAIR || !isGameIdValid}
              className="btn btn-secondary"
            >
              Join Existing Game
            </button>
          </div>
        </section>
      </div>
    </main>
  );
};

function isUuid(value: string): boolean {
  const uuidPattern =
    /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/;
  return uuidPattern.test(value);
}
