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
    <main>
      <h1>Role Selection</h1>

      <section>
        <h2>Countries</h2>
        {countryList.map((roleId) => (
          <label key={roleId}>
            <input
              type="radio"
              name="role"
              value={roleId}
              checked={selectedRoleId === roleId}
              onChange={() => setSelectedRoleId(roleId)}
            />
            {roleId}
          </label>
        ))}
      </section>

      <section>
        <h2>NGOs</h2>
        {ngoList.map((roleId) => (
          <label key={roleId}>
            <input
              type="radio"
              name="role"
              value={roleId}
              checked={selectedRoleId === roleId}
              onChange={() => setSelectedRoleId(roleId)}
            />
            {roleId}
          </label>
        ))}
      </section>

      <section>
        <h2>Chair (not selectable)</h2>
        <label>
          <input type="radio" name="role" value={CHAIR} disabled />
          {CHAIR}
        </label>
      </section>

      <section>
        <button
          type="button"
          onClick={() => void handleStartNewGame()}
          disabled={!selectedRoleId || selectedRoleId === CHAIR || isCreating}
        >
          {isCreating ? "Starting..." : "Start New Game"}
        </button>
        {createError && <div style={{ fontSize: 12, color: "#b00", marginTop: 4 }}>{createError}</div>}
      </section>

      <section style={{ marginTop: 16 }}>
        <div style={{ fontWeight: 600 }}>Join existing game (dev/test)</div>
        <label>
          Existing game ID (UUID)
          <input
            type="text"
            value={gameId}
            onChange={(e) => setGameId(e.target.value)}
            placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
          />
        </label>
        {!isGameIdValid && gameIdTrimmed && (
          <div style={{ fontSize: 12, color: "#b00", marginTop: 4 }}>
            Game ID must be a UUID (example: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
          </div>
        )}
        <button
          type="button"
          onClick={handleJoinExisting}
          disabled={!selectedRoleId || selectedRoleId === CHAIR || !isGameIdValid}
          style={{ marginTop: 8 }}
        >
          Join Existing Game
        </button>
      </section>
    </main>
  );
};

function isUuid(value: string): boolean {
  const uuidPattern =
    /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/;
  return uuidPattern.test(value);
}
