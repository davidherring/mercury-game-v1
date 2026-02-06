import { createClient, SupabaseClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL as string | undefined;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined;
const isDev = import.meta.env.DEV;

let supabaseClient: SupabaseClient | null = null;

if (supabaseUrl && supabaseAnonKey) {
  supabaseClient = createClient(supabaseUrl, supabaseAnonKey);
} else {
  const message = "Supabase env vars missing: VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY are required.";
  if (isDev) {
    throw new Error(message);
  }
  console.error(message);
}

export function getSupabaseClient(): SupabaseClient | null {
  return supabaseClient;
}
