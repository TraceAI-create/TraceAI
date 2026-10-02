import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <section className="border border-line bg-panel px-6 py-8">
      <p className="font-mono text-xs text-accent">404 / NOT_FOUND</p>
      <h1 className="mt-3 text-xl font-semibold text-slate-100">Page not found</h1>
      <p className="mt-2 text-sm text-muted">This route is not part of the TraceAI workspace.</p>
      <Link to="/dashboard" className="mt-5 inline-block text-sm text-blue-300 hover:text-blue-200">Return to dashboard</Link>
    </section>
  );
}
