import { Header } from "../../components/layout/Header";
import { BRAND } from "../../lib/brand";
import { RepositoryForm } from "./RepositoryForm";

const STEPS: [string, string, string][] = [
  ["01", "Clone", "A shallow git clone. Public repositories only."],
  ["02", "Parse", "Python: imports, functions, calls, routes. JavaScript and TypeScript: imports and routes."],
  ["03", "Rank", "PageRank over the import graph decides which files matter most."],
  ["04", "Classify", "Each file gets a role (model, data, training, config…) from a classifier you train. Keyword rules until you do."],
  ["05", "Cluster", "Files are grouped by their code and their imports. The number of groups is picked by silhouette score."],
  ["06", "Explain", "A language model reads the README and a few top files, only when you press the button."],
];

/*
 * HERO SLOT
 * Originkit "Hero 54" was not available when this was written (its registry could not be reached).
 * To use it: run  npx originkit@latest add hero-54  inside frontend/, then replace the
 * <section className="hero"> block below with the generated component and keep <RepositoryForm />
 * inside it.
 */
export default function Landing() {
  return (
    <div className="landing">
      <Header minimal />
      <main className="landing__grid">
        <section className="hero">
          <p className="eyebrow mono">{BRAND} / repository reader</p>
          <h1>
            See how a codebase <em>fits together</em> before you read it.
          </h1>
          <p className="lede">
            Paste a GitHub repository. You get a map of what imports what, the files worth opening first, and
            plain-language notes on each one.
          </p>
          <RepositoryForm />
          <p className="fine">
            Python is analysed in depth. JavaScript and TypeScript get imports and routes, not call graphs. File
            explanations come from a language model and can be wrong, so check them against the code.
          </p>
        </section>

        <aside className="steps" aria-label="What happens when you press Analyse">
          <h2 className="eyebrow mono">What happens next</h2>
          <ol>
            {STEPS.map(([n, name, text]) => (
              <li key={n}>
                <span className="mono">{n}</span>
                <div>
                  <h3>{name}</h3>
                  <p>{text}</p>
                </div>
              </li>
            ))}
          </ol>
        </aside>
      </main>
      <p className="landing__hint mono">↳ click anywhere</p>
    </div>
  );
}