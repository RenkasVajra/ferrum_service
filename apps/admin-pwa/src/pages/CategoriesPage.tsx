import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import { CategoryForm } from "../components/CategoryForm";
import { CategoryTree } from "../components/CategoryTree";
import type { CategoryNode, CategoryPayload } from "../lib/api";
import { addCategory, loadCategories, patchCategory, removeCategory } from "../store/categoriesSlice";
import type { AppDispatch, RootState } from "../store";

export function CategoriesPage() {
  const dispatch: AppDispatch = useDispatch();
  const { tree, loading, error } = useSelector((state: RootState) => state.categories);
  const [selected, setSelected] = useState<CategoryNode | null>(null);

  useEffect(() => {
    if (!tree.length) {
      dispatch(loadCategories());
    }
  }, [dispatch, tree.length]);

  const handleSubmit = (payload: CategoryPayload) => {
    if (payload.id) {
      dispatch(patchCategory({ id: payload.id, data: payload }));
    } else {
      dispatch(addCategory(payload));
    }
    setSelected(null);
  };

  const handleDelete = (node: CategoryNode) => {
    if (confirm(`Удалить категорию ${node.name}?`)) {
      dispatch(removeCategory(node.id));
      setSelected(null);
    }
  };

  return (
    <div className="grid two">
      <article className="card">
        <header style={{ display: "flex", alignItems: "center", marginBottom: "1rem" }}>
          <div>
            <h2 style={{ margin: 0 }}>Дерево категорий</h2>
            <p style={{ color: "#64748b" }}>Drag&drop реализуется позже, сейчас CRUD через форму справа</p>
          </div>
          <button className="btn secondary" style={{ marginLeft: "auto" }} onClick={() => dispatch(loadCategories())}>
            Обновить
          </button>
        </header>

        {loading ? <p>Загрузка...</p> : <CategoryTree data={tree} onSelect={setSelected} onDelete={handleDelete} />}
        {error ? <p style={{ color: "#ef4444" }}>{error}</p> : null}
      </article>

      <CategoryForm nodes={tree} selected={selected} onSubmit={handleSubmit} onReset={() => setSelected(null)} />
    </div>
  );
}

