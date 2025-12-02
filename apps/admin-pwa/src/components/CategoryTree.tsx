import { Fragment } from "react";

import type { CategoryNode } from "../lib/api";

interface Props {
  data: CategoryNode[];
  onSelect: (node: CategoryNode) => void;
  onDelete: (node: CategoryNode) => void;
}

export function CategoryTree({ data, onSelect, onDelete }: Props) {
  if (!data.length) {
    return <p className="empty-state">Категорий пока нет</p>;
  }

  return (
    <div>
      {data.map((node) => (
        <Fragment key={node.id}>
          <TreeRow node={node} depth={0} onSelect={onSelect} onDelete={onDelete} />
          {node.children?.length ? (
            <div style={{ marginLeft: "1.25rem" }}>
              <CategoryTree data={node.children} onSelect={onSelect} onDelete={onDelete} />
            </div>
          ) : null}
        </Fragment>
      ))}
    </div>
  );
}

function TreeRow({
  node,
  depth,
  onSelect,
  onDelete
}: {
  node: CategoryNode;
  depth: number;
  onSelect: (node: CategoryNode) => void;
  onDelete: (node: CategoryNode) => void;
}) {
  return (
    <div className="category-row" style={{ paddingLeft: depth * 12 }}>
      <span style={{ fontWeight: 600 }}>{node.name}</span>
      <code style={{ background: "#eef2ff", padding: "0.1rem 0.4rem", borderRadius: 6 }}>{node.slug}</code>
      <div style={{ marginLeft: "auto", display: "flex", gap: "0.5rem" }}>
        <button onClick={() => onSelect(node)}>Редактировать</button>
        <button onClick={() => onDelete(node)} style={{ color: "#ef4444" }}>
          Удалить
        </button>
      </div>
    </div>
  );
}

