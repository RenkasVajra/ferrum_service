import { ReactNode } from "react";

type Props = {
  overline: string;
  title: string;
  description?: string;
  action?: ReactNode;
};

export function SectionHeading({ overline, title, description, action }: Props) {
  return (
    <header style={{ marginBottom: "1.5rem" }}>
      <div className="badge">{overline}</div>
      <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "1rem" }}>
        <div>
          <h2 style={{ marginBottom: "0.25rem", fontSize: "2rem" }}>{title}</h2>
          {description ? <p className="muted">{description}</p> : null}
        </div>
        {action}
      </div>
    </header>
  );
}


