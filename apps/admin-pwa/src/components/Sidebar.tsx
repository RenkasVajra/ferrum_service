import { NavLink, useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";

import { logout } from "../store/authSlice";
import type { RootState } from "../store";

export function Sidebar() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const email = useSelector((state: RootState) => state.auth.email);

  const handleLogout = () => {
    dispatch(logout());
    navigate("/login");
  };

  return (
    <aside className="sidebar">
      <div>
        <strong>Ferrum Admin</strong>
        <p style={{ color: "rgba(255,255,255,0.65)", marginTop: "0.25rem" }}>Конструктор e-commerce</p>
      </div>

      <nav>
        <NavLink to="/" end className={({ isActive }) => (isActive ? "active-links" : undefined)}>
          Дэшборд
        </NavLink>
        <NavLink
          to="/catalog/categories"
          className={({ isActive }) => (isActive ? "active-links" : undefined)}
        >
          Категории
        </NavLink>
        <NavLink to="/content/news" className={({ isActive }) => (isActive ? "active-links" : undefined)}>
          Новости
        </NavLink>
        <NavLink
          to="/catalog/products"
          className={({ isActive }) => (isActive ? "active-links" : undefined)}
        >
          Товары
        </NavLink>
      </nav>

      <div style={{ marginTop: "auto" }}>
        <small style={{ display: "block", marginBottom: "0.5rem", color: "rgba(255,255,255,0.6)" }}>
          {email}
        </small>
        <button className="btn secondary" onClick={handleLogout}>
          Выйти
        </button>
      </div>
    </aside>
  );
}

