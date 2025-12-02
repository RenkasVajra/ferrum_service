import type { Category, LandingData, NewsArticle, Product } from "./types";

const catalogApi =
  process.env.CATALOG_API_URL ??
  process.env.NEXT_PUBLIC_CATALOG_API_URL ??
  "http://localhost:8104/api/v1";
const contentApi =
  process.env.CONTENT_API_URL ??
  process.env.NEXT_PUBLIC_CONTENT_API_URL ??
  "http://localhost:8103/api/v1/public";

async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    cache: "no-store"
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const data = await response.json();
      detail = JSON.stringify(data);
    } catch {
      /* ignore */
    }
    throw new Error(`Request to ${url} failed: ${detail}`);
  }

  return response.json() as Promise<T>;
}

export async function getLandingData(): Promise<LandingData> {
  const [categories, productsPayload, newsPayload] = await Promise.all([
    fetchJson<Category[]>(`${catalogApi}/categories/?tree=true`),
    fetchJson<{ results?: Product[]; data?: Product[]; length?: number } | Product[]>(
      `${catalogApi}/goods/?is_published=true&ordering=-created_at`
    ),
    fetchJson<{ results?: NewsArticle[] } | NewsArticle[]>(`${contentApi}/news/`)
  ]);

  const normalize = <T>(payload: { results?: T[] } | { data?: T[] } | T[]): T[] => {
    if (Array.isArray(payload)) return payload;
    if ("results" in payload && payload.results) return payload.results;
    if ("data" in payload && Array.isArray(payload.data)) return payload.data;
    return [];
  };

  return {
    categories,
    products: normalize<Product>(productsPayload).slice(0, 8),
    news: normalize<NewsArticle>(newsPayload).slice(0, 4)
  };
}


