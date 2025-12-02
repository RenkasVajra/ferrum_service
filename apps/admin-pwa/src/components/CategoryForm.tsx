import { useEffect, useMemo, useState } from "react";

import type { CategoryNode, CategoryPayload } from "../lib/api";

interface Props {
  nodes: CategoryNode[];
  selected: CategoryNode | null;
  onSubmit: (payload: CategoryPayload) => void;
  onReset: () => void;
}

const emptyCategory: CategoryPayload = {
  name: "",
  slug: "",
  description: "",
  parent: null,
  position: 0,
  is_active: true
};

export function CategoryForm({ nodes, selected, onSubmit, onReset }: Props) {
  const [form, setForm] = useState<CategoryPayload>(emptyCategory);

  useEffect(() => {
    if (selected) {
      setForm({
        id: selected.id,
        name: selected.name,
        slug: selected.slug,
        description: selected.description,
        parent: selected.parent ?? null,
        position: selected.position,
        is_active: selected.is_active
      });
    } else {
      setForm(emptyCategory);
    }
  }, [selected]);

  const options = useMemo(() => flatten(nodes), [nodes]);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = event.target;
    setForm((prev) => ({
      ...prev,
      [name]:
        name === "position"
          ? Number(value)
          : name === "parent"
            ? value === "" ? null : Number(value)
            : name === "is_active"
              ? value === "true"
              : value
    }));
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    onSubmit(form);
  };

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h3>{selected ? "Редактирование" : "Новая категория"}</h3>

      <label>
        Название
        <input name="name" value={form.name} onChange={handleChange} required />
      </label>

      <label>
        Slug
        <input name="slug" value={form.slug} onChange={handleChange} required />
      </label>

      <label>
        Описание
        <textarea name="description" value={form.description} onChange={handleChange} rows={3} />
      </label>

      <label>
        Родитель
        <select name="parent" value={form.parent ?? ""} onChange={handleChange}>
          <option value="">Корень</option>
          {options.map((option) => (
            <option key={option.id} value={option.id}>
              {option.label}
            </option>
          ))}
        </select>
      </label>

      <label>
        Позиция
        <input type="number" name="position" value={form.position} onChange={handleChange} min={0} />
      </label>

      <label>
        Статус
        <select name="is_active" value={String(form.is_active)} onChange={handleChange}>
          <option value="true">Активна</option>
          <option value="false">Выключена</option>
        </select>
      </label>

      <div style={{ display: "flex", gap: "0.5rem" }}>
        <button className="btn primary" type="submit">
          {selected ? "Сохранить" : "Создать"}
        </button>
        {selected ? (
          <button
            type="button"
            className="btn secondary"
            onClick={() => {
              onReset();
              setForm(emptyCategory);
            }}
          >
            Сбросить
          </button>
        ) : null}
      </div>
    </form>
  );
}

function flatten(nodes: CategoryNode[], depth = 0): Array<{ id: number; label: string }> {
  return nodes.flatMap((node) => [
    { id: node.id, label: `${"— ".repeat(depth)}${node.name}` },
    ...(node.children ? flatten(node.children, depth + 1) : [])
  ]);
}

