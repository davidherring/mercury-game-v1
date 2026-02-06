import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { Session, User } from "@supabase/supabase-js";
import { getSupabaseClient } from "../api/supabaseClient";

type AuthContextValue = {
  session: Session | null;
  user: User | null;
  isLoadingAuth: boolean;
  authEvent: string | null;
  signInWithPassword: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [session, setSession] = useState<Session | null>(null);
  const [isLoadingAuth, setIsLoadingAuth] = useState(true);
  const [authEvent, setAuthEvent] = useState<string | null>(null);

  useEffect(() => {
    const supabase = getSupabaseClient();
    if (!supabase) {
      console.error("Supabase client not initialized.");
      setIsLoadingAuth(false);
      return;
    }

    let isActive = true;
    const bootstrapAuth = async () => {
      let nextSession: Session | null = null;
      try {
        if (typeof window !== "undefined") {
          const url = new URL(window.location.href);
          const code = url.searchParams.get("code");
          if (code) {
            const { error } = await supabase.auth.exchangeCodeForSession(window.location.href);
            if (error) {
              console.error("Supabase code exchange error:", error.message);
            }
            url.searchParams.delete("code");
            url.searchParams.delete("type");
            window.history.replaceState({}, document.title, url.pathname + url.search + url.hash);
          }
        }

        const { data, error } = await supabase.auth.getSession();
        if (!isActive) return;
        if (error) {
          console.error("Supabase session error:", error.message);
          setSession(null);
        } else {
          nextSession = data.session;
          setSession(data.session);
        }
      } finally {
        if (!isActive) return;
        setIsLoadingAuth(false);
        if (import.meta.env.DEV) {
          const hasSession = Boolean(nextSession);
          const hasInviteParams = typeof window !== "undefined" ? hasInviteParamsInUrl() : false;
          console.log("[auth]", { hasSession, hasInviteParams, authEvent });
        }
      }
    };

    void bootstrapAuth();

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((event, nextSession) => {
      if (isActive) {
        setAuthEvent(event);
        setSession(nextSession);
      }
    });

    return () => {
      isActive = false;
      subscription.unsubscribe();
    };
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      session,
      user: session?.user ?? null,
      isLoadingAuth,
      authEvent,
      signInWithPassword: async (email: string, password: string) => {
        const supabase = getSupabaseClient();
        if (!supabase) {
          throw new Error("Supabase client not initialized.");
        }
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) {
          throw error;
        }
      },
      signOut: async () => {
        const supabase = getSupabaseClient();
        if (!supabase) {
          throw new Error("Supabase client not initialized.");
        }
        const { error } = await supabase.auth.signOut();
        if (error) {
          throw error;
        }
      },
    }),
    [session, isLoadingAuth, authEvent]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider.");
  }
  return context;
}

function hasInviteParamsInUrl(): boolean {
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

  return Boolean(hasTokens && (type === "invite" || type === "recovery"));
}
