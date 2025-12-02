export interface CategoryNode {
  id: number;
  name: string;
  slug: string;
  description: string;
  parent: number | null;
  is_active: boolean;
  position: number;
  icon: string;
  meta: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  children?: CategoryNode[];
}

const API_BASE_URL = import.meta.env.VITE_CATALOG_API_URL ?? "http://localhost:8104/api/v1";
const AUTH_BASE_URL = import.meta.env.VITE_AUTH_API_URL
  ? `${import.meta.env.VITE_AUTH_API_URL}/auth`
  : "http://localhost:8101/api/v1/auth";

async function requestJson<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    ...init
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Не удалось выполнить запрос");
  }

  return response.json();
}

export async function requestOtp(email: string) {
  return requestJson<{ detail: string }>(`${AUTH_BASE_URL}/login/`, {
    method: "POST",
    body: JSON.stringify({ email })
  });
}

export async function confirmOtp(email: string, code: string) {
  return requestJson<{ access: string; refresh?: string }>(`${AUTH_BASE_URL}/confirm/`, {
    method: "POST",
    body: JSON.stringify({ email, code })
  });
}

function normalizeNode(node: CategoryNode): CategoryNode {
  return {
    ...node,
    children: node.children?.map(normalizeNode) ?? []
  };
}

function normalizeTree(nodes: CategoryNode[]): CategoryNode[] {
  return nodes?.map(normalizeNode) ?? [];
}

export async function fetchCategories(token: string) {
  const data = await requestJson<CategoryNode[]>(`${API_BASE_URL}/categories/?tree=true`, {
    headers: token
      ? {
          Authorization: `Bearer ${token}`
        }
      : undefined
  });
  return normalizeTree(data);
}

export interface CategoryPayload {
  id?: number;
  name: string;
  slug: string;
  description?: string;
  parent?: number | null;
  position?: number;
  is_active?: boolean;
}

export async function createCategory(token: string, payload: CategoryPayload) {
  const node = await requestJson<CategoryNode>(`${API_BASE_URL}/categories/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(payload)
  });
  return normalizeNode(node);
}

export async function updateCategory(token: string, id: number, payload: Partial<CategoryPayload>) {
  const node = await requestJson<CategoryNode>(`${API_BASE_URL}/categories/${id}/`, {
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(payload)
  });
  return normalizeNode(node);
}

export async function deleteCategory(token: string, id: number) {
  await requestJson<void>(`${API_BASE_URL}/categories/${id}/`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  return id;
}

