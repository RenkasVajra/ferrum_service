import type { Product } from "../lib/types";

type Props = {
  product: Product;
};

export function ProductCard({ product }: Props) {
  return (
    <article className="card" style={{ display: "flex", flexDirection: "column", gap: "0.8rem" }}>
      <div>
        <p className="pill">{product.brand?.name ?? "Ferrum"}</p>
        <h3 style={{ margin: "0.4rem 0 0.2rem" }}>{product.name}</h3>
        <p className="muted" style={{ minHeight: "3rem" }}>
          {product.description?.slice(0, 120) ?? "Новый товар в каталоге Ferrum."}
        </p>
      </div>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginTop: "auto"
        }}
      >
        <strong style={{ fontSize: "1.3rem" }}>
          {Number(product.price).toLocaleString("ru-RU")} {product.currency}
        </strong>
        <button
          type="button"
          style={{
            border: "none",
            background: "linear-gradient(120deg, #6366f1, #8b5cf6)",
            color: "white",
            padding: "0.6rem 1.2rem",
            borderRadius: "999px",
            cursor: "pointer",
            fontWeight: 600
          }}
        >
          Добавить
        </button>
      </div>
    </article>
  );
}


