import type { Category } from "../lib/types";

type Props = {
  categories: Category[];
};

function CategoryNode({ node }: { node: Category }) {
  return (
    <li style={{ marginBottom: "0.6rem" }}>
      <strong>{node.name}</strong>
      {node.children && node.children.length > 0 ? (
        <ul style={{ marginTop: "0.3rem", marginLeft: "1rem", paddingLeft: "0.5rem" }}>
          {node.children.map((child) => (
            <CategoryNode key={child.id} node={child} />
          ))}
        </ul>
      ) : null}
    </li>
  );
}

export function CategoriesList({ categories }: Props) {
  return (
    <div className="card">
      <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
        {categories.map((category) => (
          <CategoryNode key={category.id} node={category} />
        ))}
      </ul>
    </div>
  );
}


