type FastApiValidationError = {
  loc?: Array<string | number>;
  msg?: string;
  type?: string;
};

function errorDetail(body: unknown, fallback: string): string {
  if (!body || typeof body !== "object" || !("detail" in body)) return fallback;
  const detail = (body as { detail?: unknown }).detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (!item || typeof item !== "object") return null;
        const error = item as FastApiValidationError;
        const field = error.loc?.filter((part) => part !== "body").join(".");
        return [field, error.msg].filter(Boolean).join(": ");
      })
      .filter((message): message is string => Boolean(message));
    return messages.length ? messages.join("; ") : fallback;
  }
  return fallback;
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !headers.has("content-type")) {
    headers.set("content-type", "application/json");
  }

  const response = await fetch(path, {
    ...init,
    headers,
    credentials: "include",
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      detail = errorDetail(await response.json(), detail);
    } catch {
      // Keep HTTP status text when the response has no JSON body.
    }
    throw new Error(detail);
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}
