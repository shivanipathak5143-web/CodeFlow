import { Navigate, Outlet, Route, Routes } from "react-router-dom";
import { Header } from "../components/layout/Header";
import { Sidebar } from "../components/layout/Sidebar";
import { CallTrace } from "../features/trace/CallTrace";
import { CodeSearch } from "../features/search/CodeSearch";
import { FileExplorer } from "../features/files/FileExplorer";
import { ModuleClusters } from "../features/modules/ModuleClusters";
import { OverviewPage } from "../features/overview/OverviewPage";
import { PullRequestImpact } from "../features/diff/PullRequestImpact";
import { RepositoryGraph } from "../features/graph/RepositoryGraph";
import Landing from "../features/repository/Landing";
import { useRepo } from "./providers";

/** Everything under /repo needs an analysed repository. */
function RequireRepo() {
  const { status, data } = useRepo();
  if (status === "loading") return <p className="boot mono">Reopening the repository…</p>;
  if (status !== "ready" || !data) return <Navigate to="/" replace />;
  return <Outlet />;
}

function Shell() {
  return (
    <div className="shell">
      <Header />
      <Sidebar />
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route element={<RequireRepo />}>
        <Route element={<Shell />}>
          <Route path="/repo/overview" element={<OverviewPage />} />
          <Route path="/repo/graph" element={<RepositoryGraph />} />
          <Route path="/repo/files" element={<FileExplorer />} />
          <Route path="/repo/modules" element={<ModuleClusters />} />
          <Route path="/repo/search" element={<CodeSearch />} />
          <Route path="/repo/trace" element={<CallTrace />} />
          <Route path="/repo/pr" element={<PullRequestImpact />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}