export function Hero() {
  return (
    <section
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "1.2rem",
        padding: "2.5rem",
        borderRadius: "32px",
        background:
          "linear-gradient(135deg, rgba(99,102,241,0.12), rgba(14,165,233,0.12)), radial-gradient(circle at top right, rgba(14,165,233,0.25), transparent 45%)",
        border: "1px solid rgba(99,102,241,0.15)"
      }}
    >
      <div className="badge">Ferrum Commerce</div>
      <h1 style={{ fontSize: "3rem", margin: 0 }}>
        Конструктор сайтов и интернет‑магазинов уровня enterprise
      </h1>
      <p className="muted" style={{ fontSize: "1.1rem", maxWidth: "60ch" }}>
        Соберите витрину, контент, каталог и платежи за считанные минуты. Микросервисы и фронтенды
        подключаются к единому API, а события транслируются через Redis Streams для real-time
        аналитики.
      </p>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "1rem" }}>
        <a
          href="#catalog"
          style={{
            background: "linear-gradient(120deg, #6366f1, #8b5cf6)",
            color: "white",
            padding: "0.9rem 1.6rem",
            borderRadius: "999px",
            fontWeight: 600
          }}
        >
          Смотреть каталог
        </a>
        <a
          href="#news"
          style={{
            borderRadius: "999px",
            padding: "0.9rem 1.6rem",
            border: "1px solid rgba(99,102,241,0.4)",
            color: "#4f46e5"
          }}
        >
          Лента обновлений
        </a>
      </div>
    </section>
  );
}


