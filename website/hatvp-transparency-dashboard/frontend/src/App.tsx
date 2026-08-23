import { Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { I18nProvider } from "./context/I18nContext";
import { AboutPage } from "./pages/AboutPage";
import { AgeAnalysisPage } from "./pages/AgeAnalysisPage";
import { DashboardPage } from "./pages/DashboardPage";
import { DeclarationPage } from "./pages/DeclarationPage";
import { ExplorePage } from "./pages/ExplorePage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { QualityIssuesPage } from "./pages/QualityIssuesPage";
import { PipelineHealthPage } from "./pages/PipelineHealthPage";
import { SearchPage } from "./pages/SearchPage";
import { SimpleAnalysisPage } from "./pages/SimpleAnalysisPage";

export function App() {
  return (
    <I18nProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/declarations/:uuid" element={<DeclarationPage />} />
          <Route path="/explore" element={<ExplorePage />} />
          <Route path="/analysis" element={<SimpleAnalysisPage />} />
          <Route path="/age-analysis" element={<AgeAnalysisPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/quality-issues" element={<QualityIssuesPage />} />
          <Route path="/pipeline-health" element={<PipelineHealthPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Layout>
    </I18nProvider>
  );
}
