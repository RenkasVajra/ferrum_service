import type { NewsArticle } from "../lib/types";

type Props = {
  news: NewsArticle[];
};

export function NewsList({ news }: Props) {
  return (
    <div className="grid grid-2">
      {news.map((article) => (
        <article key={article.id} className="card">
          <div className="badge">новости</div>
          <h3 style={{ marginTop: "0.8rem" }}>{article.title}</h3>
          <p className="muted">{article.summary}</p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", marginTop: "0.8rem" }}>
            {(article.tags ?? []).slice(0, 3).map((tag) => (
              <span key={tag} className="pill">
                {tag}
              </span>
            ))}
          </div>
        </article>
      ))}
    </div>
  );
}


