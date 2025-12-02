import { Navigate, Route, Routes } from "react-router-dom";
import { useSelector } from "react-redux";

import { Layout } from "./components/Layout";
import { CategoriesPage } from "./pages/CategoriesPage";
import { DashboardPage } from "./pages/DashboardPage";
import { LoginPage } from "./pages/LoginPage";
import type { RootState } from "./store";

function PrivateRoute({ children }: { children: JSX.Element }) {
  const token = useSelector((state: RootState) => state.auth.accessToken);
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="catalog/categories" element={<CategoriesPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

