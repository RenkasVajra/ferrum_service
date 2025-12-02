export type Category = {
  id: number;
  name: string;
  slug: string;
  description?: string;
  parent?: number | null;
  children?: Category[] | null;
};

export type Product = {
  id: number;
  name: string;
  slug: string;
  description?: string;
  price: string;
  currency: string;
  is_published: boolean;
  brand?: { name: string };
};

export type NewsArticle = {
  id: number;
  title: string;
  slug: string;
  summary: string;
  published_at?: string;
  tags?: string[];
};

export type LandingData = {
  categories: Category[];
  products: Product[];
  news: NewsArticle[];
};


