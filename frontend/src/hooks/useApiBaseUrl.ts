import { useEffect, useMemo, useState } from "react";

const STORAGE_KEY = "mercury_api_base";
const envDefault = import.meta.env.VITE_API_BASE_URL || "/api";

export function useApiBaseUrl() {
  const [override, setOverride] = useState<string | null>(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ?? null;
  });

  useEffect(() => {
    if (override) {
      localStorage.setItem(STORAGE_KEY, override);
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  }, [override]);

  const baseUrl = useMemo(() => override || envDefault, [override]);

  return { baseUrl, override, setOverride };
}
