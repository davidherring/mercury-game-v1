import { DebugInfo } from "../components/DebugBox";

export interface RunRequestResult<T> {
  result?: T;
  lastRequest: DebugInfo;
  errorMessage?: string;
}

export async function runRequest<T>(opts: {
  method: string;
  url: string;
  body?: unknown;
  exec: () => Promise<T>;
}): Promise<RunRequestResult<T>> {
  const { method, url, body, exec } = opts;
  const lastRequest: DebugInfo = {
    method,
    url,
    body,
    timestamp: new Date().toISOString(),
  };
  try {
    const result = await exec();
    lastRequest.status = "ok";
    return { result, lastRequest };
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    lastRequest.status = "error";
    return { lastRequest, errorMessage: message };
  }
}
