import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";

import type { CategoryNode } from "../lib/api";
import { loadCategories } from "../store/categoriesSlice";
import type { AppDispatch, RootState } from "../store";

export function DashboardPage() {
  const dispatch: AppDispatch = useDispatch();
  const categories = useSelector((state: RootState) => state.categories.tree);

  useEffect(() => {
    if (!categories.length) {
      dispatch(loadCategories());
    }
  }, [categories.length, dispatch]);

  return (
    <div className="grid two">
      <article className="card">
        <h3>Каталог</h3>
        <p>Корневых категорий: {categories.length}</p>
        <p>Всего узлов: {countNodes(categories)}</p>
      </article>
      <article className="card">
        <h3>Новости</h3>
        <p>Публикации управляются через Content Service (/api/v1/news).</p>
      </article>
      <article className="card">
        <h3>Платежи</h3>
        <p>Методы оплаты и доставки доступны в Catalog API.</p>
      </article>
    </div>
  );
}

function countNodes(nodes: CategoryNode[]): number {
  return nodes.reduce(
    (acc, node) => acc + 1 + (node.children && node.children.length ? countNodes(node.children) : 0),
    0
  );
}

