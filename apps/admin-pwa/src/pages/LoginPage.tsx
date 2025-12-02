import { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Navigate } from "react-router-dom";

import { confirmLoginCode, requestLoginCode } from "../store/authSlice";
import type { AppDispatch, RootState } from "../store";

export function LoginPage() {
  const dispatch: AppDispatch = useDispatch();
  const auth = useSelector((state: RootState) => state.auth);
  const [code, setCode] = useState("");
  const [email, setEmail] = useState("");

  if (auth.accessToken) {
    return <Navigate to="/" replace />;
  }

  const handleRequest = (event: React.FormEvent) => {
    event.preventDefault();
    dispatch(requestLoginCode(email));
  };

  const handleConfirm = (event: React.FormEvent) => {
    event.preventDefault();
    dispatch(confirmLoginCode({ email, code }));
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "2rem"
      }}
    >
      <div className="card" style={{ width: "100%", maxWidth: 420 }}>
        <h2>Админ-панель Ferrum</h2>
        <p style={{ color: "#64748b" }}>Войдите по одноразовому коду</p>

        <form onSubmit={auth.otpRequested ? handleConfirm : handleRequest}>
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </label>

          {auth.otpRequested ? (
            <label>
              Код из письма
              <input value={code} onChange={(event) => setCode(event.target.value)} required />
            </label>
          ) : null}

          <button className="btn primary" type="submit" disabled={auth.loading}>
            {auth.otpRequested ? "Подтвердить" : "Получить код"}
          </button>

          {auth.error ? <p style={{ color: "#ef4444" }}>{auth.error}</p> : null}
        </form>
      </div>
    </div>
  );
}

